import {mkdir,open,readFile} from 'node:fs/promises';
import {join} from 'node:path';
import {createHash} from 'node:crypto';
import {validateGrant,GenesisAuthority} from './p410_genesis.mjs';
export const BLOCKADE='{-{+{%}+}-}';
const sha=x=>createHash('sha256').update(x).digest('hex');
const deploymentKey=id=>sha('ROOT0/P412/deployment/'+id);
export class DeploymentRegistry {
 constructor({directory,authorityFile,operatorKey,deployment}) {Object.assign(this,{directory,authorityFile,operatorKey,deployment});}
 static async provision(directory){await mkdir(directory,{recursive:true});let f;try{f=await open(join(directory,'PROVISIONED'),'wx',0o600);await f.writeFile('ROOT0:P412:ACTIVE\n');await f.sync();}finally{await f?.close();}}
 async initialize(grant,{abortAfterReserve=false}={}) {
  if(!validateGrant(grant,this.operatorKey,this.deployment))return {ok:false,reason:'invalid-grant'};
  try{if(await readFile(join(this.directory,'PROVISIONED'),'utf8')!=='ROOT0:P412:ACTIVE\n')return {ok:false,reason:'invalid-registry'};}catch{return {ok:false,reason:'registry-unavailable'};}
  let f;const record=join(this.directory,deploymentKey(this.deployment)+'.json');
  try{f=await open(record,'wx',0o600);}catch(e){return {ok:false,reason:e.code==='EEXIST'?'deployment-already-reserved':'registry-unavailable'};}
  try{
   await f.writeFile(JSON.stringify({deployment:this.deployment,grantHash:sha(grant.signature),stage:'reserved'})+'\n');await f.sync();
   const d=await open(this.directory,'r');try{await d.sync();}finally{await d.close();}
   if(abortAfterReserve)return {ok:false,reason:'injected-interruption-reservation-retained'};
   let a;try{a=GenesisAuthority.provision(this.authorityFile,this.operatorKey,this.deployment,grant);}catch(e){return {ok:false,reason:'local-provision-refused',detail:e.message};}
   try{return {ok:true,epoch:a.status().epoch};}finally{a.close();}
  }finally{await f.close();}
 }
}