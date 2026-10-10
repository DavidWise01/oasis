import {readFileSync} from 'node:fs';
import {createPrivateKey,createPublicKey} from 'node:crypto';
import {StrictCasWitness} from './p434_cas.mjs';
const c=JSON.parse(readFileSync(process.argv[2],'utf8'));
const db=new StrictCasWitness(c.db,createPrivateKey(readFileSync(c.witnessKey)),createPublicKey(readFileSync(c.witnessPublic)),createPublicKey(readFileSync(c.ownerPublic)));
process.on('message',msg=>{
 let out;
 try{
  if(msg?.action==='READ')out=db.read(c.deployment);
  else if(msg?.action==='CAS')out=db.cas(msg.intent);
  else out={ok:false,reason:'unsupported-operation'};
  if(out?.ok&&!out.stamp){const current=db.read(c.deployment);if(current.ok)out={...out,stamp:current.stamp};}
 }catch(e){out={ok:false,reason:'internal-error',detail:e.message};}
 process.send?.({id:msg?.id,...out});
});
process.send?.({ready:true});