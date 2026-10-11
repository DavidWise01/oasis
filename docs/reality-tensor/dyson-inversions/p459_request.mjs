import {readFileSync} from 'node:fs';
import {createPrivateKey,createPublicKey} from 'node:crypto';
import {anchorRequest} from './p454_client.mjs';
const [cfgPath,action,nonce,epoch]=process.argv.slice(2);
const c=JSON.parse(readFileSync(cfgPath,'utf8'));
const res=await anchorRequest({port:c.port,deployment:c.deployment,clientPrivate:createPrivateKey(readFileSync(c.privateKey)),anchorPublic:createPublicKey(readFileSync(c.anchorPublic)),cert:readFileSync(c.cert),key:readFileSync(c.tlsKey),ca:readFileSync(c.ca)},action,null,nonce,Number(epoch));
console.log(JSON.stringify(res));