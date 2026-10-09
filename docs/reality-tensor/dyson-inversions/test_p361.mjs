import assert from 'node:assert/strict';
import {mkdtemp,rm} from 'node:fs/promises';import {join} from 'node:path';import {tmpdir} from 'node:os';
import {keypair,verifyVote} from './p359_witness.mjs';import {CrashWitness,STAGES} from './p361_crash.mjs';
let assertions=0;function check(b){assert.ok(b);assertions++;}
const kp=keypair(),keys=new Map([['w0',kp.publicKey]]);
const cp=h=>({context:'oasis/main',epoch:9,length:1440,head:h.repeat(64)});
const report=[];
for(const stage of STAGES){const dir=await mkdtemp(join(tmpdir(),'p361-'));
 try{const w=new CrashWitness(dir,keys);await assert.rejects(w.vote('w0',cp('a'),kp.privateKey,{crashAt:stage}),/INJECTED:/);assertions++;
  const restarted=new CrashWitness(dir,keys),inspection=await restarted.inspect('w0',cp('a'));
  const conflict=await restarted.vote('w0',cp('b'),kp.privateKey);check(!conflict.ok&&conflict.reason==='double-vote');
  const same=await restarted.vote('w0',cp('a'),kp.privateKey);
  if(stage==='committed'){check(inspection.status==='committed');check(same.ok&&same.duplicate&&verifyVote(same.vote,keys));}
  else{check(inspection.status==='quarantined');check(!same.ok&&same.reason==='reserved-pending-recovery');}
  const next=await restarted.vote('w0',{...cp('c'),epoch:10},kp.privateKey);check(next.ok&&verifyVote(next.vote,keys));
  report.push({stage,inspection:inspection.status,conflictRejected:true});
 }finally{await rm(dir,{recursive:true,force:true});}}
console.log(JSON.stringify({status:'PASS',assertions,scenarios:STAGES.length,report},null,2));