"""Bounded transport optimizations for public JSON reads, never execution streams or files."""

import gzip
import hashlib
import logging
import re
import time
from contextvars import ContextVar
from uuid import uuid4

logger = logging.getLogger(__name__)
CONDITIONAL = re.compile(r"^/api/v1/conversations(?:/[a-f0-9]{32})?$")
MAX_BUFFER = 1024 * 1024
READ_SPANS = ContextVar("read_spans", default=None)


def record_read(name, elapsed):
    spans = READ_SPANS.get()
    if spans is not None:
        spans[name] = spans.get(name, 0) + elapsed * 1000


def accepts_gzip(value):
    for part in value.lower().split(","):
        fields = [v.strip() for v in part.split(";")]
        if fields[0] == "gzip" and not any(re.fullmatch(r"q=0(?:\.0*)?", v) for v in fields[1:]):
            return True
    return False


class ReadPerformanceMiddleware:
    def __init__(self, app, allowed_origins=()):
        self.app = app
        self.allowed_origins = frozenset(allowed_origins)

    async def __call__(self, scope, receive, send):
        path = scope.get("path", "")
        if scope["type"] != "http" or scope.get("method") != "GET" or not path.startswith("/api/v1/"):
            return await self.app(scope, receive, send)
        spans = {}
        token = READ_SPANS.set(spans)
        start = time.perf_counter()
        request = dict(scope.get("headers", []))
        response_start, chunks, size, buffering = None, [], 0, False

        async def send_read(message):
            nonlocal response_start, chunks, size, buffering
            if message["type"] == "http.response.start":
                headers = dict(message["headers"])
                buffering = (
                    message["status"] == 200
                    and headers.get(b"content-type", b"").startswith(b"application/json")
                    and b"content-disposition" not in headers
                    and b"content-encoding" not in headers
                )
                if not buffering:
                    await send(message)
                else:
                    response_start = message
                return
            if message["type"] != "http.response.body" or not buffering:
                return await send(message)
            chunks.append(message.get("body", b""))
            size += len(chunks[-1])
            if size > MAX_BUFFER:
                # Do not buffer large/streamed JSON or affect its original byte contract.
                buffering = False
                await send(response_start)
                for index, chunk in enumerate(chunks):
                    await send(
                        {
                            "type": "http.response.body",
                            "body": chunk,
                            "more_body": index < len(chunks) - 1 or message.get("more_body", False),
                        }
                    )
                chunks = []
                return
            if message.get("more_body", False):
                return
            body = b"".join(chunks)
            headers = dict(response_start["headers"])
            elapsed = (time.perf_counter() - start) * 1000
            read_id = uuid4().hex[:16]
            headers[b"x-querylane-read-id"] = read_id.encode()
            headers[b"server-timing"] = (
                f"app;dur={elapsed:.2f}"
                + f', read;desc="{read_id}"'
                + "".join(f", {name};dur={duration:.2f}" for name, duration in sorted(spans.items()))
            ).encode()
            origin = request.get(b"origin", b"").decode(errors="replace")
            if origin in self.allowed_origins:
                headers[b"timing-allow-origin"] = origin.encode()
            status = response_start["status"]
            if CONDITIONAL.fullmatch(path):
                etag = b'W/"' + hashlib.sha256(body).hexdigest().encode() + b'"'
                headers[b"etag"] = etag
                offered = request.get(b"if-none-match", b"").split(b",")
                if any(value.strip() in (etag, etag.removeprefix(b"W/"), b"*") for value in offered):
                    status, body = 304, b""
            if (
                status != 304
                and len(body) >= 1024
                and accepts_gzip(request.get(b"accept-encoding", b"").decode())
            ):
                body = gzip.compress(body, compresslevel=5, mtime=0)
                headers[b"content-encoding"] = b"gzip"
            vary = [v.strip() for v in headers.get(b"vary", b"").split(b",") if v.strip()]
            if b"accept-encoding" not in [v.lower() for v in vary]:
                vary.append(b"Accept-Encoding")
            if b"timing-allow-origin" in headers and b"origin" not in [v.lower() for v in vary]:
                vary.append(b"Origin")
            headers[b"vary"] = b", ".join(vary)
            headers.pop(b"content-length", None)
            if status != 304:
                headers[b"content-length"] = str(len(body)).encode()
            logger.info(
                "public_read read_id=%s route=%s duration_ms=%.2f status=%s bytes=%s",
                read_id,
                scope.get("route", path),
                elapsed,
                status,
                len(body),
            )
            await send({**response_start, "status": status, "headers": list(headers.items())})
            await send({"type": "http.response.body", "body": body})

        try:
            await self.app(scope, receive, send_read)
        finally:
            READ_SPANS.reset(token)
