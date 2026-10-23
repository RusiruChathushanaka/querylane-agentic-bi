import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import vm from 'node:vm';
import ts from 'typescript';

function load(path, require) {
  const compiledModule = { exports: {} };
  const code = ts.transpileModule(readFileSync(new URL(path, import.meta.url), 'utf8'), {
    compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2022, jsx: ts.JsxEmit.ReactJSX },
  }).outputText;
  vm.runInNewContext(code, { module: compiledModule, exports: compiledModule.exports, require });
  return compiledModule.exports;
}

test('application links navigate normally without speculative route fetches', () => {
  const Link = load('../src/components/ui/app-link.tsx', name => {
    if (name === 'next/link') return { default: 'next-link' };
    return { jsx: (type, props) => ({ type, props }) };
  }).default;
  const clicked = () => {};
  const rendered = Link({ href: '/reports', children: 'Reports', onClick: clicked, 'aria-label': 'Saved reports' });
  assert.equal(rendered.props.prefetch, false);
  assert.equal(rendered.props.href, '/reports');
  assert.equal(rendered.props.onClick, clicked);
  assert.equal(rendered.props['aria-label'], 'Saved reports');
});

test('a visible card starts code loading while saved metadata is pending', async () => {
  let codeStarted = false, release, capturedSignal;
  const metadata = new Promise(resolve => { release = resolve; });
  const { loadSavedCard, preparedResultCard } = load('../src/components/saved-card-loader.ts', name => {
    if (name.includes('saved-result-loader')) return { savedResult: (_path, signal) => { capturedSignal = signal; return metadata; } };
    if (name.includes('result-card')) { codeStarted = true; return { default: () => {} }; }
    throw new Error(name);
  });
  const signal = new AbortController().signal;
  const pending = loadSavedCard('/artifacts/saved?metadata_only=true', signal);
  assert.equal(preparedResultCard(), undefined);
  await new Promise(resolve => setImmediate(resolve));
  assert.equal(codeStarted, true, 'chart module must not wait for the metadata response');
  assert.equal(capturedSignal, signal);
  const component = preparedResultCard();
  assert.equal(typeof component, 'function');
  release({ id: 'saved' });
  assert.equal((await pending).id, 'saved');
  assert.equal(preparedResultCard(), component, 'the renderer must reuse ready code synchronously');
});

test('optional code warm-up failure does not hide saved metadata or replay reads', async () => {
  let reads = 0;
  const { loadSavedCard, preparedResultCard } = load('../src/components/saved-card-loader.ts', name => {
    if (name.includes('saved-result-loader')) return { savedResult: async () => { reads++; return { id: 'saved' }; } };
    throw new Error('chunk unavailable');
  });
  assert.equal((await loadSavedCard('/artifacts/saved')).id, 'saved');
  await Promise.resolve(); await Promise.resolve();
  assert.equal(reads, 1);
  assert.equal(preparedResultCard(), undefined, 'a failed warm-up must permit the ordinary loader to retry');
});

test('ready chart code renders synchronously while unprepared code retains its dynamic fallback', () => {
  const Ready = () => {};
  const Deferred = () => {};
  const state = { ReadyResultCard: undefined };
  const { default: Card } = load('../src/components/prepared-result-card.tsx', name => {
    if (name === 'next/dynamic') return { default: () => Deferred };
    if (name === './saved-card-loader') return state;
    if (name === 'react/jsx-runtime') return { jsx: (type, props) => ({ type, props }) };
    return { Skeleton: 'skeleton' };
  });
  const artifact = { id: 'saved' };
  assert.equal(Card({ artifact }).type, Deferred);
  state.ReadyResultCard = Ready;
  const rendered = Card({ artifact });
  assert.equal(rendered.type, Ready);
  assert.equal(rendered.props.artifact, artifact);
});
