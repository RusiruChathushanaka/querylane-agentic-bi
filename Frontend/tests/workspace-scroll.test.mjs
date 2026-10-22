import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import vm from 'node:vm';
import ts from 'typescript';
const compile=path=>ts.transpileModule(readFileSync(new URL(path,import.meta.url),'utf8'),{compilerOptions:{module:ts.ModuleKind.CommonJS,target:ts.ScriptTarget.ES2022}}).outputText;
function harness(auto=true) {
  let index=0,frameId=0,resizeCallback;const cells=[],effects=[],setups=[],frames=new Map(),styles=new Map(),listeners=new Map();let disconnected=0;
  const react={useRef:v=>{const i=index++;return cells[i]??={current:v};},useState:v=>{const i=index++;cells[i]??=v;return[cells[i],n=>{cells[i]=n;}];},useCallback:f=>f,useEffect:f=>{setups.push(f);}};
  class ResizeObserver {constructor(f){resizeCallback=f;} observe(){} disconnect(){disconnected++;}}
  const viewport={height:360,offsetTop:20,scale:1,addEventListener:(k,f)=>listeners.set('viewport:'+k,f),removeEventListener:k=>listeners.delete('viewport:'+k)};
  const win={innerWidth:390,visualViewport:viewport,addEventListener:(k,f)=>listeners.set('window:'+k,f),removeEventListener:k=>listeners.delete('window:'+k)};
  const m={exports:{}};
  vm.runInNewContext(compile('../src/hooks/use-workspace-scroll.ts'),{module:m,exports:m.exports,require:()=>react,ResizeObserver,window:win,requestAnimationFrame:f=>{frames.set(++frameId,f);return frameId;},cancelAnimationFrame:id=>frames.delete(id)});
  const result=m.exports.useWorkspaceScroll(auto);
  result.scroller.current={scrollTop:20,scrollHeight:2000,clientHeight:500};
  result.shell.current={style:{setProperty:(k,v)=>styles.set(k,v),removeProperty:k=>styles.delete(k)}};
  setups.forEach(f=>effects.push(f()));
  return{result,frames,styles,listeners,viewport,win,resize:()=>resizeCallback(),flush:()=>{for(const [id,f]of frames){frames.delete(id);f();}},cleanup:()=>effects.forEach(f=>f?.()),disconnected:()=>disconnected};
}
test('chat scroll targets only its container and coalesces resize frames',()=>{
 const h=harness();h.result.registerBottom({parentElement:{}});h.resize();h.resize();assert.equal(h.frames.size,1);h.flush();assert.equal(h.result.scroller.current.scrollTop,2000);h.cleanup();
});
test('reading older messages survives growth; explicit jump resumes following',()=>{
 const h=harness();h.result.pauseFollowing();h.result.registerBottom({parentElement:{}});h.resize();assert.equal(h.frames.size,0);assert.equal(h.result.scroller.current.scrollTop,20);h.result.jumpToLatest();h.flush();assert.equal(h.result.scroller.current.scrollTop,2000);h.cleanup();
});
test('manual jump works with auto follow off; cleanup cancels pending work',()=>{
 const h=harness(false);h.result.registerBottom({parentElement:{}});assert.equal(h.frames.size,0);h.result.jumpToLatest();assert.equal(h.frames.size,1);h.cleanup();assert.equal(h.frames.size,0);assert.ok(h.disconnected()>0);
});
test('unchanged JSON keeps state identity; message edits are committed',()=>{
 const m={exports:{}};vm.runInNewContext(compile('../src/lib/read-equality.ts'),{module:m,exports:m.exports});
 const previous=[{id:'one',text:'saved',followups:['next']}];assert.equal(m.exports.retainEqualRead(previous,JSON.parse(JSON.stringify(previous))),previous);
 const edited=[{id:'one',text:'changed'}];assert.equal(m.exports.retainEqualRead(previous,edited),edited);
});

test('narrow keyboard viewport follows height and offset, preserves zoom and removes listeners',()=>{
 const h=harness();assert.equal(h.styles.get('--workspace-viewport-height'),'360px');assert.equal(h.styles.get('--workspace-viewport-offset'),'20px');
 h.viewport.height=280;h.listeners.get('viewport:resize')();assert.equal(h.styles.get('--workspace-viewport-height'),'280px');
 h.viewport.scale=2;h.listeners.get('viewport:resize')();assert.equal(h.styles.size,0);
 h.cleanup();assert.equal(h.listeners.size,0);assert.equal(h.styles.size,0);
});
