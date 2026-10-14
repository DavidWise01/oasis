/** OASIS FINAL SIX: six explicit acceptance gates, no endless cycling.
 * Additive verification only; frozen KET, {{i}}, OBS and dual5 untouched.
 * Truthful statuses: PASS (scope proved), GAP (requirement fails), PARTIAL (some proved).
 */
import assert from 'node:assert/strict';
import net from 'node:net';
import {spawn} from 'node:child_process';
import {writeFileSync} from 'node:fs';
import {setTimeout as delay} from 'node:timers/promises';
import {I42,CANONICAL,parse,route,unroute} from '../iso-graded-chain-v1.9c.mjs';
import * as d from '../diatom.mjs';
import {SOURCE} from '../astrophage-field-v2.0.mjs';
import {encodeDualBytes,decodeDualBytes,encodeField,decodeField} from '../astrophage-compact-v2.1.mjs';
const BASE=new URL('../obf2-rust-dualtarget-v2.4/',import.meta.url);
const portNative=31650,portWasm=31651;
const records=[];
function record(number,name,status,evidence,unverified=[]){
 const obj={test:number,name,status,evidence,unverified};
 records.push(obj);
 console.log('FINAL_GATE '+JSON.stringify(obj));
}
async function start(command,args,ready){
 const p=spawn(command,args,{cwd:new URL('.',BASE),stdio:['ignore','pipe','pipe']});
 let stdout='',stderr='';
 const readyPromise=new Promise((res,rej)=>{
  const timer=setTimeout(()=>rej(new Error('server launch timeout '+stderr)),6000);
  p.stdout.on('data',buf=>{stdout+=buf; if(stdout.includes(ready)){clearTimeout(timer);res(p)}});
  p.stderr.on('data',buf=>stderr+=buf);
  p.once('exit',code=>{clearTimeout(timer);rej(new Error('server exited '+code+' '+stderr))});
 });
 await readyPromise;return p;
}
async function stop(p){
 if(!p||p.exitCode!==null)return;
 const ended=new Promise(resolve=>p.once('exit',resolve));
 p.kill('SIGTERM');
 await Promise.race([ended,delay(2000).then(()=>{p.kill('SIGKILL')})]);
}
async function call(port,frame){
 return await new Promise((resolve,reject)=>{
  const s=net.connect({host:'127.0.0.1',port});
  s.setNoDelay(true);s.setTimeout(4000);
  let buf=Buffer.alloc(0),complete=false;
  const fail=e=>{if(!complete){complete=true;s.destroy();reject(e)}};
  s.on('timeout',()=>fail(new Error('timeout')));
  s.on('error',fail);
  s.on('connect',()=>{
   const h=Buffer.alloc(4);h.writeUInt32BE(frame.length,0);
   s.write(Buffer.concat([h,frame]));
  });
  s.on('data',chunk=>{
   buf=Buffer.concat([buf,chunk]);
   if(buf.length>=5){
    const len=buf.readUInt32BE(1);
    if(len>131088){fail(new Error('oversized response'));return}
    if(buf.length>=5+len&&!complete){
      complete=true;const status=buf[0],body=Buffer.from(buf.subarray(5,5+len));
      s.end();resolve({status,body});
    }
   }
  });
 });
}
let native,wasm;
try {
 // 1. Math/identity: exactly 42 coordinate-distinct identities, 8 views, canonical chain.
 assert.equal(I42.length,42);
 assert.equal(new Set(I42.map(t=>t.id)).size,42);
 const chain=parse(CANONICAL);
 assert.deepEqual(chain.identityOccurrences,[0,4]);
 assert.deepEqual(chain.edges.map(e=>e.depth),[1,2,3,4,5]);
 assert.equal(chain.arithmetic.value,729);
 assert.notEqual(I42.find(t=>t.id==='i6:3').id,I42.find(t=>t.id==='i7:4').id);
 assert.equal(I42.find(t=>t.id==='i6:3').glyph,'0');
 assert.equal(I42.find(t=>t.id==='i7:4').glyph,'0');
 for(const token of I42)for(let source=0;source<8;source++)for(let target=0;target<8;target++){
  const pkt=route(token.id,source,target);
  assert.equal(unroute(pkt),token.id);
  assert.equal(pkt.sourceView,source);
  assert.equal(pkt.targetView,target);
 }
 record(1,'{{i}} identity + six-node relation','PASS','42 unique coordinates, 8 views, 2688 directed transitions; both 0 glyphs and both {{i}} positions preserved');

 // 2. Diamond carrier: lossless full registry through all views, no mutated frozen mapping.
 const ids=I42.map(x=>x.id);
 for(let source=0;source<8;source++)for(let target=0;target<8;target++){
  const packed=d.project(d.encode(ids,source),target);
  const restored=d.deserialize(d.serialize(packed));
  assert.deepEqual(d.decode(restored),ids);
  assert.equal(restored.sourceView,source);
  assert.equal(restored.view,target);
 }
 record(2,'{{d}} 4/3 reversible carrier','PASS','42 original addresses survive all source/target view combinations without collisions or reordered cells');

 native=await start('./kernel_native',['serve',String(portNative)],'READY rust-native');
 wasm=await start(process.execPath,['host.mjs','serve',String(portWasm)],'READY rust-wasm');
 // 3. Field + native/WASM interoperability and accidental-corruption rejection.
 const field=encodeField(SOURCE);
 assert.equal(field.length,444);
 assert.equal(decodeField(field),SOURCE);
 for(const port of [portNative,portWasm]){
  const reply=await call(port,field);
  assert.equal(reply.status,0);assert.deepEqual(reply.body,field);
  assert.equal(decodeField(reply.body),SOURCE);
  const bad=Buffer.from(field);bad[16]^=1;
  const invalid=await call(port,bad);
  assert.equal(invalid.status,1);
 }
 record(3,'ASTROPHAGE / OBF2 native ↔ WASM interoperability','PASS','444-byte canonical frame exact round-trip through both separate TCP processes; corrupt frames rejected');

 // 4. Real authentication is absent in existing OBF2; demonstrate a fully valid forgery accepted.
 const forged=encodeDualBytes(Buffer.from('SPOOFED FROM SOMEONE ELSE','utf8'));
 const accepted=await call(portNative,forged);
 assert.equal(accepted.status,0);
 assert.deepEqual(decodeDualBytes(accepted.body),Buffer.from('SPOOFED FROM SOMEONE ELSE'));
 record(4,'Authenticated source and provenance','GAP','A frame with a valid CRC and two matching rails is accepted without any sender credentials; source identity and factual truth are not authenticated',['Add explicit sender authentication above frozen OBF2 before production']);

 // 5. Restart case: stateless message reprocessing, not durable exactly-once delivery.
 const initial=await call(portNative,field);assert.equal(initial.status,0);
 await stop(native);native=undefined;
 native=await start('./kernel_native',['serve',String(portNative)],'READY rust-native');
 const resumed=await call(portNative,field);assert.equal(resumed.status,0);
 assert.deepEqual(resumed.body,initial.body);
 record(5,'Disconnect / process restart / recovery','PARTIAL','Fresh process accepts exact same field after server restart; stateless recovery verified',['No persisted ACK, durable commit record, duplicate suppression or exactly-once semantics verified']);

 // 6. Controlled concurrent clients, bounds, end-to-end provenance is not validated remotely.
 const clients=12;
 const replies=await Promise.all(Array.from({length:clients},()=>call(portNative,field)));
 for(const p of replies){assert.equal(p.status,0);assert.deepEqual(p.body,field)}
 // Oversized wire rejects by protocol framing, separately open single socket.
 const oversized=Buffer.alloc(4);oversized.writeUInt32BE(131089,0);
 const refused=await call(portNative,oversized);assert.equal(refused.status,1);
 record(6,'Integrated bounded-traffic and end-to-end acceptance','PARTIAL',
  '12 concurrent localhost connections returned exact 444-byte frame; oversized frame rejected',['Not tested on two independent devices or with controlled cross-host latency/loss; overall production trust/recovery blockers remain']);
} catch(e) {
 const expected=records.length+1;
 record(expected,['','{{i}} identity','{{d}} carrier','field transport','authentication','recovery','end-to-end'][expected]||'unknown','FAIL',String(e?.stack||e));
} finally {
 await Promise.allSettled([stop(native),stop(wasm)]);
 const statuses=Object.fromEntries(records.map(x=>[x.test,x.status]));
 const complete=records.length===6;
 const final=complete&&records.every(x=>x.status==='PASS')?'READY':'HOLD';
 const summary={release:'OASIS-FINAL-SIX-v1',suiteExecution:complete&&records.every(x=>x.status!=='FAIL')?'PASS':'FAIL',
  productionDecision:final,completedGates:records.length,results:records,
  frozenChanges:0,notes:'PASS is limited to explicit scope. PARTIAL and GAP block production READY.'};
 writeFileSync(new URL('./final-six-results.json',import.meta.url),JSON.stringify(summary,null,2)+'\n');
 console.log('FINAL_SIX_SUMMARY '+JSON.stringify({suiteExecution:summary.suiteExecution,productionDecision:final,completedGates:records.length,statuses}));
 if(!complete||records.some(x=>x.status==='FAIL'))process.exitCode=1;
}
