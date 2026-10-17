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
  readFileSync(new URL("../src/components/ui/table.tsx", import.meta.url), "utf8"),
  { compilerOptions: { module: ts.ModuleKind.CommonJS, jsx: ts.JsxEmit.ReactJSX } },
).outputText, { require, module: compiledModule, exports: compiledModule.exports });
const { Table } = compiledModule.exports;

test("multiple named result tables expose distinct keyboard-accessible scroll regions", () => {
  const html = renderToStaticMarkup(React.createElement("main", null,
    ...["Monthly revenue", "Product category revenue"].map(label =>
      React.createElement(Table, { key: label, "aria-label": label },
        React.createElement("caption", null, label))),
  ));
  assert.equal((html.match(/role="region"/g) ?? []).length, 2);
  assert.match(html, /aria-label="Monthly revenue scroll area"/);
  assert.match(html, /aria-label="Product category revenue scroll area"/);
  assert.equal((html.match(/tabindex="0"/g) ?? []).length, 2);
});

test("unlabeled tables retain native captions without generic duplicate landmarks", () => {
  const html = renderToStaticMarkup(React.createElement(Table, null,
    React.createElement("caption", null, "Forecast diagnostics")));
  assert.match(html, /<caption>Forecast diagnostics<\/caption>/);
  assert.doesNotMatch(html, /role="region"/);
});
