import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import vm from "node:vm";
import ts from "typescript";

const compiled = { exports: {} };
vm.runInNewContext(ts.transpileModule(
  readFileSync(new URL("../src/lib/report-assumptions.ts", import.meta.url), "utf8"),
  { compilerOptions: { module: ts.ModuleKind.CommonJS } },
).outputText, { module: compiled, exports: compiled.exports });
const { assumptionValues, assumptionRows, assumptionHorizon } = compiled.exports;

test("future assumptions require explicit finite values and preserve genuine zero", () => {
  assert.deepEqual(Array.from(assumptionValues("0", 3)), [0, 0, 0]);
  assert.deepEqual(Array.from(assumptionValues("1, 2; 3", 3)), [1, 2, 3]);
  for (const value of ["", " ", "NaN", "Infinity", "1e999", "0x10", "1,2"])
    assert.throws(() => assumptionValues(value, 3));
});
test("assumption rows align every driver and period without invented defaults", () => {
  const requirement = { target: "revenue", drivers: ["promotion", "stores"], grain: "month", horizon: null };
  assert.equal(assumptionHorizon(requirement), 3);
  assert.deepEqual(JSON.parse(JSON.stringify(assumptionRows(requirement, {
    promotion: "0,1,2", stores: "24",
  }))), [{ promotion: 0, stores: 24 }, { promotion: 1, stores: 24 }, { promotion: 2, stores: 24 }]);
  assert.throws(() => assumptionRows(requirement, { promotion: "1" }));
});
