import {readFile} from 'node:fs/promises';
import {createPublicKey} from 'node:crypto';
import {DeploymentRegistry} from './p412_deployment.mjs';
const data=JSON.parse(await readFile(process.argv[2],'utf8'));
const registry=new DeploymentRegistry({directory:data.registry,authorityFile:data.authority,operatorKey:createPublicKey(data.publicKey),deployment:data.deployment});
const result=await registry.initialize(data.grant,{abortAfterReserve:process.argv[3]==='after-reserve'});
if(process.send)process.send({ready:true,result});
if(process.argv[3]==='after-reserve')setInterval(()=>{},1000);