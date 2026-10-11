import assert from 'node:assert/strict';
import {mkdtemp,rm} from 'node:fs/promises';import {tmpdir} from 'node:os';import {join} from 'node:path';
import {generateKeyPairSync} from 'node:crypto';
import {KernelZero,signIntent,signPolicy,signRequest} from './kernel0.mjs';
const dir=await mkdtemp(join(tmpdir(),'ke0-'));let assertions=0;
const chk=(x,label)=>{assert.ok(x,label);assertions++};
const w=generateKeyPairSync('ed25519'),a=generateKeyPairSync('ed25519'),o=generateKeyPairSync('ed25519'),c=generateKeyPairSync('ed25519');
const keys={deployment:'ke0',witnessPrivate:w.privateKey,witnessPublic:w.publicKey,adminPublic:a.publicKey,ownerPublic:o.publicKey,clients:{controller:c.publicKey}};
const db=join(dir,'state.db');let kernel;
try {
 kernel=new KernelZero(db,keys);
 chk(kernel.provisionGenesis('a'.repeat(64)).ok,'genesis');
 chk(kernel.provisionPolicy(signPolicy(a.privateKey,{deployment:'ke0',sequence:0,epoch:0,keys:['controller']})).ok,'policy');
 const s0=kernel.snapshot();chk(s0.ok&&s0.kernel===0&&s0.tracks.length===3,'three tracks');chk(s0.present.epoch===0&&s0.future===null,'genesis present');
 const intent=signIntent(o.privateKey,{deployment:'ke0',epoch:1,prior:'a'.repeat(64),next:'b'.repeat(64),nonce:'1'.repeat(32)});
 chk(kernel.snapshot({future:intent}).future.status==='candidate-uncommitted','future candidate');
 const req=signRequest(c.privateKey,{deployment:'ke0',keyId:'controller',policyEpoch:0,nonce:'2'.repeat(32),action:'CAS',intent});
 chk(kernel.dispatch(req).ok,'publish');chk(!kernel.dispatch(req).ok,'replay denied');
 const now=kernel.snapshot({past:s0.present});chk(now.ok&&now.past.epoch===0&&now.present.epoch===1,'past and present');
 chk(kernel.snapshot({future:{deployment:'ke0',epoch:3,prior:'b'.repeat(64)}}).reason==='invalid-future-intent','future jump denied');
 chk(kernel.snapshot({past:{deployment:'other',epoch:0}}).reason==='invalid-past','wrong past rejected');
 kernel.close();kernel=new KernelZero(db,keys);chk(kernel.snapshot().present.epoch===1,'restart persists');
 console.log(JSON.stringify({status:'PASS',assertions,kernel:'{{ | K . E | }}',tracks:3,temporalRegisters:['past','present','future'],independentHostVerified:false}));
}finally{kernel?.close();await rm(dir,{recursive:true,force:true});}