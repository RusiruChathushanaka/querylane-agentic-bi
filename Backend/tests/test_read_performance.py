import asyncio

import pytest
from fastapi.testclient import TestClient
from test_chart_presentation import artifact

from app.config import Settings
from app.connectors import Connectors
from app.main import create_app
from app.read_performance import ReadPerformanceMiddleware, accepts_gzip
from app.saved_chart_cache import SavedChartCache
from app.storage import MemoryStore


def test_browser_timing_is_origin_scoped_and_each_read_has_its_own_identity():
    with TestClient(create_app(Settings(environment="test"))) as client:
        first = client.get("/api/v1/conversations", headers={"Origin": "http://localhost:3000"})
        assert first.headers["timing-allow-origin"] == "http://localhost:3000"
        read_id = first.headers["x-querylane-read-id"]
        assert len(read_id) == 16 and f'read;desc="{read_id}"' in first.headers["server-timing"]
        unchanged = client.get(
            "/api/v1/conversations",
            headers={"Origin": "http://localhost:3000", "If-None-Match": first.headers["etag"]},
        )
        assert unchanged.status_code == 304
        assert unchanged.headers["x-querylane-read-id"] != read_id
        assert unchanged.headers["timing-allow-origin"] == "http://localhost:3000"
        assert "Origin" in unchanged.headers["vary"]
        foreign = client.get("/api/v1/conversations", headers={"Origin": "https://unapproved.invalid"})
        assert "timing-allow-origin" not in foreign.headers
        assert "timing-allow-origin" not in client.get("/api/v1/conversations").headers
        assert "X-Querylane-Read-Id" in first.headers["access-control-expose-headers"]


def test_json_compression_conditional_reads_and_changed_evidence():
    store = MemoryStore()
    with TestClient(create_app(Settings(environment="test"), store_override=store)) as client:
        rows = [{"id": f"{i:032x}", "title": "public history " * 40, "updated_at": str(i)} for i in range(30)]
        for row in rows:
            asyncio.run(store.put("conversations", row["id"], row))
        first = client.get("/api/v1/conversations", headers={"Accept-Encoding": "gzip"})
        assert first.headers["content-encoding"] == "gzip"
        assert first.json()["conversations"] and "app;dur=" in first.headers["server-timing"]
        assert first.headers["cache-control"] == "no-store"
        unchanged = client.get("/api/v1/conversations", headers={"If-None-Match": first.headers["etag"]})
        assert unchanged.status_code == 304 and unchanged.content == b""
        asyncio.run(store.put("conversations", rows[0]["id"], rows[0] | {"title": "updated"}))
        changed = client.get("/api/v1/conversations", headers={"If-None-Match": first.headers["etag"]})
        assert changed.status_code == 200 and changed.headers["etag"] != first.headers["etag"]
        assert (
            client.get("/api/v1/conversations/" + "f" * 32, headers={"If-None-Match": "*"}).status_code == 404
        )
        preflight = client.options(
            "/api/v1/conversations",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
                "Access-Control-Request-Headers": "If-None-Match",
            },
        )
        assert preflight.status_code == 200


@pytest.mark.asyncio
async def test_streams_and_downloads_keep_exact_chunks_and_bytes():
    for kind, extra in [
        (b"text/event-stream", []),
        (b"application/json", [(b"content-disposition", b"attachment; filename=evidence.json")]),
    ]:
        sent = []

        async def app(scope, receive, send):
            await send(
                {"type": "http.response.start", "status": 200, "headers": [(b"content-type", kind), *extra]}
            )
            await send({"type": "http.response.body", "body": b"first", "more_body": True})
            assert len(sent) == 2
            await send({"type": "http.response.body", "body": b"last", "more_body": False})

        async def send(value):
            sent.append(value)

        await ReadPerformanceMiddleware(app)(
            {
                "type": "http",
                "method": "GET",
                "path": "/api/v1/test",
                "headers": [(b"accept-encoding", b"gzip")],
            },
            None,
            send,
        )
        assert b"".join(v.get("body", b"") for v in sent) == b"firstlast"
    assert not accepts_gzip("br, gzip;q=0") and accepts_gzip("gzip;q=0.5")


@pytest.mark.asyncio
async def test_ui_source_status_singleflight_never_replaces_fresh_execution_gate():
    connectors = Connectors(Settings(environment="test"))
    calls = 0

    async def check(source):
        nonlocal calls
        calls += 1
        await asyncio.sleep(0)
        return {"connected": True, "mode": "test"}

    connectors.test = check
    first, second = await asyncio.gather(connectors.status("bigquery"), connectors.status("bigquery"))
    assert calls == 1 and first["checked_at"] == second["checked_at"]
    assert (await connectors.status("bigquery"))["cached"] and calls == 1
    await connectors.test("bigquery")
    assert calls == 2
    connectors._status_cache["bigquery"] = (0, first)
    await connectors.status("bigquery")
    assert calls == 3
    await connectors.close()


@pytest.mark.asyncio
async def test_chart_cache_deduplicates_views_expires_and_keeps_missing_page_validation():
    class CountingStore(MemoryStore):
        reads = 0

        async def get(self, collection, key):
            if collection.endswith("/pages"):
                self.reads += 1
                await asyncio.sleep(0)
            return await super().get(collection, key)

    store = CountingStore()
    rows = [{"month": "2024-01", "revenue": 10}, {"month": "2024-02", "revenue": 20}]
    art = artifact(rows)
    await store.put(f"artifacts/{art['id']}/pages", "0", {"rows": rows})
    cache = SavedChartCache(store, asyncio.Semaphore(2), max_entries=1)
    one, two = await asyncio.gather(cache.get(art, view="line"), cache.get(art, view="line"))
    assert one == two and store.reads == 1
    await cache.get(art, view="line", start=None, end=None, primary=None, order="value_desc", top=10)
    assert store.reads == 1
    await cache.get(art, view="bar")
    assert store.reads == 2 and len(cache.values) == 1
    cache.ttl = -1
    await cache.get(art, view="line")
    await store.delete(f"artifacts/{art['id']}/pages", "0")
    with pytest.raises(Exception, match="missing a page"):
        await cache.get(art, view="line")
    await cache.close()


def test_initial_preview_reuses_same_view_and_deleted_artifact_remains_404():
    store = MemoryStore()
    art = artifact([{"month": "2024-01", "revenue": 10}])
    with TestClient(create_app(Settings(environment="test"), store_override=store)) as client:
        asyncio.run(store.put("artifacts", art["id"], art))
        asyncio.run(
            store.put(f"artifacts/{art['id']}/pages", "0", {"rows": [{"month": "2024-01", "revenue": 10}]})
        )
        preview = client.get(f"/api/v1/artifacts/{art['id']}?metadata_only=true&initial_chart=true").json()
        assert (
            preview["initial_chart"]["data"]
            == client.get(f"/api/v1/artifacts/{art['id']}/chart-data?view=line").json()
        )
        asyncio.run(store.delete("artifacts", art["id"]))
        assert client.get(f"/api/v1/artifacts/{art['id']}/chart-data?view=line").status_code == 404
        assert "initial_chart" not in art
