import assert from 'node:assert/strict';
import {mkdtemp,mkdir,readdir,rm,writeFile,readFile,unlink} from 'node:fs/promises';
import {tmpdir} from 'node:os';import {join} from 'node:path';
import {keypair,fingerprint} from './p359_witness.mjs';
import {CrashWitness} from './p361_crash.mjs';
import {AnchoredWitness} from './p365_anchor.mjs';
let assertions=0;const cp=c=>({context:'oasis/main',epoch:15,length:1440,head:c.repeat(64)});
const kp=keypair(),keys=new Map([['w0',kp.publicKey]]),report=[];
for(const mode of ['deleted','truncated','empty','bad-digest','bad-signature','stale-pending']){
 const root=await mkdtemp(join(tmpdir(),'root0-p365-')),primary=join(root,'primary'),anchor=join(root,'anchor');
 try{await mkdir(primary);await mkdir(anchor);
  const anchorPath=join(anchor,Buffer.from('w0|oasis/main|15').toString('hex')+'.json');
  await writeFile(anchorPath,JSON.stringify({id:'w0',digest:fingerprint(cp('a'))}));
  const w=new CrashWitness(primary,keys);await assert.rejects(w.vote('w0',cp('a'),kp.privateKey,{crashAt:'committed'}));assertions++;
  const name=(await readdir(primary)).find(x=>x.endsWith('.json')),path=join(primary,name);
  if(mode==='deleted')await unlink(path);
  if(mode==='truncated')await writeFile(path,'{"id":"w0"');
  if(mode==='empty')await writeFile(path,'');
  if(mode==='bad-digest'){const o=JSON.parse(await readFile(path,'utf8'));o.digest='0'.repeat(64);await writeFile(path,JSON.stringify(o));}
  if(mode==='bad-signature'){const o=JSON.parse(await readFile(path,'utf8'));o.vote.signature='invalid';await writeFile(path,JSON.stringify(o));}
  if(mode==='stale-pending')await writeFile(path+'.pending','partial');
  const store=new AnchoredWitness(primary,anchor,keys);
  const result=await store.vote('w0',cp('b'),kp.privateKey);
  assert.equal(result.ok,false);assert.equal(result.reason,'anchor-conflict');assertions+=2;
  const same=await store.vote('w0',cp('a'),kp.privateKey);
  assert.equal(mode==='stale-pending',same.ok===true);assertions++;
  const fresh=await store.vote('w0',{...cp('c'),epoch:16},kp.privateKey);assert.equal(fresh.ok,true);assertions++;
  const freshConflict=await store.vote('w0',{...cp('d'),epoch:16},kp.privateKey);assert.equal(freshConflict.ok,false);assertions++;
  report.push({mode,conflictingVoteRejected:true,recovery:same.reason??'duplicate',freshEpochSigned:true});
 }finally{await rm(root,{recursive:true,force:true});}
}
console.log(JSON.stringify({status:'PASS',assertions,report},null,2));
