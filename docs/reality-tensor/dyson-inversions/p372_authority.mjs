import {DatabaseSync} from 'node:sqlite';
import {createHash} from 'node:crypto';
const H=x=>createHash('sha256').update(x).digest('hex');
export const GENESIS=H('ROOT0:P372:GENESIS');
export class SerializedAuthority {
 constructor(file){
  this.db=new DatabaseSync(file,{timeout:15000});
  this.db.exec('PRAGMA journal_mode=WAL; PRAGMA synchronous=FULL; PRAGMA busy_timeout=15000;');
  this.db.exec("CREATE TABLE IF NOT EXISTS votes(id TEXT NOT NULL,epoch INTEGER NOT NULL,head TEXT NOT NULL,PRIMARY KEY(id,epoch)); CREATE TABLE IF NOT EXISTS meta(k TEXT PRIMARY KEY,v TEXT NOT NULL);");
  this.db.prepare("INSERT OR IGNORE INTO meta(k,v) VALUES('head',?)").run(GENESIS);
  this.db.prepare("INSERT OR IGNORE INTO meta(k,v) VALUES('count','0')").run();
 }
 reserve(id,epoch,head){
  if(typeof id!=='string'||!id||!Number.isSafeInteger(epoch)||epoch<0||!/^[0-9a-f]{64}$/.test(head))throw new RangeError('reservation');
  this.db.exec('BEGIN IMMEDIATE');
  try{
   const previous=this.db.prepare('SELECT head FROM votes WHERE id=? AND epoch=?').get(id,epoch);
   if(previous){this.db.exec('COMMIT');return {ok:previous.head===head,duplicate:previous.head===head,reason:previous.head===head?'duplicate':'conflict'};}
   const max=this.db.prepare('SELECT MAX(epoch) AS e FROM votes WHERE id=?').get(id).e;
   if(max!==null&&epoch<max){this.db.exec('ROLLBACK');return {ok:false,reason:'rollback'};}
   const old=this.db.prepare("SELECT v FROM meta WHERE k='head'").get().v;
   const next=H(old+'|'+JSON.stringify({id,epoch,head}));
   this.db.prepare('INSERT INTO votes VALUES (?,?,?)').run(id,epoch,head);
   this.db.prepare("UPDATE meta SET v=? WHERE k='head'").run(next);
   this.db.prepare("UPDATE meta SET v=CAST(CAST(v AS INTEGER)+1 AS TEXT) WHERE k='count'").run();
   this.db.exec('COMMIT');return {ok:true,duplicate:false,checkpointHead:next};
  }catch(e){try{this.db.exec('ROLLBACK')}catch{}throw e;}
 }
 status(){return {count:Number(this.db.prepare("SELECT v FROM meta WHERE k='count'").get().v),head:this.db.prepare("SELECT v FROM meta WHERE k='head'").get().v,integrity:this.db.prepare('PRAGMA integrity_check').get().integrity_check};}
 close(){this.db.close();}
}