import {readFileSync} from 'node:fs';import {createPrivateKey,createPublicKey} from 'node:crypto';import {StrictCasWitness} from './p434_cas.mjs';
const c=JSON.parse(readFileSync(process.argv[2],'utf8'));
const witness=new StrictCasWitness(c.db,createPrivateKey(c.witnessPrivate),createPublicKey(c.witnessPublic),createPublicKey(c.ownerPublic));
const out=witness.cas(c.intent,{checkpoint(stage){if(stage===c.killAt){process.send?.({stage});Atomics.wait(new Int32Array(new SharedArrayBuffer(4)),0,0,60000)}}});
process.send?.({out});witness.close();