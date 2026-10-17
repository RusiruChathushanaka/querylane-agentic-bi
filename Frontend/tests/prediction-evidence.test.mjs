import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { createRequire } from "node:module";
import vm from "node:vm";
import ts from "typescript";
import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
const require = createRequire(import.meta.url);
const compiledModule = { exports: {} };
vm.runInNewContext(ts.transpileModule(
  readFileSync(new URL("../src/components/prediction-evidence.tsx", import.meta.url), "utf8"),
  { compilerOptions: { module: ts.ModuleKind.CommonJS, jsx: ts.JsxEmit.ReactJSX } },
).outputText, { require, module: compiledModule, exports: compiledModule.exports });
const { PredictionEvidence } = compiledModule.exports;
const base = { method: "timesfm_3", cutoff: "2026-09-30", horizon: 3,
  limitations: ["Synthetic history does not guarantee future performance."],
  scores: { timesfm_3: { mae: 5, rmse: 6, folds: [] }, ets: { mae: 10, rmse: 12, folds: [] } },
  comparison: { status: "evaluated", model: "TimesFM 3.0", preview: true,
    reason: "Compared against the baseline.", jobs: [], input_hash: "abc", selection_policy_version: 1 } };
function render(prediction, artifactId = "a") {
  return renderToStaticMarkup(React.createElement(PredictionEvidence, { prediction, artifactId, reportId: "report", reportVersion: 2 }));
}
test("managed method, preview, selection and evidence are accessible without hydration", () => {
  const html = render(base);
  assert.match(html, /TimesFM 3.0 · Preview/);
  assert.match(html, /<caption>/);
  assert.match(html, /<th scope="col">MAE/);
  assert.match(html, /<summary>Forecast validation/);
  assert.match(html, /Forecast method comparison a/);
  assert.match(html, /Selected/);
  assert.match(html, /uncertainty is not quantified/);
  assert.match(html, /reports\/report\?version=2/);
});
test("scenario and provider failure remain clear and escaped", () => {
  const html = render({ ...base, kind: "scenario", scenario_name: "<script>attack</script>",
    comparison: { ...base.comparison, status: "unavailable", reason: "Permission denied; statistical evidence retained." } });
  assert.match(html, /Conditional scenario comparison/);
  assert.match(html, /same method and history/);
  assert.match(html, /unavailable/);
  assert.doesNotMatch(html, /<script>/);
});
test("historical artifacts need no new metadata and retain distinct detail regions", () => {
  const old = { method: "ets", cutoff: "2026-09-30", horizon: 3, limitations: [] };
  assert.match(render(old), /ets/);
  assert.doesNotMatch(render(old), /TimesFM comparison/);
  assert.notEqual(render(base, "one"), render(base, "two"));
});
test("planning assumptions and allocated estimates cannot be mistaken for independent forecasts", () => {
  const html = render({ ...base, kind: "adjusted_plan", status: "allocated" });
  assert.match(html, /User planning assumptions/);
  assert.match(html, /not independently modeled/);
});
