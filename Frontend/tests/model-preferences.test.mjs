import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import vm from "node:vm";
import ts from "typescript";

const compiledModule = { exports: {} };
vm.runInNewContext(
  ts.transpileModule(
    readFileSync(new URL("../src/lib/preferences.ts", import.meta.url), "utf8"),
    { compilerOptions: { module: ts.ModuleKind.CommonJS } },
  ).outputText,
  { module: compiledModule, exports: compiledModule.exports },
);
const { parsePreferences } = compiledModule.exports;

test("model preference accepts current pinned choices and migrates older browser storage", () => {
  for (const textModel of [
    "default",
    "gemini-3.8-flash",
    "gemini-3.5-flash-lite",
  ]) {
    assert.equal(
      parsePreferences(JSON.stringify({ textModel })).textModel,
      textModel,
    );
  }
  assert.equal(parsePreferences('{"accent":"teal"}').textModel, "default");
  assert.equal(
    parsePreferences('{"textModel":"arbitrary-model"}').textModel,
    "default",
  );
  assert.equal(parsePreferences('{"textModel":true}').textModel, "default");
  assert.equal(parsePreferences("invalid").textModel, "default");
});
