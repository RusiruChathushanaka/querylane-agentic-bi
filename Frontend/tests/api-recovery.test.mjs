import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import vm from 'node:vm';
import ts from 'typescript';

function harness(handler, cached, configuration = {backend_url:'https://backend.test'}) {
  const values = new Map(cached ? [['bi-guest', cached]] : []);
  const compiledModule = { exports: {} };
  const requests = [];
  const context = {
    module: compiledModule, exports: compiledModule.exports,
    require: () => ({}), Headers, Response, TextDecoder, AbortSignal, AbortController, DOMException,
    sessionStorage: { getItem: k => values.get(k), setItem: (k,v) => values.set(k,v), removeItem: k => values.delete(k) },
    fetch: async (url, init) => {
      requests.push({url,init});
      if (url === '/api/config') return configuration instanceof Response ? configuration.clone() : Response.json(configuration);
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


test('initial reads retry one transient failure, but never replay ordinary background GETs', async () => {
  for (const status of [0,408,502,503,504]) {
    let reads=0;
    const h=harness(() => {
      if (++reads===1) {
        if (!status) throw new TypeError('connection interrupted');
        return new Response('',{status});
      }
      return Response.json({ok:true});
    });
    assert.equal((await h.initialRead(() => h.api('/history'),new AbortController().signal)).ok,true);
    assert.equal(reads,2);
  }
  const failed=harness(() => new Response('',{status:502}));
  await assert.rejects(failed.initialRead(() => failed.api('/history'),new AbortController().signal));
  assert.equal(failed.requests.filter(r=>r.url.endsWith('/history')).length,2);
  await assert.rejects(failed.api('/background'));
  assert.equal(failed.requests.filter(r=>r.url.endsWith('/background')).length,1);
});

test('initial reads do not replay rate limits, invalid bodies, permission failures or aborted requests', async () => {
  for(const status of [400,401,403,404,429]) {
    const h=harness(() => new Response('',{status,headers:{'Retry-After':'9'}}));
    await assert.rejects(h.initialRead(()=>h.api('/data',{},false),new AbortController().signal));
    assert.equal(h.requests.filter(r=>r.url.endsWith('/data')).length,1);
  }
  const h=harness(() => new Response('invalid',{status:200}));
  await assert.rejects(h.initialRead(()=>h.api('/data'),new AbortController().signal));
  assert.equal(h.requests.length,2); // configuration + a single invalid response
  const controller=new AbortController();controller.abort();
  let count=0;
  await assert.rejects(h.initialRead(async()=>{count++;throw new h.ApiError('offline',0);},controller.signal));
  assert.equal(count,1);
});

test('bootstrap guest authentication does not acquire a new session again after an ambiguous POST', async () => {
  let sessions=0;
  const h=harness(url=>{if(url.endsWith('/guest-sessions')) {sessions++;throw new TypeError('lost');} return Response.json({});});
  await assert.rejects(h.initialRead(()=>h.guestApi('/dashboard-builds'),new AbortController().signal));
  assert.equal(sessions,1);
});

test('Retry-After parsing preserves server deadlines and rate-limit errors expose them', async () => {
  const h=harness(()=>new Response('',{status:429,headers:{'Retry-After':'12'}}));
  assert.equal(h.retryDelay('12'),12000);
  assert.equal(h.retryDelay('invalid'),undefined);
  assert.ok(h.retryDelay(new Date(Date.now()+20000).toUTCString())>18000);
  await assert.rejects(h.api('/data'),e=>e.status===429 && e.retryAfter===12000);
});


test('invalid runtime configuration fails explicitly without contacting a backend',async()=>{
  const h=harness(()=>{throw new Error('must not fetch backend');},undefined,{backend_url:'javascript:unsafe'});
  await assert.rejects(h.initialRead(()=>h.api('/history'),new AbortController().signal),e=>e.code==='configuration_unavailable');
  assert.equal(h.requests.length,1);assert.equal(h.requests[0].url,'/api/config');
});

test('initial timeout uses the single retry while caller cancellation prevents another attempt',async()=>{
  const h=harness(()=>Response.json({}));let calls=0;
  assert.equal(await h.initialRead(async()=>{if(++calls===1)throw new h.ApiError('Timed out',504,'request_timeout');return 'ready';},new AbortController().signal),'ready');
  assert.equal(calls,2);
  const controller=new AbortController();calls=0;
  await assert.rejects(h.initialRead(async()=>{calls++;controller.abort();throw new h.ApiError('Timed out',504);},controller.signal));
  assert.equal(calls,1);
});
