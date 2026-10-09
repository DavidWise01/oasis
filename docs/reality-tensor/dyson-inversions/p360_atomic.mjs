import {mkdir, open, readFile, rename} from 'node:fs/promises';
import {join} from 'node:path';
import {fingerprint, makeVote, verifyVote} from './p359_witness.mjs';
/** Fail-closed exclusive reservation; do not use a directory on shared NFS without verified atomic create. */
export class AtomicWitness {
 constructor(dir, keys){this.dir=dir;this.keys=keys;}
 async vote(id,cp,privateKey){
  await mkdir(this.dir,{recursive:true});if(!this.keys.has(id))throw Error('unknown witness');
  const digest=fingerprint(cp),key=Buffer.from(id+'|'+cp.context+'|'+cp.epoch).toString('hex'),path=join(this.dir,key+'.json');
  let handle;
  try{handle=await open(path,'wx',0o600);
   try{await handle.writeFile(JSON.stringify({id,digest,checkpoint:cp}));await handle.sync();}finally{await handle.close();}
   try{const fd=await open(this.dir,'r');try{await fd.sync();}finally{await fd.close();}}catch{}
  }catch(e){if(handle)try{await handle.close();}catch{}if(e.code!=='EEXIST')throw e;
   let old;try{old=JSON.parse(await readFile(path,'utf8'));}catch{return {ok:false,reason:'incomplete-reservation'};}
   if(old.digest!==digest)return {ok:false,reason:'double-vote'};
   if(old.vote&&verifyVote(old.vote,this.keys))return {ok:true,duplicate:true,vote:old.vote};
   return {ok:false,reason:'reserved-pending-recovery'};
  }
  const vote=makeVote(id,cp,privateKey),temp=path+'.signed.'+process.pid+'.'+Math.random().toString(16).slice(2),file=await open(temp,'wx',0o600);
  try{await file.writeFile(JSON.stringify({id,digest,checkpoint:cp,vote}));await file.sync();}finally{await file.close();}
  await rename(temp,path);
  try{const fd=await open(this.dir,'r');try{await fd.sync();}finally{await fd.close();}}catch{}
  return {ok:true,duplicate:false,vote};
 }
}