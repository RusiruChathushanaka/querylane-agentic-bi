import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import vm from 'node:vm';
import ts from 'typescript';

function harness(handler, cached) {
  const values = new Map(cached ? [['bi-guest', cached]] : []);
  const compiledModule = { exports: {} };
  const requests = [];
  const context = {
    module: compiledModule, exports: compiledModule.exports,
    require: () => ({}), Headers, Response, TextDecoder, AbortSignal, AbortController,
    sessionStorage: { getItem: k => values.get(k), setItem: (k,v) => values.set(k,v), removeItem: k => values.delete(k) },
    fetch: async (url, init) => {
      requests.push({url,init});
      if (url === '/api/config') return Response.json({backend_url:'https://backend.test'});
      return handler(url,init,requests);
    },
    setTimeout: (fn, ms) => { if (ms < 30000) queueMicrotask(fn); return 1; }, clearTimeout() {},
  };
  const {outputText} = ts.transpileModule(readFileSync(new URL('../src/lib/api.ts',import.meta.url),'utf8'), {
    compilerOptions:{module:ts.ModuleKind.CommonJS,target:ts.ScriptTarget.ES2022},
  });
  vm.runInNewContext(outputText,context);
  return {...compiledModule.exports,requests};
}

test('corrupt saved guest credentials recover before a mutation', async () => {
  let guests=0;
  const h=harness((url) => url.endsWith('guest-sessions')
    ? (guests++,Response.json({token:'fresh',expires_in:3600})) : Response.json({ok:true}), '{broken');
  assert.equal((await h.api('/test',{method:'POST'})).ok,true);
  assert.equal(guests,1);
});

test('non-JSON gateway failures retain HTTP status and safe actionable error', async () => {
  const h=harness(() => new Response('<html>private upstream detail</html>',{status:503}));
  await assert.rejects(h.api('/test'),error => error.status===503 && !error.message.includes('private'));
});

test('mutations are never automatically replayed for network ambiguity', async () => {
  let writes=0;
  const h=harness(url => {
    if(url.endsWith('guest-sessions'))return Response.json({token:'fresh',expires_in:3600});
    writes++;throw new TypeError('connection reset');
  });
  await assert.rejects(h.api('/test',{method:'POST'}));
  assert.equal(writes,1);
});

test('a stream ending repeatedly while its run is active surfaces reconnect exhaustion', async () => {
  let connects=0;
  const h=harness(url => url.includes('/events?') ? (connects++,new Response('')) : Response.json({status:'running'}));
  await assert.rejects(h.streamRun('run',new AbortController().signal,()=>{}),/reconnect|interrupted|connection/i);
  assert.equal(connects,4);
});

test('stream reconnection replays only after the last successfully delivered cursor', async () => {
  let connects=0;const seen=[];
  const h=harness(url => {
    if(url.includes('/events?')){
      connects++;
      assert.ok(url.endsWith(connects===1?'after=0':'after=1'));
      return new Response(connects===1?'id: 1\nevent: progress\ndata: {"message":"Query"}\n\n':'id: 2\nevent: complete\ndata: {}\n\n');
    }
    return Response.json({status:'running'});
  });
  await h.streamRun('run',new AbortController().signal,event=>{if(event.id)seen.push(event.id);});
  assert.deepEqual(seen,[1,2]);
});

test('concurrent stale 401s share refreshed credentials instead of evicting the new guest', async () => {
  let guests=0,release;
  const late=new Promise(resolve=>{release=resolve;});
  const h=harness(async(url,init)=>{
    if(url.endsWith('guest-sessions')){guests++;return Response.json({token:'new',expires_in:3600});}
    if(init.headers.get('Authorization')==='Bearer old'){
      if(url.endsWith('/two'))await late;
      return new Response('{}',{status:401});
    }
    if(url.endsWith('/one'))release();
    return Response.json({ok:true});
  },JSON.stringify({token:'old',expires:Date.now()+60000}));
  await Promise.all([h.api('/one',{method:'POST'}),h.api('/two',{method:'POST'})]);
  assert.equal(guests,1);
});

test('terminal status after stream EOF delivers a terminal event rather than silent success', async () => {
  const h=harness(url=>url.includes('/events?')?new Response(''):Response.json({status:'failed',error:'Saved source error'}));
  const events=[];
  await h.streamRun('run',new AbortController().signal,e=>events.push(e));
  assert.equal(events.at(-1).type,'error');
  assert.equal(events.at(-1).data.message,'Saved source error');
});
