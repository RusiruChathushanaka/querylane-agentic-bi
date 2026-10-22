import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { createRequire } from 'node:module';
import vm from 'node:vm';
import ts from 'typescript';
import React from 'react';
import { renderToStaticMarkup } from 'react-dom/server';
const require=createRequire(import.meta.url),m={exports:{}};
vm.runInNewContext(ts.transpileModule(readFileSync(new URL('../src/components/resource-feedback.tsx',import.meta.url),'utf8'),{compilerOptions:{module:ts.ModuleKind.CommonJS,jsx:ts.JsxEmit.ReactJSX}}).outputText,{
  module:m,exports:m.exports,require:k=>k==='./ui/button'?{Button:({children,...p})=>React.createElement('button',p,children)}:k==='./ui/skeleton'?{Skeleton:p=>React.createElement('div',p)}:k==='@/hooks/use-app-motion'?{useAppMotion:()=>({reduced:true})}:require(k),Date,
});
const render=resource=>renderToStaticMarkup(React.createElement(m.exports.ResourceFeedback,{resource:{refresh:()=>{},...resource},label:'Loading public reports',skeleton:true}));
test('initial HTML includes polite loading content and decorative reduced-motion skeletons',()=>{
  const html=render({pending:true,loaded:false,error:''});
  assert.match(html,/role="status" aria-live="polite"/);assert.match(html,/Loading public reports…/);
  assert.match(html,/aria-hidden="true" aria-busy="true"/);assert.match(html,/resource-no-motion/);
  assert.doesNotMatch(html,/No reports|0 reports|Retry/);
});
test('initial failures offer Retry, refresh failures identify retained content, and success removes feedback',()=>{
  assert.match(render({pending:false,loaded:false,error:'Unavailable'}),/Could not load public reports/);
  assert.match(render({pending:false,loaded:false,error:'Unavailable'}),/>Retry<\/button>/);
  assert.match(render({pending:false,loaded:true,error:'Unavailable'}),/Could not refresh public reports/);
  assert.equal(render({pending:false,loaded:true,error:''}),'');
});
