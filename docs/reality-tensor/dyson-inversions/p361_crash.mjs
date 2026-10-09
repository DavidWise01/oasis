import {mkdir,open,readFile,rename} from 'node:fs/promises';
import {join} from 'node:path';
import {fingerprint,makeVote,verifyVote} from './p359_witness.mjs';
export const STAGES=Object.freeze(['reserved','signed','temporary-durable','committed']);
async function syncDir(dir){const h=await open(dir,'r');try{await h.sync();}finally{await h.close();}}
export class CrashWitness {
 constructor(dir,keys){this.dir=dir;this.keys=keys;}
 async vote(id,cp,privateKey,{crashAt=null}={}){
  if(crashAt!==null&&!STAGES.includes(crashAt))throw new RangeError('crashAt');
  if(!this.keys.has(id))throw new Error('unknown witness');
  const digest=fingerprint(cp),key=Buffer.from(id+'|'+cp.context+'|'+cp.epoch).toString('hex');
  await mkdir(this.dir,{recursive:true});const path=join(this.dir,key+'.json');
  let h;try{h=await open(path,'wx',0o600);}catch(e){
   if(e.code!=='EEXIST')throw e;
   let old;try{old=JSON.parse(await readFile(path,'utf8'));}catch{return {ok:false,reason:'incomplete-reservation'};}
   if(old.digest!==digest)return {ok:false,reason:'double-vote'};
   if(old.vote&&verifyVote(old.vote,this.keys))return {ok:true,duplicate:true,vote:old.vote};
   return {ok:false,reason:'reserved-pending-recovery'};
  }
  try{await h.writeFile(JSON.stringify({id,digest,checkpoint:cp}));await h.sync();}finally{await h.close();}
  await syncDir(this.dir);if(crashAt==='reserved')throw new Error('INJECTED:reserved');
  const vote=makeVote(id,cp,privateKey);
  if(crashAt==='signed')throw new Error('INJECTED:signed');
  const temp=path+'.pending';let tmp;
  try{tmp=await open(temp,'wx',0o600);await tmp.writeFile(JSON.stringify({id,digest,checkpoint:cp,vote}));await tmp.sync();}finally{if(tmp)await tmp.close();}
  if(crashAt==='temporary-durable')throw new Error('INJECTED:temporary-durable');
  await rename(temp,path);await syncDir(this.dir);
  if(crashAt==='committed')throw new Error('INJECTED:committed');
  return {ok:true,duplicate:false,vote};
 }
 async inspect(id,cp){const key=Buffer.from(id+'|'+cp.context+'|'+cp.epoch).toString('hex');const path=join(this.dir,key+'.json');let o;try{o=JSON.parse(await readFile(path,'utf8'));}catch{return {status:'unreadable'};}
  if(o.digest!==fingerprint(cp))return {status:'conflict'};
  if(o.vote&&verifyVote(o.vote,this.keys))return {status:'committed',vote:o.vote};
  return {status:'quarantined',recovery:'manual-attestation-required'};
 }
}