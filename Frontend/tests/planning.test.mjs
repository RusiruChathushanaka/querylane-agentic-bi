import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { createRequire } from 'node:module';
import vm from 'node:vm';
import ts from 'typescript';
import React from 'react';
import { renderToStaticMarkup } from 'react-dom/server';
const require = createRequire(import.meta.url);
function load(path, overrides = {}) {
  const loadedModule = { exports: {} };
  vm.runInNewContext(ts.transpileModule(readFileSync(new URL(path, import.meta.url), 'utf8'), {
    compilerOptions: { module: ts.ModuleKind.CommonJS, jsx: ts.JsxEmit.ReactJSX },
  }).outputText, { module: loadedModule, exports: loadedModule.exports, require: key => overrides[key] ?? require(key), crypto });
  return loadedModule.exports;
}
const { dashboardChanges } = load('../src/lib/planning-review.ts');
const card = (id, title = id) => ({ artifact_id: id, title, note: '', width: 'standard', view: { view: 'line' } });
test('review compares the complete saved proposal including reorder and removals', () => {
  const base = [card('a'), card('b'), card('c')];
  const result = dashboardChanges(base, [card('a'), card('c', 'Changed title'), card('d')]);
  assert.deepEqual(JSON.parse(JSON.stringify(result.cards)), [
    { id: 'a', status: 'Retained' }, { id: 'c', status: 'Modified' }, { id: 'd', status: 'Added' },
  ]);
  assert.equal(result.removed[0].artifact_id, 'b');
  assert.equal(base[2].title, 'c');
});
test('an ambiguous mutation retains its identity while changed definitions get a new identity', () => {
  const reference = { current: undefined };
  const { usePendingRequest } = load('../src/hooks/use-pending-request.ts', { react: { useRef: value => {
    reference.current ??= value;
    return reference;
  } } });
  const hook = usePendingRequest();
  const a = hook.id('publish', { version: 1 });
  assert.equal(usePendingRequest().id('publish', { version: 1 }), a);
  assert.notEqual(hook.id('publish', { version: 2 }), a);
  hook.complete('publish', { version: 1 });
  assert.notEqual(hook.id('publish', { version: 1 }), a);
});
test('saved metric evidence links to immutable versions and escapes visitor text', () => {
  const { MetricEvidence } = load('../src/components/metric-evidence.tsx', {
    '@/components/ui/app-link': load('../src/components/ui/app-link.tsx', { 'next/link': { default: props => { const copy = {...props}; delete copy.prefetch; return React.createElement('a', copy); } } }),
  });
  const html = renderToStaticMarkup(React.createElement(MetricEvidence, { metrics: [
    { id: 'abc', version: 3, definition: { name: '<script>bad</script>', description: 'After discounts' } },
  ] }));
  assert.match(html, /href="\/metrics\/abc\/revisions\/3"/);
  assert.match(html, /&lt;script&gt;/);
  assert.doesNotMatch(html, /<script>/);
  assert.equal(renderToStaticMarkup(React.createElement(MetricEvidence, { metrics: [] })), '');
});
