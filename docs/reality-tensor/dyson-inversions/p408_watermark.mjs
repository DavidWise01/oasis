import {DatabaseSync} from 'node:sqlite';
import {verify,createHash} from 'node:crypto';
const canonical=x=>Buffer.from(JSON.stringify({domain:'ROOT0/P407/reference',sequence:x.sequence,cycle:x.cycle,values:x.values}));
const digest=x=>createHash('sha256').update(canonical(x)).digest('hex');
export class PersistentReferenceGate {
 constructor(path,publicKey,{externalFloor=null}={}){
  this.db=new DatabaseSync(path,{timeout:15000});this.db.exec('PRAGMA journal_mode=WAL; PRAGMA synchronous=FULL; PRAGMA busy_timeout=15000; CREATE TABLE IF NOT EXISTS watermark (id INTEGER PRIMARY KEY CHECK(id=1), sequence INTEGER NOT NULL, cycle INTEGER NOT NULL, digest TEXT NOT NULL);');
  this.publicKey=publicKey;this.externalFloor=externalFloor;
 }
 latest(){return this.db.prepare('SELECT sequence,cycle,digest FROM watermark WHERE id=1').get()??null;}
 accept(reference){
  if(!reference||!Number.isSafeInteger(reference.sequence)||reference.sequence<0||!Number.isSafeInteger(reference.cycle)||!Array.isArray(reference.values)||reference.values.length!==7||reference.values.some(x=>typeof x!=='string'||!/^[-]?\d+$/.test(x))||typeof reference.signature!=='string')return {ok:false,reason:'invalid-reference'};
  let valid=false;try{valid=verify(null,canonical(reference),this.publicKey,Buffer.from(reference.signature,'base64'));}catch{}
  if(!valid)return {ok:false,reason:'invalid-signature'};
  const h=digest(reference);this.db.exec('BEGIN IMMEDIATE');
  try{
   const previous=this.latest(),floor=this.externalFloor;
   if(floor&&(!previous||previous.sequence<floor.sequence||(previous.sequence===floor.sequence&&previous.digest!==floor.digest))){this.db.exec('ROLLBACK');return {ok:false,reason:'external-floor-mismatch'};}
   if(previous&&(reference.sequence<previous.sequence||reference.cycle<previous.cycle)){this.db.exec('ROLLBACK');return {ok:false,reason:'rollback'};}
   if(previous&&reference.sequence===previous.sequence){this.db.exec('COMMIT');return {ok:previous.digest===h,duplicate:previous.digest===h,reason:previous.digest===h?'duplicate':'fork'};}
   if(previous&&reference.cycle<=previous.cycle){this.db.exec('ROLLBACK');return {ok:false,reason:'cycle-rollback'};}
   this.db.prepare('INSERT INTO watermark(id,sequence,cycle,digest) VALUES(1,?,?,?) ON CONFLICT(id) DO UPDATE SET sequence=excluded.sequence,cycle=excluded.cycle,digest=excluded.digest').run(reference.sequence,reference.cycle,h);
   this.db.exec('COMMIT');return {ok:true,duplicate:false,watermark:this.latest()};
  }catch(e){try{this.db.exec('ROLLBACK');}catch{}throw e;}
 }
 close(){this.db.close();}
}
