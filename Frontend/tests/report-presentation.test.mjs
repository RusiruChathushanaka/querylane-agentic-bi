import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { createRequire } from "node:module";
import vm from "node:vm";
import ts from "typescript";
import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
const require = createRequire(import.meta.url);
const source = readFileSync(
  new URL("../src/components/report-workspace.tsx", import.meta.url),
  "utf8",
);
const labelModule = { exports: {} };
vm.runInNewContext(
  ts.transpileModule(
    readFileSync(
      new URL("../src/components/prediction-evidence.tsx", import.meta.url),
      "utf8",
    ),
    {
      compilerOptions: {
        module: ts.ModuleKind.CommonJS,
        jsx: ts.JsxEmit.ReactJSX,
      },
    },
  ).outputText,
  { require, module: labelModule, exports: labelModule.exports },
);
const compiled = { exports: {} };
// Exercise the exported report-specific view, without mounting the reader's API lifecycle.
vm.runInNewContext(
  ts.transpileModule(
    source.slice(source.indexOf("export function ReportPrediction")),
    {
      compilerOptions: {
        module: ts.ModuleKind.CommonJS,
        jsx: ts.JsxEmit.ReactJSX,
      },
    },
  ).outputText,
  {
    require,
    module: compiled,
    exports: compiled.exports,
    PredictionEvidence: () => null,
    forecastMethodLabel: labelModule.exports.forecastMethodLabel,
  },
);
const render = (prediction) =>
  renderToStaticMarkup(
    React.createElement(compiled.exports.ReportPrediction, {
      artifact: { id: "saved", prediction },
    }),
  );
const base = {
  method: "timesfm_3",
  preview: true,
  cutoff: "2026-09-30",
  grain: "month",
  horizon: 3,
  scores: {
    timesfm_3: { mae: 10, rmse: 12, folds: [] },
    ets: { mae: 30, rmse: 35, folds: [] },
  },
};
test("report overview retains cutoff, selected method, preview and uncertainty without inventing currency", () => {
  const html = render(base);
  assert.match(html, /Observed through/);
  assert.match(html, /2026-09-30/);
  assert.match(html, /TimesFM 3.0.*Preview/);
  assert.match(html, /<caption>/);
  assert.match(html, /uncertainty is not quantified/);
  assert.doesNotMatch(html, /USD|accuracy percentage:|confidence: 95/);
});
test("scenario assumptions keep genuine zero paths and escape visitor content", () => {
  const html = render({
    ...base,
    kind: "scenario",
    drivers: ["promotion"],
    assumptions: ["<script>test</script>"],
    future_drivers: [{ promotion: 0 }],
    scenario_drivers: [{ promotion: 1 }],
  });
  assert.match(html, /not causal lift estimates/);
  assert.match(html, /promotion.*0/);
  assert.doesNotMatch(html, /<script>/);
});
test("older forecasts and allocated planning evidence remain readable and honestly labeled", () => {
  assert.match(
    render({ method: "ets", cutoff: "2026-09-30", horizon: 3, grain: "month" }),
    /ets/,
  );
  const html = render({ ...base, kind: "adjusted_plan", status: "allocated" });
  assert.match(html, /not statistical predictions/);
  assert.match(html, /not independently modeled/);
});
