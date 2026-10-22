"""Small process-local cache of deterministic saved-chart views; never source or job data."""

import asyncio
import hashlib
import json
import time
from collections import OrderedDict

from app.chart_presentation import present, saved_rows


class SavedChartCache:
    def __init__(self, store, slots, ttl=30, max_bytes=8 * 1024 * 1024, max_entries=32):
        self.store, self.slots, self.ttl = store, slots, ttl
        self.max_bytes, self.max_entries = max_bytes, max_entries
        self.values = OrderedDict()
        self.pending = {}
        self.bytes = 0

    async def get(self, artifact, **options):
        # The route must read live artifact metadata first, including on a cache hit.
        # Frozen metadata + all view parameters bind this cache to exact saved evidence.
        options = {
            "start": None,
            "end": None,
            "primary": None,
            "order": "value_desc",
            "top": 10,
            "view": None,
        } | options
        key = hashlib.sha256(
            json.dumps([artifact, options, "presentation-v2"], sort_keys=True, default=str).encode()
        ).hexdigest()
        now = time.monotonic()
        for expired in [k for k, v in self.values.items() if v[0] <= now]:
            self.bytes -= self.values.pop(expired)[1]
        if key in self.values:
            self.values.move_to_end(key)
            return self.values[key][2]

        async def compute():
            async with self.slots:
                rows = [row async for row in saved_rows(self.store, artifact)]
                data = await asyncio.to_thread(present, artifact, rows, **options)
            size = len(json.dumps(data, default=str).encode())
            if size <= min(self.max_bytes, 1024 * 1024):
                if key in self.values:
                    self.bytes -= self.values.pop(key)[1]
                while self.values and (
                    len(self.values) >= self.max_entries or self.bytes + size > self.max_bytes
                ):
                    self.bytes -= self.values.popitem(last=False)[1][1]
                self.values[key] = (time.monotonic() + self.ttl, size, data)
                self.bytes += size
            return data

        task = self.pending.get(key)
        if task is None:
            if len(self.pending) >= 16:
                return await compute()  # Still bounded by the existing two chart slots.
            task = asyncio.create_task(compute())
            self.pending[key] = task

            def finished(done):
                self.pending.pop(key, None)
                if not done.cancelled():
                    done.exception()  # Consume failures even if every HTTP subscriber cancelled.

            task.add_done_callback(finished)
        return await asyncio.shield(task)

    async def close(self):
        tasks = list(self.pending.values())
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
        self.values.clear()
        self.bytes = 0
