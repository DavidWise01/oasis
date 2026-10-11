import {DatabaseSync} from 'node:sqlite';
import {sign,verify,createPublicKey} from 'node:crypto';
const msg=(domain,obj)=>Buffer.from(JSON.stringify({domain,...obj}));
const pub=k=>k?.type==='public'?k:createPublicKey(k);
const hex=(x,n)=>typeof x==='string'&&new RegExp(`^[a-f0-9]{${n}}$`).test(x);
export const signPolicy=(key,p)=>({...p,signature:sign(null,msg('ROOT0/P443/policy',{deployment:p.deployment,sequence:p.sequence,epoch:p.epoch,keys:p.keys}),key).toString('base64')});
export const signIntent=(key,i)=>({...i,signature:sign(null,msg('ROOT0/P443/intent',{deployment:i.deployment,epoch:i.epoch,prior:i.prior,next:i.next,nonce:i.nonce}),key).toString('base64')});
export const signRequest=(key,r)=>({...r,signature:sign(null,msg('ROOT0/P443/request',{deployment:r.deployment,keyId:r.keyId,policyEpoch:r.policyEpoch,nonce:r.nonce,action:r.action,intent:r.intent??null}),key).toString('base64')});
const verified=(key,domain,obj,sig)=>{try{return typeof sig==='string'&&verify(null,msg(domain,obj),pub(key),Buffer.from(sig,'base64'))}catch{return false}};
export class AtomicWitness {
 #db;#witnessKey;#witnessPub;#admin;#owner;#clients;#deployment;#cap;
 constructor(path,{deployment,witnessPrivate,witnessPublic,adminPublic,ownerPublic,clients,cap=32}){
  this.#db=new DatabaseSync(path,{timeout:15000});this.#db.exec('PRAGMA journal_mode=WAL;PRAGMA synchronous=FULL;PRAGMA busy_timeout=15000;CREATE TABLE IF NOT EXISTS policy(deployment TEXT PRIMARY KEY, sequence INTEGER NOT NULL, epoch INTEGER NOT NULL, keys TEXT NOT NULL); CREATE TABLE IF NOT EXISTS head(deployment TEXT PRIMARY KEY, epoch INTEGER NOT NULL, hash TEXT NOT NULL, signature TEXT NOT NULL);CREATE TABLE IF NOT EXISTS nonce(deployment TEXT NOT NULL,epoch INTEGER NOT NULL,value TEXT NOT NULL,PRIMARY KEY(deployment,epoch,value));');
  this.#deployment=deployment;this.#witnessKey=witnessPrivate;this.#witnessPub=pub(witnessPublic);this.#admin=pub(adminPublic);this.#owner=pub(ownerPublic);this.#clients=new Map(Object.entries(clients).map(([id,k])=>[id,pub(k)]));this.#cap=cap;
 }
 #policy(){const p=this.#db.prepare('SELECT * FROM policy WHERE deployment=?').get(this.#deployment);return p&&{sequence:p.sequence,epoch:p.epoch,keys:JSON.parse(p.keys)};}
 #head(){return this.#db.prepare('SELECT * FROM head WHERE deployment=?').get(this.#deployment)}
 #seal(epoch,hash){const x={deployment:this.#deployment,epoch,hash};return {...x,signature:sign(null,msg('ROOT0/P443/head',x),this.#witnessKey).toString('base64')}}
 read(){const r=this.#head();return r&&verified(this.#witnessPub,'ROOT0/P443/head',{deployment:r.deployment,epoch:r.epoch,hash:r.hash},r.signature)?{ok:true,stamp:r}:{ok:false,reason:'missing-or-invalid-head'};}
 bootstrap(hash){if(!hex(hash,64))return {ok:false,reason:'bad-hash'};this.#db.exec('BEGIN IMMEDIATE');try{if(this.#head()){this.#db.exec('ROLLBACK');return {ok:false,reason:'already-initialized'}}const r=this.#seal(0,hash);this.#db.prepare('INSERT INTO head VALUES(?,?,?,?)').run(r.deployment,r.epoch,r.hash,r.signature);this.#db.exec('COMMIT');return {ok:true};}catch(e){this.#db.exec('ROLLBACK');throw e}}
 applyPolicy(p){if(!p||p.deployment!==this.#deployment||!Number.isSafeInteger(p.sequence)||!Number.isSafeInteger(p.epoch)||!Array.isArray(p.keys)||p.keys.length===0||new Set(p.keys).size!==p.keys.length||p.keys.some(k=>!this.#clients.has(k))||!verified(this.#admin,'ROOT0/P443/policy',{deployment:p.deployment,sequence:p.sequence,epoch:p.epoch,keys:p.keys},p.signature))return {ok:false,reason:'bad-policy'};
  this.#db.exec('BEGIN IMMEDIATE');try{const old=this.#policy();if(old?(p.sequence!==old.sequence+1||p.epoch!==old.epoch+1):(p.sequence!==0||p.epoch!==0)){this.#db.exec('ROLLBACK');return {ok:false,reason:'policy-sequence'}}this.#db.prepare('INSERT INTO policy VALUES(?,?,?,?) ON CONFLICT(deployment) DO UPDATE SET sequence=excluded.sequence,epoch=excluded.epoch,keys=excluded.keys').run(this.#deployment,p.sequence,p.epoch,JSON.stringify(p.keys));this.#db.prepare('DELETE FROM nonce WHERE deployment=? AND epoch<?').run(this.#deployment,p.epoch);this.#db.exec('COMMIT');return {ok:true};}catch(e){this.#db.exec('ROLLBACK');throw e}}
 execute(req,{checkpoint=()=>{}}={}){
  if(!req||req.deployment!==this.#deployment||!['READ','CAS'].includes(req.action)||!Number.isSafeInteger(req.policyEpoch)||!hex(req.nonce,32)||!this.#clients.has(req.keyId)||!verified(this.#clients.get(req.keyId),'ROOT0/P443/request',{deployment:req.deployment,keyId:req.keyId,policyEpoch:req.policyEpoch,nonce:req.nonce,action:req.action,intent:req.intent??null},req.signature))return {ok:false,reason:'unauthorized'};
  this.#db.exec('BEGIN IMMEDIATE');try{checkpoint('begin');const fail=reason=>{this.#db.exec('ROLLBACK');return {ok:false,reason}};const p=this.#policy();if(!p||req.policyEpoch!==p.epoch||!p.keys.includes(req.keyId))return fail('policy-denied');
   const count=this.#db.prepare('SELECT COUNT(*) n FROM nonce WHERE deployment=? AND epoch=?').get(this.#deployment,p.epoch).n;if(count>=this.#cap)return fail('ledger-full');if(this.#db.prepare('SELECT 1 FROM nonce WHERE deployment=? AND epoch=? AND value=?').get(this.#deployment,p.epoch,req.nonce))return fail('replay');
   const head=this.read();if(!head.ok)return fail(head.reason);
   if(req.action==='CAS'){
    const i=req.intent;if(!i||i.deployment!==this.#deployment||!Number.isSafeInteger(i.epoch)||!hex(i.prior,64)||!hex(i.next,64)||!hex(i.nonce,32)||!verified(this.#owner,'ROOT0/P443/intent',{deployment:i.deployment,epoch:i.epoch,prior:i.prior,next:i.next,nonce:i.nonce},i.signature))return fail('invalid-intent');
    if(i.epoch!==head.stamp.epoch+1||i.prior!==head.stamp.hash)return fail('cas-precondition');
   }
   this.#db.prepare('INSERT INTO nonce VALUES(?,?,?)').run(this.#deployment,p.epoch,req.nonce);checkpoint('nonce-written');
   let stamp=head.stamp;
   if(req.action==='CAS'){stamp=this.#seal(req.intent.epoch,req.intent.next);this.#db.prepare('UPDATE head SET epoch=?,hash=?,signature=? WHERE deployment=?').run(stamp.epoch,stamp.hash,stamp.signature,this.#deployment);}checkpoint('head-written');this.#db.exec('COMMIT');checkpoint('committed');return {ok:true,stamp};
  }catch(e){try{this.#db.exec('ROLLBACK')}catch{}throw e}
 }
 nonceCount(){return this.#db.prepare('SELECT COUNT(*) n FROM nonce WHERE deployment=?').get(this.#deployment).n}
 close(){this.#db.close()}
}