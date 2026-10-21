import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { createRequire } from "node:module";
import vm from "node:vm";
import ts from "typescript";
import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
const require = createRequire(import.meta.url);
function load(file, aliases = {}) {
  const compiledModule = { exports: {} };
  vm.runInNewContext(
    ts.transpileModule(readFileSync(new URL(file, import.meta.url), "utf8"), {
      compilerOptions: {
        module: ts.ModuleKind.CommonJS,
        jsx: ts.JsxEmit.ReactJSX,
      },
    }).outputText,
    {
      require: (id) => aliases[id] ?? require(id),
      module: compiledModule,
      exports: compiledModule.exports,
    },
  );
  return compiledModule.exports;
}
const select = load("../src/components/ui/select.tsx");
const { AppSelect, AppSelectItem, encodeChoice, decodeChoice } = load(
  "../src/components/ui/app-select.tsx",
  { "@/components/ui/select": select },
);
test("dropdown encoding preserves defaults, zero, numeric versions and reserved-looking user values", () => {
  for (const value of [
    "",
    0,
    1,
    6,
    "business",
    "__querylane_empty_choice__",
    "v:example",
    "<script>",
    "metric/one",
  ]) {
    assert.equal(decodeChoice(encodeChoice(value)), String(value));
  }
});
test("shared dropdown renders a labeled combobox, disabled state and a selectable default safely", () => {
  const html = renderToStaticMarkup(
    React.createElement(
      AppSelect,
      {
        id: "model",
        "aria-label": "Model choice",
        value: "",
        disabled: true,
        onValueChange: () => {},
      },
      React.createElement(AppSelectItem, { value: "" }, "Workspace default"),
      React.createElement(AppSelectItem, { value: "<script>" }, "<script>"),
    ),
  );
  assert.match(html, /role="combobox"/);
  assert.match(html, /aria-label="Model choice"/);
  assert.match(html, /disabled/);
  assert.doesNotMatch(html, /<script>/);
});
