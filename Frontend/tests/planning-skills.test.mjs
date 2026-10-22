import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { createRequire } from 'node:module';
import vm from 'node:vm';
import ts from 'typescript';
import { renderToStaticMarkup } from 'react-dom/server';

const require = createRequire(import.meta.url);
const compiled = ts.transpileModule(readFileSync(new URL('../src/components/planning-skills.tsx', import.meta.url), 'utf8'), {
  compilerOptions: { module: ts.ModuleKind.CommonJS, jsx: ts.JsxEmit.ReactJSX },
}).outputText;
const skills = [
  { id: 'a', name: 'Revenue forecasting', source: 'all', enabled: true },
  { id: 'b', name: 'TimesFM comparison', source: 'bigquery', enabled: true },
  { id: 'c', name: 'Planning assumptions', source: 'all', enabled: true },
  { id: 'd', name: 'Customer cohorts', source: 'postgres', enabled: true },
  { id: 'e', name: 'Disabled example', source: 'all', enabled: false },
];

function picker({ selected = [], source = 'all', query = '', loading = false, error = '', available = skills } = {}) {
  const values = [available, error, loading, query, 0];
  const loadedModule = { exports: {} };
  let changed;
  vm.runInNewContext(compiled, {
    module: loadedModule, exports: loadedModule.exports,
    require: key => key === 'react' ? {
      useState: () => [values.shift(), () => {}], useEffect: () => {}, useId: () => 'skills-hint',
    } : key === '@/lib/api' ? {} : key === './resource-feedback' ? { ResourceFeedback: ({resource, label}) => require('react').createElement('p', {role: resource.error ? 'alert' : 'status'}, resource.error || (resource.pending ? label : '')) } : require(key),
  });
  const tree = loadedModule.exports.PlanningSkills({ source, selected, onChange: ids => { changed = [...ids]; } });
  const inputs = [];
  let search;
  function visit(node) {
    if (!node || typeof node !== 'object') return;
    if (Array.isArray(node)) return node.forEach(visit);
    if (node.type === 'input' && node.props.type === 'checkbox') inputs.push(node);
    if (node.type === 'input' && node.props.type === 'search') search = node;
    visit(node.props?.children);
  }
  visit(tree);
  return { inputs, search, html: renderToStaticMarkup(tree), change: index => { inputs[index].props.onChange(); return changed; } };
}

test('three selected skills remain removable while other choices are disabled', () => {
  const p = picker({ selected: ['a', 'b', 'c'] });
  assert.deepEqual(p.inputs.map(i => i.props.disabled), [false, false, false, true, true]);
  assert.deepEqual(p.change(1), ['a', 'c']);
  assert.match(p.html, /<legend>Attached skills/);
  assert.match(p.html, /aria-describedby="skills-hint"/);
  assert.match(p.html, /role="region" aria-label="Available planning skills" tabindex="0"/);
  assert.match(p.html, /<label[^>]*><input type="checkbox"[^>]*\/><span>Revenue forecasting<\/span><\/label>/);
});

test('search is case insensitive and retains attachments outside the visible results', () => {
  const p = picker({ selected: ['a'], query: '  TIMESFM  ' });
  assert.equal(p.inputs.length, 1);
  assert.deepEqual(p.change(0), ['a', 'b']);
  assert.doesNotMatch(p.html, /<span>Revenue forecasting/);
  assert.match(p.html, /<span>Find skills<\/span><input type="search"/);
  assert.match(picker({ query: 'no such skill' }).html, /role="status">No skills match your search/);
});

test('source-incompatible and disabled skills cannot be newly attached', () => {
  const p = picker({ source: 'postgres' });
  assert.deepEqual(p.inputs.map(i => i.props.disabled), [false, true, false, false, true]);
  assert.match(p.html, /TimesFM comparison — unavailable for this source/);
  assert.deepEqual(p.change(3), ['d']);
});

test('Enter in skill search cannot implicitly submit the paid planning form', () => {
  const p = picker();
  let prevented = false;
  p.search.props.onKeyDown({ key: 'Enter', preventDefault: () => { prevented = true; } });
  assert.equal(prevented, true);
  prevented = false;
  p.search.props.onKeyDown({ key: 'a', preventDefault: () => { prevented = true; } });
  assert.equal(prevented, false);
});

test('loading, failed and empty libraries have distinct messages', () => {
  const loading = picker({ available: [], loading: true }).html;
  assert.match(loading, /role="status">Loading shared skills/);
  assert.doesNotMatch(loading, /No shared skills available/);
  const failed = picker({ available: [], error: 'Service unavailable' }).html;
  assert.match(failed, /role="alert">Service unavailable/);
  assert.doesNotMatch(failed, /No shared skills available/);
  assert.match(picker({ available: [] }).html, /No shared skills available/);
});
