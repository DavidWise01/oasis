import {DatabaseSync} from 'node:sqlite';
import {sign,verify} from 'node:crypto';
const wire=x=>Buffer.from(JSON.stringify({domain:'ROOT0/P418/anchor/v1',deployment:x.deployment,epoch:x.epoch,head:x.head}));
export class Anchor {
 constructor(path,privateKey,publicKey,deployment){this.db=new DatabaseSync(path,{timeout:15000});this.db.exec('PRAGMA journal_mode=WAL;PRAGMA synchronous=FULL;CREATE TABLE IF NOT EXISTS head(deployment TEXT PRIMARY KEY,epoch INTEGER NOT NULL,digest TEXT NOT NULL,signature TEXT NOT NULL)');Object.assign(this,{privateKey,publicKey,deployment});}
 latest(){return this.db.prepare('SELECT deployment,epoch,digest,signature FROM head WHERE deployment=?').get(this.deployment)??null;}
 static verify(x,key){try{return !!x&&verify(null,wire({deployment:x.deployment,epoch:x.epoch,head:x.digest}),key,Buffer.from(x.signature,'base64'));}catch{return false}}
 commit(stamp){if(!stamp||stamp.deployment!==this.deployment||!Number.isSafeInteger(stamp.epoch)||stamp.epoch<0||!/^([a-f0-9]{64})$/.test(stamp.head))return {ok:false,reason:'invalid-stamp'};
 this.db.exec('BEGIN IMMEDIATE');try{const old=this.latest();if(old&&!Anchor.verify(old,this.publicKey)){this.db.exec('ROLLBACK');return {ok:false,reason:'corrupt-anchor'}};
 if(old&&(stamp.epoch<old.epoch||stamp.epoch===old.epoch&&stamp.head!==old.digest)){this.db.exec('ROLLBACK');return {ok:false,reason:'rollback-or-fork'}};
 if(old&&stamp.epoch===old.epoch){this.db.exec('COMMIT');return {ok:true,duplicate:true,stamp:old}};
 if(old&&stamp.epoch!==old.epoch+1||!old&&stamp.epoch!==0){this.db.exec('ROLLBACK');return {ok:false,reason:'gap'}};
 const row={deployment:this.deployment,epoch:stamp.epoch,digest:stamp.head,signature:sign(null,wire(stamp),this.privateKey).toString('base64')};this.db.prepare('INSERT INTO head VALUES(?,?,?,?) ON CONFLICT(deployment) DO UPDATE SET epoch=excluded.epoch,digest=excluded.digest,signature=excluded.signature').run(row.deployment,row.epoch,row.digest,row.signature);this.db.exec('COMMIT');return {ok:true,stamp:row};}catch(e){try{this.db.exec('ROLLBACK')}catch{}throw e;}}
 inspect(local){const anchor=this.latest();if(!anchor)return {ok:false,reason:'anchor-missing'};if(!Anchor.verify(anchor,this.publicKey))return {ok:false,reason:'anchor-invalid'};if(!local?.ok||!local.stamp)return {ok:false,reason:'local-unavailable'};const x=local.stamp;if(x.epoch<anchor.epoch)return {ok:false,reason:'local-rollback'};if(x.epoch>anchor.epoch)return {ok:false,reason:'local-ahead-requires-recovery-intent'};if(x.head!==anchor.digest)return {ok:false,reason:'fork'};return {ok:true,epoch:x.epoch};}
 close(){this.db.close()}
}