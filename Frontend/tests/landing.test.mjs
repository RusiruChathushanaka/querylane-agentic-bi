import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import vm from "node:vm";
import ts from "typescript";
import { createRequire } from "node:module";
import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";

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
  assert.equal(forecast[0].forecast, 10272054);
  assert.equal(forecast[1].forecast, 14367920);
  assert.equal(forecast[2].forecast, 13845351);
  assert.equal(
    Math.round((observed[8].observed / observed[7].observed - 1) * 10000) / 100,
    -1.35,
  );
});
test("TimesFM previews reconcile to immutable verified report values and scores", () => {
  const data = JSON.parse(source("../src/lib/landing-preview-data.json"));
  const evidence = JSON.parse(
    source("../../docs/evaluation/timesfm-deployed.json"),
  );
  const forecast = evidence.reports[0].predictions[0];
  const scenario = evidence.reports[1].predictions.find(
    (p) => p.kind === "scenario",
  );
  assert.equal(data.method, "TimesFM 3.0");
  assert.equal(data.preview, true);
  assert.equal(data.artifactId, forecast.artifact_id);
  assert.equal(data.scenario.artifactId, scenario.artifact_id);
  assert.deepEqual(
    data.points.filter((p) => p.forecast !== null),
    forecast.comparison.native_final_intervals.baseline.map((p) => ({
      date: p.date,
      observed: null,
      forecast: p.value,
    })),
  );
  for (const row of data.scores) {
    assert.equal(row.mae, forecast.scores[row.method].mae);
    assert.equal(row.rmse, forecast.scores[row.method].rmse);
    assert.equal(row.selected, row.method === forecast.method);
  }
  assert.equal(data.scenario.cutoff, data.cutoff);
  assert.equal(data.scenario.points.length, 14);
  assert.equal(data.scenario.contextDays, scenario.comparison.context);
  assert.equal(data.scenario.intervalAvailable, false);
  const paths = scenario.comparison.native_final_intervals;
  data.scenario.points.forEach((p, i) => {
    assert.equal(p.date, paths.baseline[i].date);
    assert.ok(p.date > data.cutoff);
    assert.equal(p.baseline, paths.baseline[i].value);
    assert.equal(p.alternative, paths.scenario[i].value);
  });
  assert.ok(
    scenario.future_drivers.every(
      (p) => p.promotion_day === data.scenario.baselineDriver,
    ),
  );
  assert.ok(
    scenario.scenario_drivers.every(
      (p) => p.promotion_day === data.scenario.alternativeDriver,
    ),
  );
  for (const [fixture, record] of [
    [data, evidence.reports[0]],
    [data.scenario, evidence.reports[1]],
  ]) {
    const link = new URL(fixture.reportUrl);
    assert.equal(
      link.origin,
      "https://agentic-bi-frontend-wekihucn7q-as.a.run.app",
    );
    assert.equal(link.pathname, `/reports/${record.report_id}`);
    assert.equal(link.searchParams.get("version"), "1");
  }
});
test("scenario illustration exposes both conditional paths with a semantic table", () => {
  const require = createRequire(import.meta.url);
  const compiledModule = { exports: {} };
  const code = ts.transpileModule(
    source("../src/components/landing/product-illustrations.tsx"),
    {
      compilerOptions: {
        module: ts.ModuleKind.CommonJS,
        jsx: ts.JsxEmit.ReactJSX,
        esModuleInterop: true,
        target: ts.ScriptTarget.ES2022,
      },
    },
  ).outputText;
  const data = JSON.parse(source("../src/lib/landing-preview-data.json"));
  new Function("require", "module", "exports", code)(
    (name) =>
      name === "@/lib/landing-preview-data.json" ? data : require(name),
    compiledModule,
    compiledModule.exports,
  );
  const html = renderToStaticMarkup(
    createElement(compiledModule.exports.ScenarioIllustration),
  );
  assert.match(html, /Neither series is observed data or a causal effect/);
  assert.match(html, /landing-scenario-baseline/);
  assert.match(html, /landing-scenario-alternative/);
  assert.match(html, /<caption>Saved conditional predictions/);
  assert.equal((html.match(/scope="row"/g) || []).length, 14);
  assert.equal((html.match(/scope="col"/g) || []).length, 3);
  assert.match(html, /<summary>View scenario data<\/summary>/);
  const forecast = renderToStaticMarkup(
    createElement(compiledModule.exports.RevenueIllustration, {
      forecast: true,
    }),
  );
  assert.match(forecast, /TimesFM 3.0 Preview point forecast/);
  assert.doesNotMatch(forecast, /ETS point forecast/);
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
