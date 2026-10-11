import {DatabaseSync} from 'node:sqlite';
import {verify,createPublicKey} from 'node:crypto';
const wire=s=>Buffer.from(JSON.stringify({domain:'ROOT0/P443/head',deployment:s.deployment,epoch:s.epoch,hash:s.hash}));
export class IndependentAnchor {
 #db;#key;#deployment;
 constructor(path,publicKey,deployment){this.#db=new DatabaseSync(path);this.#db.exec('PRAGMA journal_mode=WAL;PRAGMA synchronous=FULL;CREATE TABLE IF NOT EXISTS anchors(deployment TEXT PRIMARY KEY,epoch INTEGER NOT NULL,hash TEXT NOT NULL,signature TEXT NOT NULL)');this.#key=publicKey.type==='public'?publicKey:createPublicKey(publicKey);this.#deployment=deployment;}
 verify(s){try{return s?.deployment===this.#deployment&&Number.isSafeInteger(s.epoch)&&s.epoch>=0&&/^[a-f0-9]{64}$/.test(s.hash)&&verify(null,wire(s),this.#key,Buffer.from(s.signature,'base64'))}catch{return false}}
 latest(){return this.#db.prepare('SELECT * FROM anchors WHERE deployment=?').get(this.#deployment)??null}
 observe(s){if(!this.verify(s))return {ok:false,reason:'invalid-signature'};this.#db.exec('BEGIN IMMEDIATE');try{const old=this.latest();const reject=reason=>{this.#db.exec('ROLLBACK');return {ok:false,reason}};if(old){if(s.epoch<old.epoch)return reject('rollback-detected');if(s.epoch===old.epoch)return s.hash===old.hash&&s.signature===old.signature?reject('already-anchored'):reject('equivocation-detected');if(s.epoch!==old.epoch+1)return reject('gap-detected');}
 this.#db.prepare('INSERT INTO anchors VALUES(?,?,?,?) ON CONFLICT(deployment) DO UPDATE SET epoch=excluded.epoch,hash=excluded.hash,signature=excluded.signature').run(s.deployment,s.epoch,s.hash,s.signature);this.#db.exec('COMMIT');return {ok:true,epoch:s.epoch};}catch(e){this.#db.exec('ROLLBACK');throw e}}
 compare(s){if(!this.verify(s))return {ok:false,reason:'invalid-signature'};const a=this.latest();if(!a)return {ok:false,reason:'anchor-uninitialized'};if(s.epoch<a.epoch)return {ok:false,reason:'rollback-detected'};if(s.epoch===a.epoch&&s.hash!==a.hash)return {ok:false,reason:'equivocation-detected'};if(s.epoch>a.epoch)return {ok:false,reason:'unanchored-future'};return {ok:true,reason:'aligned'};}
 close(){this.#db.close()}
}