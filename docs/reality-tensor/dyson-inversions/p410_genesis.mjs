import {DatabaseSync} from 'node:sqlite';
import {sign, verify, randomUUID, createHash} from 'node:crypto';
import {existsSync} from 'node:fs';
const hash=x=>createHash('sha256').update(x).digest('hex');
const encode=x=>Buffer.from(JSON.stringify({domain:'ROOT0/P410/genesis/v1',deployment:x.deployment,nonce:x.nonce,mode:'GENESIS-ONLY'}));
export const BLOCKADE='{-{+{%}+}-}';
export function genesisGrant(privateKey,deployment,nonce=randomUUID()){
 const x={deployment,nonce};return {...x,signature:sign(null,encode(x),privateKey).toString('base64')};
}
export function validateGrant(g,publicKey,deployment){
 if(!g||g.deployment!==deployment||typeof g.nonce!=='string'||!g.nonce||typeof g.signature!=='string')return false;
 try{return verify(null,encode(g),publicKey,Buffer.from(g.signature,'base64'));}catch{return false;}
}
/** Prototype authority; durable local SQLite is NOT a nonrollbackable external witness. */
export class GenesisAuthority {
 constructor(file,operatorPublicKey,deployment){
  if(!deployment||typeof deployment!=='string')throw Error('deployment required');
  this.file=file;this.key=operatorPublicKey;this.deployment=deployment;
  if(!existsSync(file)) {this.db=null;return;}
  this.db=new DatabaseSync(file,{timeout:10000});
  this.db.exec('PRAGMA journal_mode=WAL; PRAGMA synchronous=FULL; PRAGMA busy_timeout=10000;');
 }
 static provision(file,operatorPublicKey,deployment,grant){
  if(existsSync(file))throw Error('authority-exists: refuse re-genesis');
  if(!validateGrant(grant,operatorPublicKey,deployment))throw Error('invalid-genesis-grant');
  const db=new DatabaseSync(file,{timeout:10000});
  try{
   db.exec('PRAGMA journal_mode=WAL; PRAGMA synchronous=FULL; BEGIN IMMEDIATE; CREATE TABLE IF NOT EXISTS meta(id INTEGER PRIMARY KEY CHECK(id=1), deployment TEXT NOT NULL, grant_digest TEXT NOT NULL, head TEXT NOT NULL, epoch INTEGER NOT NULL);');
   db.prepare('INSERT INTO meta(id,deployment,grant_digest,head,epoch) VALUES(1,?,?,?,0)').run(deployment,hash(encode(grant)),hash('ROOT0:P410:GENESIS|'+deployment));
   db.exec('COMMIT');
  }catch(e){try{db.exec('ROLLBACK');}catch{}db.close();throw e;}
  db.close();return new GenesisAuthority(file,operatorPublicKey,deployment);
 }
 status(){
  if(!this.db)return {ok:false,reason:'authority-missing:recovery-required'};
  try{const row=this.db.prepare('SELECT deployment,grant_digest,head,epoch FROM meta WHERE id=1').get();
   if(!row||row.deployment!==this.deployment||!/^([a-f0-9]{64})$/.test(row.head)||!Number.isSafeInteger(row.epoch))return {ok:false,reason:'invalid-authority-state'};
   return {ok:true,...row};
  }catch{return {ok:false,reason:'invalid-authority-state'};}
 }
 advance(epoch,head,{failBeforeCommit=false}={}){
  if(!Number.isSafeInteger(epoch)||epoch<1||typeof head!=='string'||!/^[a-f0-9]{64}$/.test(head))return {ok:false,reason:'invalid-input'};
  if(!this.db)return {ok:false,reason:'authority-missing:recovery-required'};
  this.db.exec('BEGIN IMMEDIATE');
  try{const s=this.status();if(!s.ok){this.db.exec('ROLLBACK');return s;}
   if(epoch!==s.epoch+1){this.db.exec('ROLLBACK');return {ok:false,reason:'nonconsecutive-or-replayed-epoch'};}
   const next=hash(s.head+'|'+epoch+'|'+head);
   this.db.prepare('UPDATE meta SET epoch=?,head=? WHERE id=1').run(epoch,next);
   if(failBeforeCommit)throw Error('injected-crash-before-commit');
   this.db.exec('COMMIT');return {ok:true,epoch,head:next};
  }catch(e){try{this.db.exec('ROLLBACK');}catch{}return {ok:false,reason:e.message};}
 }
 close(){this.db?.close();}
}