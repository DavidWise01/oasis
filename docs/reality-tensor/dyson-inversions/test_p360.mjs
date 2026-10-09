import assert from 'node:assert/strict';
import {mkdtemp,rm} from 'node:fs/promises';
import {tmpdir} from 'node:os';import {join} from 'node:path';
import {keypair,verifyVote} from './p359_witness.mjs';
import {AtomicWitness} from './p360_atomic.mjs';
const dir=await mkdtemp(join(tmpdir(),'root0-p360-'));let checks=0;
try{
 const kp=keypair(),keys=new Map([['w0',kp.publicKey]]),cp=h=>({context:'oasis/main',epoch:7,length:1440,head:h.repeat(64)});
 const attempts=await Promise.all(Array.from({length:64},(_,i)=>new AtomicWitness(dir,keys).vote('w0',cp(i%2?'b':'a'),kp.privateKey)));
 const winners=attempts.filter(x=>x.ok&&!x.duplicate);assert.equal(winners.length,1);checks++;
 assert.ok(verifyVote(winners[0].vote,keys));checks++;
 const h=winners[0].vote.checkpoint.head[0],restored=new AtomicWitness(dir,keys);
 const again=await restored.vote('w0',cp(h),kp.privateKey);assert.equal(again.ok,true);assert.equal(again.duplicate,true);checks++;
 assert.equal((await restored.vote('w0',cp(h==='a'?'b':'a'),kp.privateKey)).reason,'double-vote');checks++;
 assert.equal((await restored.vote('w0',{...cp('c'),epoch:8},kp.privateKey)).ok,true);checks++;
 assert.ok(attempts.some(x=>x.ok));checks++;
 console.log(JSON.stringify({status:'PASS',checks,parallelAttempts:64,firstSignatures:winners.length,conflictsRejected:attempts.filter(x=>x.reason==='double-vote').length,restartRecovered:true}));
}finally{await rm(dir,{recursive:true,force:true});}