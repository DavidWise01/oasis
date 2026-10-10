import {DatabaseSync} from 'node:sqlite';
import {randomBytes,sign,verify,createPublicKey} from 'node:crypto';
const wire=x=>Buffer.from(JSON.stringify({domain:'ROOT0/P426/receipt/v1',deployment:x.deployment,nonce:x.nonce,epoch:x.epoch,head:x.head}));
const valid=x=>x&&Number.isSafeInteger(x.epoch)&&x.epoch>=0&&typeof x.head==='string'&&/^[0-9a-f]{64}$/.test(x.head);
export function signedReceipt(privateKey,deployment,nonce,epoch,head){if(!/^[a-f0-9]{48}$/.test(nonce)||!valid({epoch,head}))throw Error('invalid receipt');const x={deployment,nonce,epoch,head};return {...x,signature:sign(null,wire(x),privateKey).toString('base64')};}
export class DurableVerifier {
 constructor(path,publicKey,deployment,{maxAgeMs=60000}={}) {this.db=new DatabaseSync(path,{timeout:15000});this.db.exec('PRAGMA journal_mode=WAL;PRAGMA synchronous=FULL;CREATE TABLE IF NOT EXISTS p426_pending(nonce TEXT PRIMARY KEY, issued INTEGER NOT NULL, consumed INTEGER NOT NULL DEFAULT 0);CREATE TABLE IF NOT EXISTS p426_floor(deployment TEXT PRIMARY KEY,epoch INTEGER NOT NULL,head TEXT NOT NULL)');this.key=createPublicKey(publicKey);this.deployment=deployment;this.maxAgeMs=maxAgeMs;}
 issue(){const nonce=randomBytes(24).toString('hex');this.db.prepare('INSERT INTO p426_pending(nonce,issued) VALUES(?,?)').run(nonce,Date.now());return {deployment:this.deployment,nonce};}
 floor(){return this.db.prepare('SELECT epoch,head FROM p426_floor WHERE deployment=?').get(this.deployment)??null;}
 verify(receipt){this.db.exec('BEGIN IMMEDIATE');try{const reject=reason=>{this.db.exec('ROLLBACK');return {ok:false,reason}};
 if(!receipt||receipt.deployment!==this.deployment||!/^([a-f0-9]{48})$/.test(receipt.nonce??''))return reject('invalid-response');
 const pending=this.db.prepare('SELECT issued,consumed FROM p426_pending WHERE nonce=?').get(receipt.nonce);if(!pending||pending.consumed)return reject('replay-or-unsolicited');
 this.db.prepare('UPDATE p426_pending SET consumed=1 WHERE nonce=?').run(receipt.nonce);
 const invalid=reason=>{this.db.exec('COMMIT');return {ok:false,reason}};
 if(Date.now()-pending.issued>this.maxAgeMs||Date.now()<pending.issued)return invalid('expired');
 if(!valid(receipt)||typeof receipt.signature!=='string')return invalid('malformed');
 let trusted=false;try{trusted=verify(null,wire(receipt),this.key,Buffer.from(receipt.signature,'base64'))}catch{}
 if(!trusted)return invalid('invalid-signature');
 const floor=this.floor();if(floor&&(receipt.epoch<floor.epoch||(receipt.epoch===floor.epoch&&receipt.head!==floor.head)))return invalid('rollback-or-fork');
 this.db.prepare('INSERT INTO p426_floor(deployment,epoch,head) VALUES(?,?,?) ON CONFLICT(deployment) DO UPDATE SET epoch=excluded.epoch,head=excluded.head').run(this.deployment,receipt.epoch,receipt.head);
 this.db.exec('COMMIT');return {ok:true,epoch:receipt.epoch};}catch(e){try{this.db.exec('ROLLBACK')}catch{}throw e;}}
 close(){this.db.close()}
}