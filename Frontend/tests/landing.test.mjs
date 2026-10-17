import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import vm from "node:vm";
import ts from "typescript";

const source = (path) => readFileSync(new URL(path, import.meta.url), "utf8");
function load(path) {
  const compiledModule = { exports: {} };
  vm.runInNewContext(
    ts.transpileModule(source(path), {
      compilerOptions: { module: ts.ModuleKind.CommonJS },
    }).outputText,
    {
      module: compiledModule,
      exports: compiledModule.exports,
      URLSearchParams,
      process: { env: {} },
    },
  );
  return compiledModule.exports;
}
const { workspacePath } = load("../src/lib/workspace-links.ts");
test("canonical workspace links encode conversation IDs on a fixed route", () => {
  assert.equal(workspacePath(), "/app");
  assert.equal(workspacePath("public-chat"), "/app?chat=public-chat");
  assert.equal(
    workspacePath("public-chat", "?chat=old&scope=example"),
    "/app?chat=public-chat&scope=example",
  );
  for (const id of [
    "a/b?x=1&next=https://evil.test",
    "name with spaces",
    "#fragment",
  ]) {
    const url = new URL(workspacePath(id), "https://querylane.test");
    assert.equal(url.origin, "https://querylane.test");
    assert.equal(url.pathname, "/app");
    assert.equal(url.searchParams.get("chat"), id);
    assert.equal(url.hash, "");
  }
});
test("legacy chat redirect is temporary, query-aware and same-origin", async () => {
  const rules = await load("../next.config.ts").default.redirects();
  assert.equal(rules.length, 1);
  assert.equal(rules[0].source, "/");
  assert.equal(rules[0].destination, "/app");
  assert.equal(rules[0].permanent, false);
  assert.equal(rules[0].has[0].type, "query");
  assert.equal(rules[0].has[0].key, "chat");
});
test("preview retains verified figures and observed/forecast boundaries", () => {
  const data = JSON.parse(source("../src/lib/landing-preview-data.json"));
  assert.equal(data.orders, 573348);
  assert.equal(data.months, 45);
  assert.equal(data.aov, 618.17);
  assert.equal(Math.round((data.revenue / data.orders) * 100) / 100, data.aov);
  assert.equal(data.cutoff, "2026-09-30");
  assert.equal(data.backtestOrigins, 3);
  assert.equal(data.intervalAvailable, false);
  const observed = data.points.filter((p) => p.observed !== null);
  const forecast = data.points.filter((p) => p.forecast !== null);
  assert.equal(observed.length, 9);
  assert.equal(forecast.length, 3);
  assert.ok(
    observed.every((p) => p.date <= data.cutoff && p.forecast === null),
  );
  assert.ok(forecast.every((p) => p.date > data.cutoff && p.observed === null));
  assert.equal(observed.at(-1).observed, 9447724.9);
  assert.equal(forecast[0].forecast, 9821574.38515586);
  assert.equal(forecast[1].forecast, 13396864.111970706);
  assert.equal(forecast[2].forecast, 13004166.888183326);
  assert.equal(
    Math.round((observed[8].observed / observed[7].observed - 1) * 10000) / 100,
    -1.35,
  );
});
// Boundary regressions: marketing must never acquire live analytics or audio.
test("guided previews have no dependency on live application clients", () => {
  for (const file of [
    "../src/app/page.tsx",
    "../src/components/landing/product-tour.tsx",
    "../src/components/landing/product-illustrations.tsx",
    "../src/components/landing/mobile-navigation.tsx",
  ]) {
    const code = source(file);
    for (const forbidden of [
      /from ["']@\/lib\/(api|voice|skill-author-voice)/,
      /from ["']@\/components\/(workspace|report-workspace|charts\/)/,
      /getUserMedia\(/,
      /fetch\(/,
      /<audio/,
    ])
      assert.doesNotMatch(code, forbidden);
    assert.doesNotMatch(
      code,
      /<Link(?![^>]*prefetch=\{false\})[^>]*href=\{workspacePath\(\)\}/,
    );
  }
});
test("source-conversation links and new chat retain the workspace route", () => {
  const workspace = source("../src/components/workspace.tsx");
  assert.doesNotMatch(workspace, /replaceState\(null, "", "\/"\)/);
  assert.match(workspace, /workspacePath\(created.id\)/);
  for (const file of ["report-workspace", "dashboard-workspace"])
    assert.doesNotMatch(
      source(`../src/components/${file}.tsx`),
      /href=\{`\/\?chat=/,
    );
});
