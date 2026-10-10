import {DatabaseSync} from 'node:sqlite';
import {createHash} from 'node:crypto';
const digest=(e,h)=>createHash('sha256').update(`ROOT0/P421|${e}|${h}`).digest('hex');
export class ControllerStore {
 constructor(path,deployment){this.deployment=deployment;this.db=new DatabaseSync(path);this.db.exec('PRAGMA journal_mode=WAL; PRAGMA synchronous=FULL; CREATE TABLE IF NOT EXISTS control (deployment TEXT PRIMARY KEY,epoch INTEGER NOT NULL,head TEXT NOT NULL)');}
 read(){return this.db.prepare('SELECT epoch,head FROM control WHERE deployment=?').get(this.deployment)??null;}
 append(epoch,head){if(!Number.isSafeInteger(epoch)||epoch<0||typeof head!=='string'||!/^[a-f0-9]{64}$/.test(head))throw Error('invalid');const last=this.read();if(epoch!==(last?last.epoch+1:0))throw Error('gap');this.db.prepare('INSERT INTO control(deployment,epoch,head) VALUES(?,?,?) ON CONFLICT(deployment) DO UPDATE SET epoch=excluded.epoch,head=excluded.head').run(this.deployment,epoch,head);return {epoch,head};}
 reconcile(stamp){const local=this.read();if(!stamp)return {ok:false,reason:'anchor-unavailable'};if(!local)return {ok:false,reason:'local-uninitialized'};if(local.epoch<stamp.epoch)return {ok:false,reason:'controller-rollback'};if(local.epoch>stamp.epoch)return {ok:false,reason:'controller-ahead-recovery-required'};if(local.head!==stamp.digest)return {ok:false,reason:'fork'};return {ok:true,epoch:local.epoch};}
 close(){this.db.close()}
}
export const nextHash=digest;