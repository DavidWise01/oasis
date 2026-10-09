import assert from 'node:assert/strict';
import {items,append} from './p355_chain.mjs';
import {keypair,seal,authenticate,accept} from './p356_auth.mjs';
const {publicKey,privateKey}=keypair();const rogue=keypair();let assertions=0;
const report={};
for(const envelope of ['total','boxy','circle']){
 const elements=[...items(envelope,47,42,1440,64)];
 const initial=append([],elements.slice(0,720));const complete=append(initial,elements.slice(720));
 const sig0=seal(initial,1,privateKey);const sig1=seal(complete,2,privateKey);
 let trusted={context:'oasis/main',epoch:0,length:0,head:'0'.repeat(64)};
 let a=accept(initial,sig0,publicKey,trusted);assert.equal(a.verdict.ok,true);assertions++;trusted=a.trusted;
 a=accept(complete,sig1,publicKey,trusted);assert.equal(a.verdict.ok,true);assertions++;trusted=a.trusted;
 assert.equal(authenticate(complete,sig1,publicKey).ok,true);assertions++;
 assert.equal(accept(initial,sig0,publicKey,trusted).verdict.reason,'policy-or-replay');assertions++;
 const wrong=seal(complete,3,rogue.privateKey);assert.equal(authenticate(complete,wrong,publicKey).reason,'signature');assertions++;
 const forged={...sig1,head:'f'.repeat(64)};assert.equal(authenticate(complete,forged,publicKey).reason,'signature');assertions++;
 const branch=append(initial,[...elements.slice(720)].reverse());
 const forkSeal=seal(branch,3,privateKey);assert.equal(accept(branch,forkSeal,publicKey,trusted).verdict.reason,'non-descendant-fork');assertions++;
 const sameEpochDifferent=seal(initial,2,privateKey);assert.equal(accept(initial,sameEpochDifferent,publicKey,trusted).verdict.reason,'policy-or-replay');assertions++;
 const truncated=complete.slice(0,-1);assert.equal(authenticate(truncated,sig1,publicKey).ok,false);assertions++;
 assert.equal(authenticate(complete,{...sig1,context:'other'},publicKey).ok,false);assertions++;
 report[envelope]={records:complete.length,checkpointEpoch:trusted.epoch,replayRejected:true,rogueKeyRejected:true,forkRejected:true};
}
console.log(JSON.stringify({status:'PASS',assertions,report},null,2));
