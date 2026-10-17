import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import vm from "node:vm";
import ts from "typescript";

function load(file) {
  const compiledModule = { exports: {} };
  vm.runInNewContext(
    ts.transpileModule(readFileSync(new URL(file, import.meta.url), "utf8"), {
      compilerOptions: { module: ts.ModuleKind.CommonJS },
    }).outputText,
    {
      module: compiledModule,
      exports: compiledModule.exports,
      Intl,
      Date,
      URL,
      Blob,
      setTimeout,
    },
  );
  return compiledModule.exports;
}
const {
  formatMeasure,
  dateLabel,
  changeLabel,
  exploreQuestion,
  unitKey,
  chartNotes,
} = load("../src/lib/chart-format.ts");
const percent = { field: "rate", unit: "percent", percent_scale: "fraction" };

test("per-measure formatting distinguishes currency, counts and both percent scales", () => {
  assert.equal(
    formatMeasure(1234.5, { unit: "currency", currency: "USD" }),
    "$1,234.50",
  );
  assert.equal(formatMeasure(1234, { unit: "count" }), "1,234");
  assert.equal(formatMeasure(0.125, percent), "12.5%");
  assert.equal(
    formatMeasure(12.5, { unit: "percent", percent_scale: "whole" }),
    "12.5%",
  );
  assert.equal(formatMeasure(0.125, { unit: "percent" }), "0.13");
  for (const invalid of [null, undefined, "", true, Infinity, NaN])
    assert.equal(formatMeasure(invalid), "—");
});
test("dates use explicit UTC and labels retain full years", () => {
  assert.equal(dateLabel("2024-02"), "February 2024");
  assert.equal(dateLabel("2024-02-29"), "February 29, 2024");
  assert.equal(dateLabel("Electronics"), "Electronics");
});
test("comparisons label percentage points and zero baseline honestly", () => {
  assert.equal(
    changeLabel({ percentage_points: 5 }, percent),
    "+5 percentage points",
  );
  assert.match(
    changeLabel({ delta: 10, percent: null }, { unit: "count" }),
    /zero baseline/,
  );
  assert.notEqual(
    unitKey(percent),
    unitKey({ unit: "currency", currency: "USD" }),
  );
});
test("chart notes disclose sampling, omitted categories and partial source result", () => {
  const notes = chartNotes({
    coverage: {
      selected_rows: 5000,
      plotted_rows: 1000,
      sampled: true,
      complete: false,
      omitted_categories: 10,
    },
    scope: { start: "2023-01", end: "2026-09" },
    visualization: { partial_periods: ["2026-09"] },
  });
  for (const phrase of [
    "January 2023",
    "September 2026",
    "sample",
    "10 categories omitted",
    "Partial source",
    "Incomplete periods",
  ])
    assert.ok(notes.includes(phrase));
});
test("exploration draft identifies selected dimension, measure and scope", () => {
  const draft = exploreQuestion(
    "Revenue",
    "order_date",
    "2024-02-29",
    "sales",
    "2024 only",
  );
  assert.match(draft, /order date 2024-02-29/);
  assert.match(draft, /sales/);
  assert.match(draft, /2024 only/);
});
test("older browser preferences acquire chart defaults and reject malformed flags", () => {
  const { parsePreferences } = load("../src/lib/preferences.ts");
  assert.equal(parsePreferences('{"accent":"teal"}').chartHighlights, true);
  assert.equal(
    parsePreferences('{"chartComparisons":false}').chartComparisons,
    false,
  );
  assert.equal(
    parsePreferences('{"chartHighlights":"false"}').chartHighlights,
    true,
  );
});

test("prediction chart exports preserve cutoff, conditional meaning, and uncertainty", () => {
  const data = {
    coverage: { selected_rows: 48, plotted_rows: 48, sampled: false, complete: true, omitted_categories: 0 },
    scope: { start: "2023-01", end: "2026-12" },
    visualization: { partial_periods: [] },
    prediction: { cutoff: "2026-09-01", method: "seasonal_naive" },
  };
  const notes = chartNotes(data);
  assert.match(notes, /Observed through 2026-09-01/);
  assert.match(notes, /conditional predictions/);
  assert.match(notes, /uncertainty is not quantified/);
  const calibrated = chartNotes({ ...data, prediction: { ...data.prediction, interval: { level: .95, coverage: .92 } } });
  assert.match(calibrated, /future coverage is not guaranteed/);
});
