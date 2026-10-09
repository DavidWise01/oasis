import assert from 'node:assert/strict';
import {mkdtemp,rm,readFile,writeFile,unlink,readdir} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {keypair} from './p359_witness.mjs';
import {CrashWitness} from './p361_crash.mjs';
const {publicKey,privateKey}=keypair();const keys=new Map([['w0',publicKey]]);
const cp=x=>({context:'oasis/main',epoch:15,length:1440,head:x.repeat(64)});
const outcomes=[];let assertions=0;
async function scenario(name,damage){
 const dir=await mkdtemp(join(tmpdir(),'p364-'));
 try{
  const witness=new CrashWitness(dir,keys);
  await assert.rejects(witness.vote('w0',cp('a'),privateKey,{crashAt:'committed'}),/INJECTED/);assertions++;
  const filename=(await readdir(dir)).find(f=>f.endsWith('.json'));
  const path=join(dir,filename);await damage(path);
  const result=await new CrashWitness(dir,keys).vote('w0',cp('b'),privateKey);
  outcomes.push({name,conflictingVoteAccepted:!!result.ok,reason:result.reason??null});
  assert.equal(!!result.ok,name==='missing-reservation');assertions++;
 }finally{await rm(dir,{recursive:true,force:true});}
}
await scenario('truncated-json',p=>writeFile(p,'{"id":"w0"'));
await scenario('empty-file',p=>writeFile(p,''));
await scenario('bad-digest',async p=>{const o=JSON.parse(await readFile(p,'utf8'));o.digest='0'.repeat(64);await writeFile(p,JSON.stringify(o));});
await scenario('bad-signature',async p=>{const o=JSON.parse(await readFile(p,'utf8'));o.vote.signature='invalid';await writeFile(p,JSON.stringify(o));});
await scenario('stale-pending',p=>writeFile(p+'.pending','partial'));
await scenario('missing-reservation',p=>unlink(p));
console.log(JSON.stringify({status:'PASS_WITH_CRITICAL_GAP',assertions,outcomes},null,2));