import assert from 'node:assert/strict';
import {mkdtemp,mkdir,rm,readdir,writeFile,unlink} from 'node:fs/promises';
import {tmpdir} from 'node:os'; import {join} from 'node:path';
import {keypair,fingerprint} from './p359_witness.mjs';
import {AnchoredWitness} from './p365_anchor.mjs';
const kp=keypair(),keys=new Map([['w0',kp.publicKey]]);
const cp=(head,epoch=15)=>({context:'oasis/main',epoch,length:1440,head:head.repeat(64)});
let assertions=0; const scenarios=[];
for(const mode of ['both-deleted','anchor-deleted','anchor-corrupt','primary-corrupt','both-corrupt','anchor-rollback','both-rollback','both-directories-deleted']) {
 const root=await mkdtemp(join(tmpdir(),'p366-')),primary=join(root,'primary'),anchor=join(root,'anchor');
 try {
  await mkdir(primary); await mkdir(anchor);
  const w=new AnchoredWitness(primary,anchor,keys);
  const original=await w.vote('w0',cp('a'),kp.privateKey);
  assert.equal(original.ok,true); assertions++;
  const anchorFile=join(anchor,(await readdir(anchor))[0]);
  const primaryFile=join(primary,(await readdir(primary)).find(n=>n.endsWith('.json')));
  if(['both-deleted','anchor-deleted','both-directories-deleted','both-rollback'].includes(mode)) await unlink(anchorFile);
  if(['both-deleted','both-directories-deleted','both-rollback'].includes(mode))await unlink(primaryFile);
  if(mode==='anchor-corrupt'||mode==='both-corrupt')await writeFile(anchorFile,'not json');
  if(mode==='primary-corrupt'||mode==='both-corrupt')await writeFile(primaryFile,'not json');
  if(mode==='anchor-rollback')await writeFile(anchorFile,JSON.stringify({id:'w0',digest:fingerprint(cp('b'))}));
  if(mode==='both-directories-deleted'){await rm(primary,{recursive:true,force:true});await rm(anchor,{recursive:true,force:true});}
  const reopened=new AnchoredWitness(primary,anchor,keys);
  const res=await reopened.vote('w0',cp('b'),kp.privateKey);
  const unsafe=!!res.ok;
  assert.equal(unsafe,['both-deleted','both-rollback'].includes(mode));assertions++;
  scenarios.push({mode,conflictingSignatureIssued:unsafe,outcome:res.reason??(unsafe?'SIGNED':'RECOVERED')});
 }finally{await rm(root,{recursive:true,force:true});}
}
console.log(JSON.stringify({status:'PASS_WITH_TWO_CONFIRMED_GAPS',assertions,scenarios},null,2));
