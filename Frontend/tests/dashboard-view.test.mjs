import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import vm from "node:vm";
import ts from "typescript";

function load(file, api) {
  const compiledModule = { exports: {} };
  const code = ts.transpileModule(
    readFileSync(new URL(file, import.meta.url), "utf8"),
    { compilerOptions: { module: ts.ModuleKind.CommonJS } },
  ).outputText;
  vm.runInNewContext(code, {
    module: compiledModule,
    exports: compiledModule.exports,
    require: () => ({ api }),
    AbortController,
    DOMException,
    Promise,
    Map,
  });
  return compiledModule.exports;
}
const { initialChartView, describeChartView } = load(
  "../src/lib/chart-view-state.ts",
);
test("saved views resolve comparison visibility, formatting and scope without changing the artifact", () => {
  const artifact = {
    visualization: {
      y: ["revenue", "target"],
      measures: [
        { field: "revenue", role: "primary" },
        { field: "target", role: "target" },
      ],
    },
  };
  const original = JSON.stringify(artifact);
  const view = initialChartView(
    artifact,
    { chartComparisons: false, chartHighlights: false, decimals: "1" },
    "line",
  );
  assert.equal(JSON.stringify(view.visible_measures), '["revenue"]');
  assert.equal(view.primary, "revenue");
  assert.equal(view.highlights, false);
  assert.equal(view.decimals, 1);
  assert.equal(view.start, null);
  assert.equal(JSON.stringify(artifact), original);
  assert.match(
    describeChartView({ ...view, start: "2024-01-01", end: "2024-12-31" }),
    /2024-01-01 → 2024-12-31/,
  );
});

const flush = () => new Promise((resolve) => setTimeout(resolve, 0));
function reader() {
  let active = 0,
    max = 0;
  const calls = [];
  const api = (path, { signal }) =>
    new Promise((resolve, reject) => {
      active++;
      max = Math.max(max, active);
      let settled = false;
      const finish = (value, failed = false) => {
        if (settled) return;
        settled = true;
        active--;
        if (failed) reject(value);
        else resolve(value);
      };
      signal.addEventListener(
        "abort",
        () => finish(new DOMException("Aborted", "AbortError"), true),
        { once: true },
      );
      if (signal.aborted)
        finish(new DOMException("Aborted", "AbortError"), true);
      calls.push({
        path,
        signal,
        resolve: (value) => finish(value),
        reject: (value) => finish(value, true),
      });
    });
  return {
    ...load("../src/lib/saved-result-loader.ts", api),
    calls,
    get max() {
      return max;
    },
  };
}
test("saved-result reads deduplicate and reserve at most two concurrent slots", async () => {
  const r = reader();
  const a = r.savedResult("a"),
    same = r.savedResult("a"),
    b = r.savedResult("b"),
    c = r.savedResult("c");
  assert.equal(r.calls.length, 2);
  r.calls[0].resolve("A");
  await flush();
  assert.equal(r.calls.length, 3);
  r.calls[1].resolve("B");
  r.calls[2].resolve("C");
  assert.deepEqual(await Promise.all([a, same, b, c]), ["A", "A", "B", "C"]);
  assert.equal(r.max, 2);
});
test("aborting one subscriber preserves a shared read for another", async () => {
  const r = reader(),
    controller = new AbortController();
  const one = r.savedResult("same", controller.signal),
    two = r.savedResult("same");
  controller.abort();
  await assert.rejects(one, { name: "AbortError" });
  assert.equal(r.calls[0].signal.aborted, false);
  r.calls[0].resolve("saved result");
  assert.equal(await two, "saved result");
});
test("obsolete reads abort and a failed result can be retried", async () => {
  const r = reader(),
    controller = new AbortController();
  const obsolete = r.savedResult("old", controller.signal);
  controller.abort();
  await assert.rejects(obsolete, { name: "AbortError" });
  assert.equal(r.calls[0].signal.aborted, true);
  const failed = r.savedResult("retry");
  r.calls[1].reject(new Error("offline"));
  await assert.rejects(failed, /offline/);
  await flush();
  const retried = r.savedResult("retry");
  r.calls[2].resolve("success");
  assert.equal(await retried, "success");
});
