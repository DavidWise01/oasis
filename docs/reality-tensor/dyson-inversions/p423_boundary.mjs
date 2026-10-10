import {readFile,realpath,stat} from 'node:fs/promises';
import {createPublicKey,createHash} from 'node:crypto';
import {resolve,sep} from 'node:path';
import {PinnedWitnessGuard} from './p422_guard.mjs';
const inside=(p,root)=>p===root||p.startsWith(root+sep);
export async function validateDeployment(config){
 const {controllerRoot,witnessRoot,controllerDb,pinnedWitnessPublicKey,caCert,clientCertificate,clientPrivateKey,deployment}=config;
 if(!deployment||!/^[a-zA-Z0-9_/.:-]{3,128}$/.test(deployment))throw Error('invalid-deployment');
 const ctrl=await realpath(controllerRoot),wit=await realpath(witnessRoot);
 if(inside(ctrl,wit)||inside(wit,ctrl))throw Error('trust-roots-overlap');
 for(const [name,p] of [['clientPrivateKey',clientPrivateKey],['clientCertificate',clientCertificate],['caCert',caCert]]){
  const real=await realpath(p);if(!inside(real,ctrl))throw Error(name+'-outside-controller-root');
 }
 const dbParent=await realpath(resolve(controllerDb,'..'));
 if(!inside(dbParent,ctrl))throw Error('controller-db-outside-controller-root');
 const key=createPublicKey(await readFile(pinnedWitnessPublicKey,'utf8'));
 if(!inside(await realpath(pinnedWitnessPublicKey),ctrl))throw Error('pin-outside-controller-root');
 const witnessKey=await readFile(pinnedWitnessPublicKey,'utf8');
 if(!witnessKey.includes('BEGIN PUBLIC KEY'))throw Error('pin-not-public-key');
 const perms=await stat(clientPrivateKey);if((perms.mode&0o077)!==0)throw Error('client-key-not-private');
 return {ok:true,deployment,controllerRoot:ctrl,witnessRoot:wit,pinSha256:createHash('sha256').update(key.export({format:'der',type:'spki'})).digest('hex'),isolation:'directory-separation-only'};
}
export async function reconcilePinnedSnapshot({dbPath,deployment,pinnedPublicKey,response}){
 const guard=new PinnedWitnessGuard(dbPath,deployment,pinnedPublicKey);
 try{return guard.check(response)}finally{guard.close()}
}