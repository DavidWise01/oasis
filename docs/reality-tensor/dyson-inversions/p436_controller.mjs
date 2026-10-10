import {fork} from 'node:child_process';
import {randomBytes,createPublicKey,verify} from 'node:crypto';
export const payload=x=>Buffer.from(JSON.stringify({domain:'ROOT0/P436/receipt',deployment:x.deployment,nonce:x.nonce,epoch:x.epoch,head:x.head}));
export function verifyReceipt(r,key,deployment){
 if(!r||r.deployment!==deployment||!/^[0-9a-f]{48}$/.test(r.nonce??'')||!Number.isSafeInteger(r.epoch)||!/^[0-9a-f]{64}$/.test(r.head??''))return false;
 try{return verify(null,payload(r),(key?.type==='public'?key:createPublicKey(key)),Buffer.from(r.signature,'base64'));}catch{return false;}
}
export class WitnessClient {
 constructor(path,config,publicKey,deployment){this.proc=fork(path,[config],{stdio:['ignore','ignore','pipe','ipc']});this.key=publicKey;this.deployment=deployment;this.pending=new Map();this.counter=0;this.live=true;this.proc.on('message',msg=>{if(msg?.ready){this.readyResolve?.();return;}const p=this.pending.get(msg.requestId);if(p){this.pending.delete(msg.requestId);p.resolve(msg);}});this.proc.on('exit',()=>{this.live=false;for(const p of this.pending.values())p.resolve({ok:false,reason:'witness-offline'});this.pending.clear();});this.ready=new Promise((resolve,reject)=>{this.readyResolve=resolve;this.proc.once('error',reject);});}
 async sign(epoch,head,{nonce=randomBytes(24).toString('hex'),timeoutMs=2000}={}){await this.ready;if(!this.live)return {ok:false,reason:'witness-offline'};const id=++this.counter;const request={deployment:this.deployment,nonce,epoch,head};const promise=new Promise(resolve=>{this.pending.set(id,{resolve});this.proc.send({action:'SIGN',requestId:id,request});});const response=await Promise.race([promise,new Promise(resolve=>setTimeout(()=>resolve({ok:false,reason:'timeout'}),timeoutMs))]);this.pending.delete(id);if(!response.ok)return response;return verifyReceipt(response.receipt,this.key,this.deployment)?response:{ok:false,reason:'invalid-signature'};}
 kill(){this.proc.kill('SIGKILL');}
}
