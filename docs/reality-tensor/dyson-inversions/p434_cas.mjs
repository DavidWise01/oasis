import {DatabaseSync} from 'node:sqlite';
import {sign,verify} from 'node:crypto';
const intentWire=x=>Buffer.from(JSON.stringify({domain:'ROOT0/P431/intent/v1',deployment:x.deployment,epoch:x.epoch,priorHead:x.priorHead,nextHead:x.nextHead,nonce:x.nonce}));
export function signIntent(key,x){if(!x||!Number.isSafeInteger(x.epoch)||x.epoch<1||!/^[a-f0-9]{64}$/.test(x.priorHead)||!/^[a-f0-9]{64}$/.test(x.nextHead)||!/^[a-f0-9]{32}$/.test(x.nonce))throw Error('invalid intent');return {...x,signature:sign(null,intentWire(x),key).toString('base64')};}
export function verifyIntent(key,x){try{return !!x&&verify(null,intentWire(x),key,Buffer.from(x.signature,'base64'))}catch{return false}}
const enc=x=>Buffer.from(JSON.stringify({domain:'ROOT0/P433/checkpoint/v1',deployment:x.deployment,epoch:x.epoch,head:x.head}));
export class StrictCasWitness {
 #db;#signer;#verifier;#owner;
 constructor(path,signer,verifier,owner){this.#db=new DatabaseSync(path,{timeout:15000});this.#db.exec('PRAGMA journal_mode=WAL;PRAGMA synchronous=FULL;PRAGMA busy_timeout=15000;CREATE TABLE IF NOT EXISTS p433_head(deployment TEXT PRIMARY KEY,epoch INTEGER NOT NULL,head TEXT NOT NULL,signature TEXT NOT NULL);CREATE TABLE IF NOT EXISTS p433_intent(deployment TEXT NOT NULL,epoch INTEGER NOT NULL,nonce TEXT NOT NULL,nextHead TEXT NOT NULL,PRIMARY KEY(deployment,epoch),UNIQUE(deployment,nonce));');this.#signer=signer;this.#verifier=verifier;this.#owner=owner;}
 #signed(deployment,epoch,head){let r={deployment,epoch,head};return {...r,signature:sign(null,enc(r),this.#signer).toString('base64')}}
 #valid(r){try{return r&&verify(null,enc(r),this.#verifier,Buffer.from(r.signature,'base64'));}catch{return false}}
 read(deployment){const r=this.#db.prepare('SELECT * FROM p433_head WHERE deployment=?').get(deployment);return !r?{ok:false,reason:'missing'}:this.#valid(r)?{ok:true,stamp:r}:{ok:false,reason:'bad-signature'};}
 initialize(deployment,head){if(typeof deployment!=='string'||!deployment||!/^[a-f0-9]{64}$/.test(head))return {ok:false,reason:'invalid'};this.#db.exec('BEGIN IMMEDIATE');try{if(this.read(deployment).ok){this.#db.exec('ROLLBACK');return {ok:false,reason:'already-initialized'}}const r=this.#signed(deployment,0,head);this.#db.prepare('INSERT INTO p433_head VALUES(?,?,?,?)').run(r.deployment,r.epoch,r.head,r.signature);this.#db.exec('COMMIT');return {ok:true,stamp:r}}catch(e){this.#db.exec('ROLLBACK');return {ok:false,reason:'genesis-refused'}}}
 // Deliberately no publish() or raw database accessor.
 cas(intent,{checkpoint=()=>{}}={}){
 if(!intent||!Number.isSafeInteger(intent.epoch)||intent.epoch<1||!/^[a-f0-9]{64}$/.test(intent.priorHead??'')||!/^[a-f0-9]{64}$/.test(intent.nextHead??'')||!/^[a-f0-9]{32}$/.test(intent.nonce??'')||!verifyIntent(this.#owner,intent))return {ok:false,reason:'bad-intent'};
 this.#db.exec('BEGIN IMMEDIATE');try{
 checkpoint('transaction-start');
 const old=this.read(intent.deployment);if(!old.ok){this.#db.exec('ROLLBACK');return {ok:false,reason:old.reason}}
 const prev=this.#db.prepare('SELECT nonce,nextHead FROM p433_intent WHERE deployment=? AND epoch=?').get(intent.deployment,intent.epoch);
 if(prev){this.#db.exec('COMMIT');return prev.nonce===intent.nonce&&prev.nextHead===intent.nextHead&&old.stamp.epoch===intent.epoch&&old.stamp.head===intent.nextHead?{ok:true,duplicate:true}:{ok:false,reason:'conflict'}}
 if(old.stamp.epoch!==intent.epoch-1||old.stamp.head!==intent.priorHead){this.#db.exec('ROLLBACK');return {ok:false,reason:'cas-mismatch'}}
 this.#db.prepare('INSERT INTO p433_intent VALUES(?,?,?,?)').run(intent.deployment,intent.epoch,intent.nonce,intent.nextHead);
 checkpoint('intent-written');
 const receipt=this.#signed(intent.deployment,intent.epoch,intent.nextHead);
 this.#db.prepare('UPDATE p433_head SET epoch=?,head=?,signature=? WHERE deployment=?').run(receipt.epoch,receipt.head,receipt.signature,intent.deployment);
 checkpoint('checkpoint-written');
 this.#db.exec('COMMIT');checkpoint('committed');return {ok:true,stamp:receipt};
 }catch(e){try{this.#db.exec('ROLLBACK')}catch{}throw e;}
 }
 close(){this.#db.close()}
}