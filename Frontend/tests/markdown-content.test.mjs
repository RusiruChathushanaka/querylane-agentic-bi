import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { createRequire } from "node:module";
import vm from "node:vm";
import ts from "typescript";
import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";

// Exercise the production TSX renderer without adding a separate test bundler.
const compiled = ts.transpileModule(
  readFileSync(
    new URL("../src/components/markdown-content.tsx", import.meta.url),
    "utf8",
  ),
  {
    compilerOptions: {
      module: ts.ModuleKind.CommonJS,
      jsx: ts.JsxEmit.ReactJSX,
      esModuleInterop: true,
    },
  },
).outputText;
const compiledModule = { exports: {} };
vm.runInNewContext(compiled, {
  module: compiledModule,
  exports: compiledModule.exports,
  require: (id) => id.endsWith(".css") ? {} : createRequire(import.meta.url)(id),
});
const { MarkdownContent, MessageContent } = compiledModule.exports;
const render = (text, props = {}) =>
  renderToStaticMarkup(
    createElement(MessageContent, { role: "assistant", ...props }, text),
  );

test("assistant messages render headings, emphasis, lists, paragraphs, and code", () => {
  const html = render(
    "## Summary\n\n**Revenue** grew by *12%*.\n\n- Sales\n- Returns\n\n1. Compare\n2. Review\n\n```sql\nSELECT 1;\n```",
  );
  for (const expected of [
    "<h2>Summary</h2>",
    "<strong>Revenue</strong>",
    "<em>12%</em>",
    "<ul>",
    "<ol>",
    "<li>Sales</li>",
    'class="language-sql"',
  ]) {
    assert.ok(html.includes(expected), expected);
  }
  assert.ok(!html.includes("**Revenue**"));
});

test("GFM tables, task lists, and strikethrough render in shared previews", () => {
  const html = renderToStaticMarkup(
    createElement(
      MarkdownContent,
      null,
      "| Region | Sales |\n| --- | ---: |\n| West | 120 |\n\n- [x] Complete\n\n~~Old definition~~",
    ),
  );
  for (const expected of [
    "<table>",
    "<th>Region</th>",
    "<td>West</td>",
    'aria-label="Markdown table"',
    'tabindex="0"',
    'type="checkbox"',
    'aria-label="Completed task"',
    "<del>Old definition</del>",
  ]) {
    assert.ok(html.includes(expected), expected);
  }
});

test("untrusted Markdown cannot insert HTML, unsafe URLs, or remote images", () => {
  const html = render(
    '<script>alert(1)</script>\n\n<img src="https://example.com/tracker" onerror="alert(1)">\n\n![track](https://example.com/track.png)\n\n[bad](javascript:alert%281%29)\n\n[safe](https://example.com/evidence)',
  );
  for (const forbidden of [
    "<script",
    "<img",
    "onerror=",
    "javascript:",
    "track.png",
  ])
    assert.ok(!html.includes(forbidden), forbidden);
  assert.ok(html.includes('href="https://example.com/evidence"'));
  assert.ok(html.includes('rel="noopener noreferrer"'));
});

test("visitor messages remain literal, including markup-looking input", () => {
  const html = render("**literal** <img src=x>\nnext line", {
    role: "user",
    className: "message-text",
  });
  assert.equal(
    html,
    '<p class="message-text">**literal** &lt;img src=x&gt;\nnext line</p>',
  );
});

test("incomplete streaming Markdown renders safely and completes on the next update", () => {
  assert.ok(render("Revenue **grew").includes("Revenue **grew"));
  assert.ok(render("Revenue **grew**").includes("<strong>grew</strong>"));
  assert.ok(render("```sql\nSELECT").includes("SELECT"));
});
