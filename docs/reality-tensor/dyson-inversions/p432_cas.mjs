import {ExternalWitness} from './p430_guard.mjs';
import {verifyIntent} from './p431_intent.mjs';
import {verify,sign} from 'node:crypto';
export class CasWitness extends ExternalWitness {
 constructor(path,signKey,verifyKey,ownerPublic){super(path,signKey,verifyKey);this.ownerPublic=ownerPublic;this.db.exec('CREATE TABLE IF NOT EXISTS p432_intents(deployment TEXT NOT NULL,epoch INTEGER NOT NULL,nonce TEXT NOT NULL,nextHead TEXT NOT NULL,PRIMARY KEY(deployment,epoch),UNIQUE(deployment,nonce))');}
 cas(intent){
  if(!intent||typeof intent.deployment!=='string'||!Number.isSafeInteger(intent.epoch)||intent.epoch<1||typeof intent.priorHead!=='string'||!/^[a-f0-9]{64}$/.test(intent.priorHead)||typeof intent.nextHead!=='string'||!/^[a-f0-9]{64}$/.test(intent.nextHead)||!/^([a-f0-9]{32})$/.test(intent.nonce)||intent.priorHead===intent.nextHead||!verifyIntent(this.ownerPublic,intent))return {ok:false,reason:'invalid-signed-intent'};
  this.db.exec('BEGIN IMMEDIATE');
  try {
   const old=this.db.prepare('SELECT deployment,epoch,head,signature FROM p430_witness WHERE deployment=?').get(intent.deployment);
   if(!old||!verify(null,Buffer.from(JSON.stringify({domain:'ROOT0/P430/witness/v1',deployment:old.deployment,epoch:old.epoch,head:old.head})),this.verifyKey,Buffer.from(old.signature,'base64'))){this.db.exec('ROLLBACK');return {ok:false,reason:'missing-or-invalid-witness'};}
   const precedent=this.db.prepare('SELECT nonce,nextHead FROM p432_intents WHERE deployment=? AND epoch=?').get(intent.deployment,intent.epoch);
   if(precedent){this.db.exec('COMMIT');return precedent.nonce===intent.nonce&&precedent.nextHead===intent.nextHead&&old.epoch===intent.epoch&&old.head===intent.nextHead?{ok:true,duplicate:true,epoch:old.epoch}:{ok:false,reason:'conflicting-intent'};}
   if(old.epoch!==intent.epoch-1||old.head!==intent.priorHead){this.db.exec('ROLLBACK');return {ok:false,reason:'cas-precondition-failed'};}
   this.db.prepare('INSERT INTO p432_intents VALUES(?,?,?,?)').run(intent.deployment,intent.epoch,intent.nonce,intent.nextHead);
   const unsigned={domain:'ROOT0/P430/witness/v1',deployment:intent.deployment,epoch:intent.epoch,head:intent.nextHead};
   const signature=sign(null,Buffer.from(JSON.stringify(unsigned)),this.signKey).toString('base64');
   this.db.prepare('UPDATE p430_witness SET epoch=?,head=?,signature=? WHERE deployment=?').run(intent.epoch,intent.nextHead,signature,intent.deployment);
   this.db.exec('COMMIT');return {ok:true,epoch:intent.epoch,duplicate:false};
  }catch(e){try{this.db.exec('ROLLBACK')}catch{}throw e;}
 }
}