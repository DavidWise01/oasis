import {DatabaseSync} from 'node:sqlite';
import {sign,verify} from 'node:crypto';
const encode=x=>Buffer.from(JSON.stringify({domain:'ROOT0/P415/witness/v1',deployment:x.deployment,epoch:x.epoch,head:x.head}));
export class SeparateWitness {
 constructor(path,privateKey,publicKey,deployment,{offline=false}={}){
 this.path=path;this.privateKey=privateKey;this.publicKey=publicKey;this.deployment=deployment;this.offline=offline;
 this.db=new DatabaseSync(path,{timeout:15000});
 this.db.exec('PRAGMA journal_mode=WAL; PRAGMA synchronous=FULL; PRAGMA busy_timeout=15000; CREATE TABLE IF NOT EXISTS witness (deployment TEXT PRIMARY KEY, epoch INTEGER NOT NULL, head TEXT NOT NULL, sig TEXT NOT NULL);');
 }
 static signed(privateKey,deployment,epoch,head){const data={deployment,epoch,head};return {...data,sig:sign(null,encode(data),privateKey).toString('base64')};}
 static valid(x,publicKey){if(!x||typeof x.deployment!=='string'||!Number.isSafeInteger(x.epoch)||x.epoch<0||!/^([a-f0-9]{64})$/.test(x.head)||typeof x.sig!=='string')return false;try{return verify(null,encode(x),publicKey,Buffer.from(x.sig,'base64'));}catch{return false;}}
 read(){if(this.offline)return {ok:false,reason:'witness-unavailable'};const r=this.db.prepare('SELECT deployment,epoch,head,sig FROM witness WHERE deployment=?').get(this.deployment);if(!r)return {ok:false,reason:'no-witness-record'};if(!SeparateWitness.valid(r,this.publicKey))return {ok:false,reason:'invalid-witness-signature'};return {ok:true,stamp:r};}
 register(epoch,head){if(this.offline)return {ok:false,reason:'witness-unavailable'};this.db.exec('BEGIN IMMEDIATE');try{
 const old=this.db.prepare('SELECT deployment,epoch,head,sig FROM witness WHERE deployment=?').get(this.deployment);
 if(old&&!SeparateWitness.valid(old,this.publicKey)){this.db.exec('ROLLBACK');return {ok:false,reason:'stored-signature-invalid'}};
 if(old&&(epoch<old.epoch||(epoch===old.epoch&&head!==old.head))){this.db.exec('ROLLBACK');return {ok:false,reason:'rollback-or-fork'}};
 if(old&&epoch===old.epoch){this.db.exec('COMMIT');return {ok:true,duplicate:true,stamp:old}};
 if(old&&epoch!==old.epoch+1){this.db.exec('ROLLBACK');return {ok:false,reason:'epoch-gap'}};
 if(!Number.isSafeInteger(epoch)||epoch<0||!/^([a-f0-9]{64})$/.test(head)){this.db.exec('ROLLBACK');return {ok:false,reason:'invalid-register'}};
 const stamp=SeparateWitness.signed(this.privateKey,this.deployment,epoch,head);
 this.db.prepare('INSERT INTO witness (deployment,epoch,head,sig) VALUES (?,?,?,?) ON CONFLICT(deployment) DO UPDATE SET epoch=excluded.epoch,head=excluded.head,sig=excluded.sig').run(this.deployment,epoch,head,stamp.sig);
 this.db.exec('COMMIT');return {ok:true,duplicate:false,stamp};
 }catch(e){try{this.db.exec('ROLLBACK')}catch{}throw e;}}
 close(){this.db.close()}
}