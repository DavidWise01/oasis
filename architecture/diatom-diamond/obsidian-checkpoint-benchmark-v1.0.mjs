import assert from 'node:assert/strict';
import * as fs from 'node:fs';
import * as os from 'node:os';
import * as path from 'node:path';
import {newWitnessKeys,trustFromKeys,writeCheckpoint,readCheckpoints,recoverFinalization,quarantinePrepared,ROOT_HEAD} from './obsidian-checkpoint-v1.0.mjs';
import {assertFloor} from './quantum-dual.mjs';
const home=fs.mkdtempSync(path.join(os.tmpdir(),'obsidian-v1-')); const keys=newWitnessKeys(),trust=trustFromKeys(keys),badKeys=newWitnessKeys(),badTrust=trustFromKeys(badKeys);
let checks=0;
const ok=(x,m)=>{assert.ok(x,m);checks++};
const eq=(a,b,m)=>{assert.deepEqual(a,b,m);checks++};
const rejects=(fn,m)=>{assert.throws(fn,Error,m);checks++};
const inputs=['AaaA','555','∑','ZzzZ'];const dir=path.join(home,'checkpoints');
function load(stage,seq=1){return JSON.parse(fs.readFileSync(path.join(dir,String(seq).padStart(12,'0')+'.'+stage+'.json'),'utf8'))}
function put(stage,val,seq=1){fs.writeFileSync(path.join(dir,String(seq).padStart(12,'0')+'.'+stage+'.json'),JSON.stringify(val,null,2)+'\n')}
try{
 const floor=assertFloor();ok(floor.version==='0.7','floor frozen');
 eq(readCheckpoints(dir,trust).latest,null,'blank ledger');
 rejects(()=>writeCheckpoint(dir,{tokens:inputs,keys,trust:badTrust}),'wrong signer trust');
 rejects(()=>writeCheckpoint(dir,{tokens:inputs,keys:{alpha:keys.alpha,beta:keys.alpha},trust}),'one signer in two slots');
 // Window 1: prepared but not committed is never promoted.
 rejects(()=>writeCheckpoint(dir,{tokens:inputs,keys,trust,failpoint:'afterPrepare'}),'simulated prepared-only crash');
 let inspect=readCheckpoints(dir,trust);eq(inspect.latest,null,'prepare cannot become committed');eq(inspect.pending?.seq,1,'pending prepare present');
 rejects(()=>writeCheckpoint(dir,{tokens:inputs,keys,trust}),'blocked following uncommitted prepare');
 eq(quarantinePrepared(dir,trust).discarded,1,'explicit quarantine');
 eq(readCheckpoints(dir,trust).pending,null,'prepared stage moved');
 // Window 2: both-signed commit is recoverable, final marker needs signers.
 rejects(()=>writeCheckpoint(dir,{tokens:inputs,keys,trust,failpoint:'afterCommit'}),'simulated post-commit crash');
 inspect=readCheckpoints(dir,trust);
 eq(inspect.latest.seq,1,'committed checkpoint accepted');eq(inspect.latest.status,'COMMITTED_NOT_FINALIZED','recovery pending');
 rejects(()=>writeCheckpoint(dir,{tokens:inputs,keys,trust}),'no future write before finalization');
 rejects(()=>recoverFinalization(dir,trust,badKeys),'wrong finalizer keys');
 inspect=recoverFinalization(dir,trust,keys);eq(inspect.latest.status,'FINALIZED','recovered after commit');
 // Window 3: finalized checkpoint is read after crash on return path.
 rejects(()=>writeCheckpoint(dir,{tokens:['AaaA','11','ZzzZ'],noise:0.25,parent:'NEXT',generation:1,keys,trust,failpoint:'afterFinalize'}),'crash after finalized write');
 inspect=readCheckpoints(dir,trust);
 eq(inspect.latest.seq,2,'second checkpoint');eq(inspect.latest.status,'FINALIZED','finalized despite callback crash');
 eq(inspect.latest.record.prev,inspect.records[0].id,'hash chaining');
 ok(inspect.latest.record.coreWitness!==inspect.records[0].record.coreWitness,'core changed');
 // Third commit and strong out-of-band antirollback requirement.
 const third=writeCheckpoint(dir,{tokens:['AaaA','0','∞','∑','ZzzZ'],noise:.1,parent:'THIRD',generation:2,keys,trust});
 eq(readCheckpoints(dir,trust,{anchorHead:third.id,anchorSeq:3}).latest.id,third.id,'external trust anchor');
 rejects(()=>readCheckpoints(dir,badTrust),'untrusted public keys');
 // Replay and truncation simulation, anchored externally.
 const removed=[];
 for(const stage of ['prepare','commit','finalize']){const f=path.join(dir,'000000000003.'+stage+'.json');removed.push([f,fs.readFileSync(f)]);fs.unlinkSync(f)}
 rejects(()=>readCheckpoints(dir,trust,{anchorHead:third.id,anchorSeq:3}),'detect rollback with out-of-band pinned head');
 for(const [f,body] of removed)fs.writeFileSync(f,body);
 eq(readCheckpoints(dir,trust,{anchorHead:third.id}).latest.id,third.id,'restore anchored chain');
 // Faults exercised on isolated copies of a valid baseline.
 const baseline=fs.readdirSync(dir).map(name=>[name,fs.readFileSync(path.join(dir,name))]);
 function tamper(test,fn){
  const sandbox=path.join(home,'case'+checks);fs.mkdirSync(sandbox);
  for(const [name,bytes] of baseline)fs.writeFileSync(path.join(sandbox,name),bytes);
  fn(sandbox);rejects(()=>readCheckpoints(sandbox,trust),test);
 }
 tamper('modified token payload',sandbox=>{const p=path.join(sandbox,'000000000001.prepare.json');const x=JSON.parse(fs.readFileSync(p));x.record.tokens[0]='BbbB';fs.writeFileSync(p,JSON.stringify(x))});
 tamper('changed commit digest',sandbox=>{const p=path.join(sandbox,'000000000001.commit.json');const x=JSON.parse(fs.readFileSync(p));x.digest='0'.repeat(64);fs.writeFileSync(p,JSON.stringify(x))});
 tamper('replaced observer signature',sandbox=>{const p=path.join(sandbox,'000000000002.commit.json');const x=JSON.parse(fs.readFileSync(p));x.signatures.beta='notasignature';fs.writeFileSync(p,JSON.stringify(x))});
 tamper('altered core witness',sandbox=>{const p=path.join(sandbox,'000000000002.prepare.json');const x=JSON.parse(fs.readFileSync(p));x.record.coreWitness='a'.repeat(64);fs.writeFileSync(p,JSON.stringify(x))});
 tamper('reordered sequence',sandbox=>{const p=path.join(sandbox,'000000000002.prepare.json');const x=JSON.parse(fs.readFileSync(p));x.record.prev=ROOT_HEAD;fs.writeFileSync(p,JSON.stringify(x))});
 tamper('missing commit in middle',sandbox=>fs.unlinkSync(path.join(sandbox,'000000000002.commit.json')));
 tamper('forged finalize',sandbox=>{const p=path.join(sandbox,'000000000003.finalize.json');const x=JSON.parse(fs.readFileSync(p));x.signatures.alpha='junk';fs.writeFileSync(p,JSON.stringify(x))});
 tamper('wrong floor pinned digest',sandbox=>{const p=path.join(sandbox,'000000000003.prepare.json');const x=JSON.parse(fs.readFileSync(p));x.record.floorSha256='f'.repeat(64);fs.writeFileSync(p,JSON.stringify(x))});
 tamper('missing history',sandbox=>{for(const stage of ['prepare','commit','finalize'])fs.unlinkSync(path.join(sandbox,'000000000001.'+stage+'.json'))});
 tamper('unexpected temporary file',sandbox=>fs.writeFileSync(path.join(sandbox,'.unfinished'),'garbage'));
 // Sweep 32 diverse committed finite slices, including a 13-level state.
 const fresh=path.join(home,'sweep');let sweep=0;
 for(let n=2;n<=16;n++){
  const tokens=Array.from({length:n},(_,i)=>i%4===0?'AaaA':i%4===1?String(i*13):i%4===2?'∞':'ZzzZ');
  const w=writeCheckpoint(fresh,{tokens,noise:n/32,keys,trust,generation:n-2,parent:'SWEEP'});
  const r=readCheckpoints(fresh,trust);
  eq(r.latest.id,w.id,'sweep roundtrip '+n);eq(r.records.length,n-1,'sweep continuity '+n);sweep++;
 }
 for(let n=2;n<=16;n++){
  const keys2=newWitnessKeys(),trusted2=trustFromKeys(keys2),d=path.join(home,'noise'+n);
  const vals=Array.from({length:n},(_,i)=>'AaaA');
  writeCheckpoint(d,{tokens:vals,noise:n/16,keys:keys2,trust:trusted2});
  eq(readCheckpoints(d,trusted2).latest.record.tokens.length,n,'dimension sweep '+n);sweep++;
 }
 const report={status:'PASS',release:'{{i & dd}}/v1.0',floorSha256:floor.source,
   assertions:checks,sweeps:sweep,checkpointChain:3,committedHead:third.id,
   features:['Ed25519 two-distinct-key receipts','prepared/committed/finalized atomic files','fail-closed corruption handling','external rollback anchor','recovery of committed checkpoint','quarantine prepared-only state'],
   disclaimer:'Classical crypto + simulated quantum-state model; no physical quantum hardware or independent remote custody proven'};
 console.log(JSON.stringify(report,null,2));
} finally {fs.rmSync(home,{recursive:true,force:true})}