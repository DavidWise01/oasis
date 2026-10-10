import {DatabaseSync} from 'node:sqlite';
import {sign,verify,createHash} from 'node:crypto';
const hash=v=>createHash('sha256').update(v).digest('hex');
const encoded=x=>Buffer.from(JSON.stringify({domain:'ROOT0/P409/external-floor',sequence:x.sequence,cycle:x.cycle,digest:x.digest}));
export class ExternalFloor {
  constructor(path,signKey,verifyKey){this.db=new DatabaseSync(path,{timeout:15000});this.db.exec('PRAGMA journal_mode=WAL; PRAGMA synchronous=FULL; PRAGMA busy_timeout=15000; CREATE TABLE IF NOT EXISTS floor (id INTEGER PRIMARY KEY CHECK(id=1), sequence INTEGER NOT NULL,cycle INTEGER NOT NULL,digest TEXT NOT NULL,signature TEXT NOT NULL)');this.signKey=signKey;this.verifyKey=verifyKey;}
  latest(){return this.db.prepare('SELECT sequence,cycle,digest,signature FROM floor WHERE id=1').get()??null;}
  static verify(stamp,key){if(!stamp||!Number.isSafeInteger(stamp.sequence)||!Number.isSafeInteger(stamp.cycle)||!(/^[a-f0-9]{64}$/.test(stamp.digest))||typeof stamp.signature!=='string')return false;try{return verify(null,encoded(stamp),key,Buffer.from(stamp.signature,'base64'))}catch{return false;}}
  publish({sequence,cycle,digest},{failBeforeCommit=false}={}){
    if(!Number.isSafeInteger(sequence)||sequence<0||!Number.isSafeInteger(cycle)||cycle<0||!(/^[a-f0-9]{64}$/.test(digest)))throw Error('invalid floor');
    this.db.exec('BEGIN IMMEDIATE');try{const old=this.latest();if(old&&!ExternalFloor.verify(old,this.verifyKey)){this.db.exec('ROLLBACK');return {ok:false,reason:'invalid-stored-signature'}}
      if(old&&(sequence<old.sequence||cycle<old.cycle)){this.db.exec('ROLLBACK');return {ok:false,reason:'rollback'}}
      if(old&&sequence===old.sequence){this.db.exec('COMMIT');return {ok:old.digest===digest&&old.cycle===cycle,duplicate:true,reason:old.digest===digest&&old.cycle===cycle?'duplicate':'fork',stamp:old}}
      const unsigned={sequence,cycle,digest},stamp={...unsigned,signature:sign(null,encoded(unsigned),this.signKey).toString('base64')};
      this.db.prepare('INSERT INTO floor(id,sequence,cycle,digest,signature) VALUES(1,?,?,?,?) ON CONFLICT(id) DO UPDATE SET sequence=excluded.sequence,cycle=excluded.cycle,digest=excluded.digest,signature=excluded.signature').run(sequence,cycle,digest,stamp.signature);
      if(failBeforeCommit)throw Error('injected-before-commit');this.db.exec('COMMIT');return {ok:true,duplicate:false,stamp};
    }catch(e){try{this.db.exec('ROLLBACK')}catch{}return {ok:false,reason:e.message}}
  }
  close(){this.db.close()}
}
export const digestReference=r=>hash(JSON.stringify({domain:'ROOT0/P407/reference',sequence:r.sequence,cycle:r.cycle,values:r.values}));
export function guardedPublish(local,external,reference,{failBeforeExternalCommit=false}={}){
  const floor=external.latest();if(floor&&!ExternalFloor.verify(floor,external.verifyKey))return {ok:false,reason:'untrusted-floor'};
  const here=local.latest();if(floor&&(!here||here.sequence<floor.sequence||(here.sequence===floor.sequence&&here.digest!==floor.digest)))return {ok:false,reason:'local-rollback-quarantine'};
  if(floor&&here.sequence>floor.sequence)return {ok:false,reason:'local-ahead-requires-authenticated-intent'};
  const chosen=local.accept(reference);if(!chosen.ok)return chosen;
  const result=external.publish({sequence:reference.sequence,cycle:reference.cycle,digest:digestReference(reference)},{failBeforeCommit:failBeforeExternalCommit});
  if(!result.ok)return {ok:false,reason:'external-publication-quarantine',cause:result.reason};
  return {ok:true,stamp:result.stamp,duplicate:chosen.duplicate};
}
export function reconcileOnly(local,external){const floor=external.latest(),here=local.latest();if(!floor||!ExternalFloor.verify(floor,external.verifyKey))return {ok:false,reason:'trusted-floor-unavailable'};if(!here)return {ok:false,reason:'local-missing'};if(here.sequence===floor.sequence&&here.digest===floor.digest)return {ok:true,status:'consistent'};return {ok:false,reason:here.sequence>floor.sequence?'local-ahead-requires-authenticated-intent':'rollback-or-fork'};}
