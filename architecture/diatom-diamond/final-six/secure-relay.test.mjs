/* One bounded acceptance test for OASIS gates 4-6. No arbitrary stress loops.
 * The journal itself is the ONLY idempotent effect; remote exactly-once effects
 * are NOT guaranteed by a durable receipt. Keys generated solely for this test.
 */
import assert from 'node:assert/strict';
import {mkdtempSync,writeFileSync,readFileSync,copyFileSync,appendFileSync} from 'node:fs';
import {tmpdir} from 'node:os';
import path from 'node:path';
import {spawn} from 'node:child_process';
import {generateKeyPairSync} from 'node:crypto';
import {setTimeout as sleep} from 'node:timers/promises';
import {encodeField,decodeField,encodeDualBytes} from '../astrophage-compact-v2.1.mjs';
import {SOURCE} from '../astrophage-field-v2.0.mjs';
import {ReceiptJournal,signedEnvelope,submit} from './secure-relay.mjs';

const root=mkdtempSync(path.join(tmpdir(),'oasis-secure-'));
const publicKeyFile=path.join(root,'sender.pub.pem');
const journal=path.join(root,'commits.jsonl');
const {privateKey,publicKey}=generateKeyPairSync('ed25519');
const {privateKey:rogueKey}=generateKeyPairSync('ed25519');
writeFileSync(publicKeyFile,publicKey.export({type:'spki',format:'pem'}));
const original=encodeField(SOURCE);
assert.equal(original.length,444);
assert.equal(decodeField(original),SOURCE);
const port=process.env.OASIS_SECURE_PORT?Number(process.env.OASIS_SECURE_PORT):31989;
const result={tests:[],status:'PASS',gates:{4:'NOT VERIFIED',5:'NOT VERIFIED',6:'NOT VERIFIED'}};
let receiver=null;
const envelope=(id,frame=original,key=privateKey)=>signedEnvelope({sender:'OASIS_TEST',id,frame,privateKey:key});
function add(name,detail){result.tests.push({name,result:'PASS',detail});console.log('CHECK '+name+': '+detail)}
async function boot(crashId=null) {
  const args=[new URL('./secure-relay.mjs',import.meta.url).pathname,'serve',String(port),journal,publicKeyFile,'OASIS_TEST'];
  if(crashId)args.push(crashId);
  const proc=spawn(process.execPath,args,{stdio:['ignore','pipe','pipe']});
  let messages='';
  const ready=new Promise((resolve,reject)=>{
    const timer=setTimeout(()=>reject(new Error('receiver not ready: '+messages)),5000);
    proc.stdout.on('data',buf=>{messages+=buf;if(messages.includes('READY SECURE OBF2')){clearTimeout(timer);resolve()}});
    proc.stderr.on('data',buf=>{messages+=buf});
    proc.on('exit',code=>{clearTimeout(timer);reject(new Error('receiver exited before READY: '+code+' '+messages))});
  });
  await ready;receiver=proc;return proc;
}
async function shutdown(){if(!receiver||receiver.exitCode!==null)return;
 const proc=receiver;receiver=null;
 const stopped=new Promise(resolve=>proc.once('exit',resolve));proc.kill('SIGTERM');
 await Promise.race([stopped,sleep(1000).then(()=>proc.kill('SIGKILL'))]);
}
try{
 await boot();
 const e1=envelope('event-0001');
 const a1=await submit({port,envelope:e1});
 assert.equal(a1.status,'APPLIED'); assert.ok(/^[a-f0-9]{64}$/.test(a1.receipt));
 const d1=await submit({port,envelope:e1});
 assert.equal(d1.status,'DUPLICATE');assert.equal(d1.receipt,a1.receipt);
 add('G4-G5 authenticated initial commit and idempotent retransmission','durable receipt ACK and identical replay classified as duplicate');

 const spoof=await submit({port,envelope:envelope('fake-signer',original,rogueKey)});
 assert.equal(spoof.status,'REJECTED');
 const noSignature={...envelope('unsigned')};delete noSignature.sig;
 assert.equal((await submit({port,envelope:noSignature})).status,'REJECTED');
 const forged={...envelope('tampered')};forged.frame=encodeDualBytes(Buffer.from('ALTERNATE')).toString('base64');
 assert.equal((await submit({port,envelope:forged})).status,'REJECTED');
 const flipped=Buffer.from(original);flipped[18]^=1;
 assert.equal((await submit({port,envelope:envelope('crc-damaged',flipped)})).status,'REJECTED');
 const disagreement=await submit({port,envelope:envelope('event-0001',encodeDualBytes(Buffer.from('NEW CONTENT')))});
 assert.equal(disagreement.status,'CONFLICT');
 add('G4 reject forged, unsigned, altered, bad-CRC and conflicting events','all five negative classes rejected');
 result.gates[4]='PASS';

 await shutdown();
 await boot('crash-event');
 const crashEnvelope=envelope('crash-event');
 let observedLostAck=false;
 try{await submit({port,envelope:crashEnvelope,timeoutMs:3000})}
 catch{observedLostAck=true}
 assert.equal(observedLostAck,true);
 await shutdown();
 await boot();
 const recovered=await submit({port,envelope:crashEnvelope});
 assert.equal(recovered.status,'DUPLICATE');
 const verifyLog=readFileSync(journal,'utf8').split('\n').filter(Boolean).map(JSON.parse);
 assert.equal(verifyLog.filter(x=>x.id==='crash-event').length,1);
 const after=await submit({port,envelope:envelope('event-0001')});
 assert.equal(after.status,'DUPLICATE');assert.equal(after.receipt,a1.receipt);
 add('G5 kill after fsync before ACK and restart','replayed event has one durable receipt, no second application');

 await shutdown();
 appendFileSync(journal,'{"incomplete":');
 await boot();
 const tail=await submit({port,envelope:envelope('event-0001')});
 assert.equal(tail.status,'DUPLICATE');
 add('G5 truncated last journal record recovery','partial unacknowledged JSON tail discarded on restart');
 result.gates[5]='PASS';

 const many=await Promise.all(Array.from({length:12},(_,i)=>submit({port,envelope:envelope('concurrent-'+String(i).padStart(2,'0'))})));
 assert.equal(many.filter(x=>x.status==='APPLIED').length,12);
 assert.equal(new Set(many.map(x=>x.receipt)).size,12);
 add('G6 twelve concurrent clients','all 12 authenticated connections committed independently');

 await shutdown();
 const audit=new ReceiptJournal(journal);
 assert.equal(audit.size,14);
 const tip=audit.tip;audit.close();
 assert.ok(tip!=='0'.repeat(64));
 const invalid=path.join(root,'tampered.jsonl');copyFileSync(journal,invalid);
 const raw=readFileSync(invalid,'utf8');writeFileSync(invalid,raw.replace('event-0001','event-0002'));
 assert.throws(()=>new ReceiptJournal(invalid),/journal hash chain mismatch/);
 add('G5 journal consistency audit','14 unique durable receipt records; tampering prevented journal replay');

 const sample=readFileSync(new URL('../obf2-rust-dualtarget-v2.5/leanfast.wasm',import.meta.url));
 const {instance}=await WebAssembly.instantiate(sample);
 const {exports:x}=instance;
 const field=new TextEncoder().encode(SOURCE);
 new Uint8Array(x.memory.buffer).set(field,x.input_ptr());
 const len=x.encode(field.length);
 assert.equal(len,444);
 // Rust can grow WASM memory during first encode, invalidating old typed-array views.
 const frame=Buffer.from(new Uint8Array(x.memory.buffer).subarray(x.frame_ptr(),x.frame_ptr()+len));
 assert.deepEqual(frame,original);
 assert.equal(x.decode(len),field.length);
 add('G3 retained Rust WASM parity','bundled 23 KB balanced WASM produced the exact signed-message frame');
 result.gates[6]='PARTIAL';
 result.unverified=['The two communicating processes shared one physical host. No independent-device link, cross-host loss/jitter, or TLS channel has been established.',
   'Exactly-once durable receipt is not exactly-once arbitrary downstream external side effects.',
   'Public keys must be provisioned and rotated securely; this test creates disposable trust roots.'];
 result.appliedEvents=14;
 result.status='PASS_WITH_DEPLOYMENT_GAP';
} catch(error){result.status='FAIL';result.error=String(error.stack||error);process.exitCode=1}
finally{await shutdown();
 writeFileSync(new URL('./secure-relay-results.json',import.meta.url),JSON.stringify(result,null,2)+'\n');
 console.log('FINAL_NEXT_RESULT '+JSON.stringify({status:result.status,gates:result.gates,checks:result.tests.length,error:result.error||null}));
}
