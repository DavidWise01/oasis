import {DurableVerifier} from './p426_core.mjs';
import {randomBytes} from 'node:crypto';

export class QuotaVerifier extends DurableVerifier {
 constructor(path,key,deployment,{maxOutstanding=64,maxAgeMs=60000,retentionMs=120000,maxIssuesPerWindow=128,windowMs=60000}={}){
  super(path,key,deployment,{maxAgeMs});
  if(![maxOutstanding,maxAgeMs,retentionMs,maxIssuesPerWindow,windowMs].every(x=>Number.isSafeInteger(x)&&x>0))throw Error('invalid-limits');
  this.maxOutstanding=maxOutstanding;this.retentionMs=retentionMs;this.maxIssuesPerWindow=maxIssuesPerWindow;this.windowMs=windowMs;
  this.db.exec('CREATE TABLE IF NOT EXISTS p427_issues(deployment TEXT NOT NULL, issued INTEGER NOT NULL); CREATE INDEX IF NOT EXISTS p427_issues_idx ON p427_issues(deployment,issued); CREATE INDEX IF NOT EXISTS p426_pending_cleanup_idx ON p426_pending(issued,consumed)');
 }
 cleanup(now=Date.now()){
  this.db.exec('BEGIN IMMEDIATE');
  try{const r=this._prune(now);this.db.exec('COMMIT');return r;}catch(e){this.db.exec('ROLLBACK');throw e;}
 }
 _prune(now){
  const deleted=this.db.prepare('DELETE FROM p426_pending WHERE issued < ?').run(now-Math.max(this.maxAgeMs,this.retentionMs)).changes;
  const oldIssues=this.db.prepare('DELETE FROM p427_issues WHERE issued < ?').run(now-this.windowMs).changes;
  const expired=this.db.prepare('UPDATE p426_pending SET consumed=1 WHERE consumed=0 AND issued < ?').run(now-this.maxAgeMs).changes;
  return {deleted,oldIssues,expired};
 }
 issue(){
  const now=Date.now();this.db.exec('BEGIN IMMEDIATE');
  try{
   this._prune(now);
   const rate=this.db.prepare('SELECT COUNT(*) AS n FROM p427_issues WHERE deployment=? AND issued>=?').get(this.deployment,now-this.windowMs).n;
   const outstanding=this.db.prepare('SELECT COUNT(*) AS n FROM p426_pending WHERE consumed=0').get().n;
   if(rate>=this.maxIssuesPerWindow||outstanding>=this.maxOutstanding){this.db.exec('ROLLBACK');return {ok:false,reason:rate>=this.maxIssuesPerWindow?'rate-limit':'outstanding-limit'};}
   const nonce=randomBytes(24).toString('hex');
   this.db.prepare('INSERT INTO p426_pending(nonce,issued) VALUES(?,?)').run(nonce,now);
   this.db.prepare('INSERT INTO p427_issues(deployment,issued) VALUES(?,?)').run(this.deployment,now);
   this.db.exec('COMMIT');return {ok:true,deployment:this.deployment,nonce};
  }catch(e){try{this.db.exec('ROLLBACK')}catch{}throw e;}
 }
 counts(){return {outstanding:this.db.prepare('SELECT COUNT(*) AS n FROM p426_pending WHERE consumed=0').get().n,pendingRows:this.db.prepare('SELECT COUNT(*) AS n FROM p426_pending').get().n,windowIssues:this.db.prepare('SELECT COUNT(*) AS n FROM p427_issues WHERE deployment=?').get(this.deployment).n};}
}