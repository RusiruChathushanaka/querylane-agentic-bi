import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import vm from 'node:vm';
import ts from 'typescript';

const compiled=ts.transpileModule(readFileSync(new URL('../src/hooks/use-read-resource.ts',import.meta.url),'utf8'),{compilerOptions:{module:ts.ModuleKind.CommonJS,target:ts.ScriptTarget.ES2022}}).outputText;
const deferred=()=>{let resolve,reject;const promise=new Promise((a,b)=>{resolve=a;reject=b;});return {promise,resolve,reject};};
const flush=async()=>{for(let i=0;i<6;i++)await Promise.resolve();};
function harness() {
  let index=0,effects=[],pending=[],interval;
  const cells=[];
  const same=(a,b)=>a&&b&&a.length===b.length&&a.every((v,i)=>v===b[i]);
  const react={
    useRef:value=>{const i=index++;cells[i]??={current:value};return cells[i];},
    useState:value=>{const i=index++;if(!(i in cells))cells[i]=value;return [cells[i],next=>{cells[i]=typeof next==='function'?next(cells[i]):next;}];},
    useCallback:(fn,deps)=>{const i=index++;if(!cells[i]||!same(cells[i].deps,deps))cells[i]={fn,deps};return cells[i].fn;},
    useEffect:(fn,deps)=>{const i=index++;if(!effects[i]||!same(effects[i].deps,deps))pending.push(()=>{effects[i]?.cleanup?.();effects[i]={deps,cleanup:fn()};});},
  };
  class ApiError extends Error {constructor(message,retryAfter){super(message);this.retryAfter=retryAfter;}}
  const m={exports:{}};
  vm.runInNewContext(compiled,{module:m,exports:m.exports,require:k=>k==='react'?react:{ApiError,initialRead:task=>task()},AbortController,Date,Error,document:{hidden:false},setInterval:fn=>(interval=fn,1),clearInterval:()=>{interval=undefined;}});
  return {ApiError,render(key,read,commit=()=>{},poll=0){index=0;const v=m.exports.useReadResource(key,read,commit,poll);const tasks=pending;pending=[];tasks.forEach(fn=>fn());return v;},poll:()=>interval?.(),unmount:()=>effects.forEach(e=>e?.cleanup?.())};
}

test('independent resources reveal whichever finishes first and distinguish pending from empty',async()=>{
  const history=harness(),sources=harness(),h=deferred(),s=deferred();let rows;
  const readH=()=>h.promise,readS=()=>s.promise,commit=v=>{rows=v;};
  assert.equal(history.render('history',readH,commit).loaded,false);
  sources.render('sources',readS);
  h.resolve([]);await flush();
  assert.deepEqual(rows,[]);
  assert.equal(history.render('history',readH,commit).loaded,true);
  assert.equal(sources.render('sources',readS).pending,true);
  sources.unmount();history.unmount();
});

test('manual retry replaces pending reads; stale responses and unmounted requests cannot commit',async()=>{
  const h=harness(),a=deferred(),b=deferred();const pending=[a,b];let calls=0,values=[],signals=[];
  const read=signal=>{signals.push(signal);return pending[calls++].promise;},commit=v=>values.push(v);
  h.render('report',read,commit);
  h.render('report',read,commit).refresh();
  assert.equal(signals[0].aborted,true);
  a.resolve('obsolete');b.resolve('current');await flush();
  assert.deepEqual(values,['current']);
  const late=deferred();h.render('different',()=>late.promise,commit);h.unmount();late.resolve('abandoned');await flush();
  assert.deepEqual(values,['current']);
});

test('polling skips initial and refresh work and background failure retains successful content',async()=>{
  const h=harness(),a=deferred(),b=deferred();let calls=0,values=[];
  const read=()=>[a,b][calls++].promise,commit=v=>values.push(v);
  h.render('library',read,commit,5000);h.poll();h.poll();assert.equal(calls,1);
  a.resolve(['saved']);await flush();h.poll();h.poll();assert.equal(calls,2);
  b.reject(new Error('offline'));await flush();
  const state=h.render('library',read,commit,5000);
  assert.equal(state.loaded,true);assert.equal(state.pending,false);assert.equal(state.error,'offline');
  assert.deepEqual(values,[['saved']]);h.unmount();
});

test('rate-limit cooldown applies to both manual retry and polling',async()=>{
  const h=harness();let calls=0;
  const read=async()=>{calls++;throw new h.ApiError('Wait',60000);};
  h.render('limited',read,()=>{},5000);await flush();
  const state=h.render('limited',read,()=>{},5000);
  assert.ok(state.retryAt>Date.now());state.refresh();h.poll();await flush();assert.equal(calls,1);h.unmount();
});


test('an initial failure stops automatic polling until a deliberate retry',async()=>{
  const h=harness();let calls=0;
  const read=async()=>{calls++;throw new Error('offline');};
  h.render('failed',read,()=>{},5000);await flush();h.poll();h.poll();await flush();assert.equal(calls,1);
  h.render('failed',read,()=>{},5000).refresh();await flush();assert.equal(calls,2);h.unmount();
});
