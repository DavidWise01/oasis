// OASIS {{i & dd}} v1.0 signed checkpoint overlay. No frozen source is modified.
// All signatures are Ed25519. Keys MUST be managed outside the checkpoint directory.
import {createHash, generateKeyPairSync, sign as edSign, verify as edVerify, createPublicKey} from 'node:crypto';
import * as fs from 'node:fs';
import * as path from 'node:path';
import {buildObsidian} from './obsidian-core.mjs';
import {assertFloor} from './quantum-dual.mjs';

export const CHECKPOINT_VERSION='i-dd-obsidian-checkpoint/v1.0';
export const ROOT_HEAD='GENESIS';
const hex=x=>createHash('sha256').update(x).digest('hex');
const canon=x=>JSON.stringify(x,(_,v)=>{if(v&&typeof v==='object'&&!Array.isArray(v))return Object.fromEntries(Object.entries(v).sort(([a],[b])=>a.localeCompare(b,'en')));return v});
function fail(msg){throw new Error('OBSIDIAN-CHECKPOINT: '+msg)}
function must(cond,msg){if(!cond)fail(msg)}
function cleanKey(v){return (v?.type==='public'?v:createPublicKey(v)).export({type:'spki',format:'pem'}).toString()}
const shaObject=v=>hex(canon(v));
const signRaw=(key,digest)=>edSign(null,Buffer.from(digest,'hex'),key).toString('base64');
const verifyRaw=(key,digest,sig)=>typeof sig==='string'&&edVerify(null,Buffer.from(digest,'hex'),key,Buffer.from(sig,'base64'));
const recordId=record=>shaObject(['OASIS-OBSIDIAN-RECORD-v1.0',record]);
const stageId=(stage,id)=>shaObject(['OASIS-OBSIDIAN-STAGE-v1.0',stage,id]);
const seqName=seq=>String(seq).padStart(12,'0');
function validateTrust(trust){
 must(trust&&trust.alpha&&trust.beta,'trusted public keys required');
 const keys={alpha:cleanKey(trust.alpha),beta:cleanKey(trust.beta)};
 must(keys.alpha!==keys.beta,'independent signing keys required');
 return keys;
}
function signed(stage,id,keys){const h=stageId(stage,id);return {stage,recordId:id,digest:h,signatures:{alpha:signRaw(keys.alpha.privateKey,h),beta:signRaw(keys.beta.privateKey,h)}}}
function checkSigned(marker,stage,id,trust){
 must(marker&&marker.stage===stage&&marker.recordId===id,'bad '+stage+' marker');
 const digest=stageId(stage,id);
 must(marker.digest===digest,'altered '+stage+' marker digest');
 for(const role of ['alpha','beta'])must(verifyRaw(trust[role],digest,marker.signatures?.[role]),'invalid '+stage+' signature: '+role);
 return true;
}
function assertRecord(record){
 must(record&&record.version===CHECKPOINT_VERSION,'wrong checkpoint version');
 must(Number.isSafeInteger(record.seq)&&record.seq>=1,'sequence invalid');
 must(typeof record.prev==='string'&&record.prev.length>0,'prior head missing');
 must(Array.isArray(record.tokens)&&record.tokens.length>=2&&record.tokens.length<=16,'finite CPU slice 2..16 required');
 must(Number.isSafeInteger(record.generation)&&record.generation>=0,'generation invalid');
 must(typeof record.parent==='string'&&record.parent.length>0,'parent invalid');
 const output=buildObsidian(record.tokens,{noise:record.noise,parent:record.parent,generation:record.generation});
 must(output.floor.sourceSha256===assertFloor().source,'upstream floor mismatch');
 must(record.floorSha256===output.floor.sourceSha256,'record floor sha mismatch');
 must(record.coreWitness===output.core.coreWitness,'core witness mismatch');
 must(record.outputSha256===shaObject(output.distribution),'outcome digest mismatch');
 return output;
}
function fileOf(root,seq,stage){return path.join(root,seqName(seq)+'.'+stage+'.json')}
function atomicImmutable(filename,data){
 const body=JSON.stringify(data,null,2)+'\n';
 if(fs.existsSync(filename)){
   must(fs.readFileSync(filename,'utf8')===body,'existing stage differs: '+path.basename(filename));return false;
 }
 const tmp=filename+'.tmp-'+process.pid+'-'+Math.random().toString(16).slice(2);
 let fd;
 try {
  fd=fs.openSync(tmp,'wx',0o600);fs.writeFileSync(fd,body);fs.fsyncSync(fd);fs.closeSync(fd);fd=undefined;
  // Exclusive link prevents overwriting existing immutable stage even under races.
  fs.linkSync(tmp,filename);fs.unlinkSync(tmp);
  const dirfd=fs.openSync(path.dirname(filename),'r');try{fs.fsyncSync(dirfd)}finally{fs.closeSync(dirfd)}
  return true;
 } finally {
  if(fd!==undefined)fs.closeSync(fd);
  if(fs.existsSync(tmp))fs.unlinkSync(tmp);
 }
}
function readJson(filename){try{return JSON.parse(fs.readFileSync(filename,'utf8'))}catch(e){fail('cannot read '+path.basename(filename)+': '+e.message)}}
function scan(root){if(!fs.existsSync(root))return [];
 const names=fs.readdirSync(root);
 for(const name of names)must(/^\d{12}\.(prepare|commit|finalize)\.json$/.test(name),'unexpected file in checkpoint directory: '+name);
 return [...new Set(names.map(x=>Number(x.slice(0,12))))].sort((a,b)=>a-b);
}
export function newWitnessKeys(){return {alpha:generateKeyPairSync('ed25519'),beta:generateKeyPairSync('ed25519')}}
export function trustFromKeys(keys){return validateTrust({alpha:keys.alpha.publicKey,beta:keys.beta.publicKey})}
export function readCheckpoints(root,trust,{anchorHead=null,anchorSeq=null}={}){
 const t=validateTrust(trust),seqs=scan(root),records=[];let previous=ROOT_HEAD;
 for(const seq of seqs){
  must(seq===records.length+1,'gap or duplicate sequence');
  const prep=readJson(fileOf(root,seq,'prepare'));
  must(prep&&prep.record,'missing checkpoint payload');
  assertRecord(prep.record);
  const id=recordId(prep.record);
  must(prep.id===id,'record digest corrupted');
  must(prep.record.seq===seq&&prep.record.prev===previous,'broken chain or replay');
  checkSigned(prep.marker,'prepare',id,t);
  const commitFile=fileOf(root,seq,'commit');
  if(!fs.existsSync(commitFile)){
    must(seq===seqs.at(-1),'uncommitted intermediate checkpoint');
    records.push({seq,id,status:'PREPARED_ONLY',record:prep.record});
    break;
  }
  checkSigned(readJson(commitFile),'commit',id,t);
  const finalFile=fileOf(root,seq,'finalize');
  if(fs.existsSync(finalFile))checkSigned(readJson(finalFile),'finalize',id,t);
  records.push({seq,id,status:fs.existsSync(finalFile)?'FINALIZED':'COMMITTED_NOT_FINALIZED',record:prep.record});
  previous=id;
 }
 const committed=records.filter(x=>x.status!=='PREPARED_ONLY');
 const latest=committed.at(-1)||null;
 if(anchorHead!==null)must(latest?.id===anchorHead,'external head anchor mismatch (rollback/fork)');
 if(anchorSeq!==null)must(latest?.seq===anchorSeq,'external sequence anchor mismatch (rollback)');
 return {latest,records,pending:records.find(x=>x.status==='PREPARED_ONLY')||null,
   recoverable:records.filter(x=>x.status==='COMMITTED_NOT_FINALIZED').map(x=>x.seq)};
}
function signerCheck(keys,trust){
 const t=validateTrust(trust);must(keys?.alpha?.privateKey&&keys?.beta?.privateKey,'two private signing keys required');
 for(const role of ['alpha','beta'])must(cleanKey(keys[role].publicKey)===t[role],'signer mismatch: '+role);
 return keys;
}
export function writeCheckpoint(root,{tokens,noise=0.1,parent='ROOT',generation=0,keys,trust,failpoint=null}={}){
 signerCheck(keys,trust);fs.mkdirSync(root,{recursive:true,mode:0o700});
 const before=readCheckpoints(root,trust);
 must(!before.pending,'uncommitted prepare exists: require explicit discard/quarantine');
 must(before.recoverable.length===0,'finalize valid committed checkpoints before writing next');
 const output=buildObsidian(tokens,{noise,parent,generation});const seq=(before.latest?.seq||0)+1;
 const record={version:CHECKPOINT_VERSION,seq,prev:before.latest?.id||ROOT_HEAD,
  tokens:[...tokens],noise,parent,generation,
  floorSha256:output.floor.sourceSha256,coreWitness:output.core.coreWitness,
  outputSha256:shaObject(output.distribution)};
 assertRecord(record);
 const id=recordId(record);
 atomicImmutable(fileOf(root,seq,'prepare'),{record,id,marker:signed('prepare',id,keys)});
 if(failpoint==='afterPrepare')throw new Error('INJECTED CRASH afterPrepare');
 atomicImmutable(fileOf(root,seq,'commit'),signed('commit',id,keys));
 if(failpoint==='afterCommit')throw new Error('INJECTED CRASH afterCommit');
 atomicImmutable(fileOf(root,seq,'finalize'),signed('finalize',id,keys));
 if(failpoint==='afterFinalize')throw new Error('INJECTED CRASH afterFinalize');
 return {seq,id,status:'FINALIZED',record};
}
export function recoverFinalization(root,trust,keys){
 signerCheck(keys,trust);const result=readCheckpoints(root,trust);
 for(const seq of result.recoverable){
  const entry=result.records.find(x=>x.seq===seq);
  atomicImmutable(fileOf(root,seq,'finalize'),signed('finalize',entry.id,keys));
 }
 return readCheckpoints(root,trust);
}
export function quarantinePrepared(root,trust){
 const result=readCheckpoints(root,trust);
 if(!result.pending)return {discarded:0,latest:result.latest};
 const file=fileOf(root,result.pending.seq,'prepare');
 const quarantine=path.join(path.dirname(root),'quarantine-'+path.basename(root));
 fs.mkdirSync(quarantine,{recursive:true,mode:0o700});
 const dst=path.join(quarantine,path.basename(file)+'.aborted-'+result.pending.id);
 must(!fs.existsSync(dst),'quarantine path already exists');
 fs.renameSync(file,dst);
 const fd=fs.openSync(root,'r');try{fs.fsyncSync(fd)}finally{fs.closeSync(fd)}
 return {discarded:1,latest:result.latest,quarantine:dst};
}