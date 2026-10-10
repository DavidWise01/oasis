import {fork} from 'node:child_process';
import {verify,createPublicKey} from 'node:crypto';
const enc=x=>Buffer.from(JSON.stringify({domain:'ROOT0/P433/checkpoint/v1',deployment:x.deployment,epoch:x.epoch,head:x.head}));
export class CasProcessClient {
 constructor(worker,config,publicKey,deployment){
  this.key=publicKey?.type==='public'?publicKey:createPublicKey(publicKey);this.deployment=deployment;this.id=0;this.pending=new Map();this.alive=true;
  this.proc=fork(worker,[config],{stdio:['ignore','ignore','pipe','ipc']});
  this.ready=new Promise((resolve,reject)=>{this.onReady=resolve;this.proc.once('error',reject);});
  this.proc.on('message',m=>{if(m.ready){this.onReady();return;}const p=this.pending.get(m.id);if(p){this.pending.delete(m.id);p(m);}});
  this.proc.on('exit',()=>{this.alive=false;for(const p of this.pending.values())p({ok:false,reason:'witness-offline'});this.pending.clear();});
 }
 async request(action,intent){await this.ready;if(!this.alive)return {ok:false,reason:'witness-offline'};
  const id=++this.id;const result=await new Promise(resolve=>{this.pending.set(id,resolve);this.proc.send({id,action,intent});});
  if(result.ok&&result.stamp){const s=result.stamp;let v=false;try{v=s.deployment===this.deployment&&verify(null,enc(s),this.key,Buffer.from(s.signature,'base64'));}catch{}
   if(!v)return {ok:false,reason:'invalid-witness-receipt'};
  }
  return result;
 }
 kill(){this.proc.kill('SIGKILL');}
}