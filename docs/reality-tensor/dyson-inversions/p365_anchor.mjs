import {mkdir,open,readFile} from 'node:fs/promises';
import {join} from 'node:path';
import {fingerprint,verifyVote} from './p359_witness.mjs';
import {CrashWitness} from './p361_crash.mjs';
/** Separate append-only reservation anchor. Missing anchor directory fails closed. */
export class AnchoredWitness {
 constructor(primaryDir,anchorDir,keys){if(primaryDir===anchorDir)throw Error('anchor must be separate');this.primaryDir=primaryDir;this.anchorDir=anchorDir;this.keys=keys;}
 async vote(id,cp,privateKey){
  if(!this.keys.has(id))throw Error('unknown witness');
  const digest=fingerprint(cp);
  const name=Buffer.from(id+'|'+cp.context+'|'+cp.epoch).toString('hex')+'.json',path=join(this.anchorDir,name);
  let file,created=false;
  try{file=await open(path,'wx',0o600);created=true;
   try{await file.writeFile(JSON.stringify({id,digest}));await file.sync();}finally{await file.close();}
   try{const d=await open(this.anchorDir,'r');try{await d.sync();}finally{await d.close();}}catch{return {ok:false,reason:'anchor-not-durable'};}
  }catch(e){if(file)try{await file.close();}catch{}if(e.code!=='EEXIST')return {ok:false,reason:'anchor-unavailable'};
   let old;try{old=JSON.parse(await readFile(path,'utf8'));}catch{return {ok:false,reason:'anchor-corrupt'};}
   if(old.id!==id||old.digest!==digest)return {ok:false,reason:'anchor-conflict'};
  }
  const primary=new CrashWitness(this.primaryDir,this.keys);
  const original=await primary.inspect(id,cp);
  if(original.status==='committed'||created)return primary.vote(id,cp,privateKey);
  return {ok:false,reason:'anchor-reserved-quarantine'};
 }
}