import {DatabaseSync} from 'node:sqlite';
import {createHash} from 'node:crypto';
const H=s=>createHash('sha256').update(s).digest('hex');
export const TOPOLOGY='-+5 + 1';
export const GENESIS=H('ROOT0:P370:GENESIS');
export class TransactionalAnchor {
 constructor(file, trusted) {
  if(!trusted||!Number.isSafeInteger(trusted.count)||!(/^[0-9a-f]{64}$/.test(trusted.head))) throw Error('independent trusted checkpoint required');
  this.db=new DatabaseSync(file);this.db.exec('PRAGMA journal_mode=WAL; PRAGMA synchronous=FULL; PRAGMA busy_timeout=5000;');
  this.db.exec('CREATE TABLE IF NOT EXISTS votes (id TEXT NOT NULL, epoch INTEGER NOT NULL, head TEXT NOT NULL, PRIMARY KEY(id,epoch)); CREATE TABLE IF NOT EXISTS meta (name TEXT PRIMARY KEY, value TEXT NOT NULL);');
  this.db.prepare("INSERT OR IGNORE INTO meta(name,value) VALUES ('head',?)").run(GENESIS);
  this.db.prepare("INSERT OR IGNORE INTO meta(name,value) VALUES ('count','0')").run();
  this.trusted={...trusted};
 }
 checkpoint(){return {count:Number(this.db.prepare("SELECT value FROM meta WHERE name='count'").get().value),head:this.db.prepare("SELECT value FROM meta WHERE name='head'").get().value};}
 validate(){const local=this.checkpoint();return local.count===this.trusted.count&&local.head===this.trusted.head;}
 reserve(id,epoch,head){
  if(typeof id!=='string'||!id||!Number.isSafeInteger(epoch)||epoch<0||!/^[a-f0-9]{64}$/.test(head))throw RangeError('reservation');
  this.db.exec('BEGIN IMMEDIATE');
  try{
   if(!this.validate()){this.db.exec('ROLLBACK');return {ok:false,reason:'checkpoint-mismatch'};}
   const old=this.db.prepare('SELECT head FROM votes WHERE id=? AND epoch=?').get(id,epoch);
   if(old){this.db.exec('COMMIT');return {ok:old.head===head,previous:old.head===head,reason:old.head===head?'duplicate':'double-vote',checkpoint:this.trusted};}
   const later=this.db.prepare('SELECT MAX(epoch) AS epoch FROM votes WHERE id=?').get(id).epoch;
   if(later!==null&&epoch<later){this.db.exec('ROLLBACK');return {ok:false,reason:'epoch-rollback'};}
   const next={count:this.trusted.count+1,head:H(this.trusted.head+'|'+JSON.stringify({id,epoch,head}))};
   this.db.prepare('INSERT INTO votes(id,epoch,head) VALUES (?,?,?)').run(id,epoch,head);
   this.db.prepare("UPDATE meta SET value=? WHERE name='head'").run(next.head);
   this.db.prepare("UPDATE meta SET value=? WHERE name='count'").run(String(next.count));
   this.db.exec('COMMIT');this.trusted=next;return {ok:true,previous:false,checkpoint:next};
  }catch(err){try{this.db.exec('ROLLBACK')}catch{}throw err;}
 }
 close(){this.db.close();}
}