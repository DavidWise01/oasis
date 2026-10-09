import assert from 'node:assert/strict';
import {items,append,checkpoint} from './p355_chain.mjs';
import {witness} from './p357_quorum.mjs';
import {acceptVerified} from './p358_integrated.mjs';
import {sign} from 'node:crypto';
const witnesses=Array.from({length:4},(_,i)=>witness('w'+i));
const authorized=new Map(witnesses.map(w=>[w.id,w.publicKey]));
function signed(cp,epoch,subset){const stamp={context:'oasis/main',epoch,...cp};const payload=Buffer.from(JSON.stringify({domain:'ROOT0-P357-v1',context:stamp.context,epoch:stamp.epoch,length:stamp.length,head:stamp.head}));return {stamp,votes:subset.map(i=>({id:witnesses[i].id,signature:sign(null,payload,witnesses[i].privateKey).toString('base64')}))};}
let assertions=0;function check(predicate){assert.ok(predicate);assertions++;}
const reports=[];
for(const envelope of ['total','boxy','circle']){
 const all=[...items(envelope,47,42,1440,16)];
 const base=append([],all.slice(0,720)),good=append(base,all.slice(720));
 const trusted={context:'oasis/main',epoch:1,...checkpoint(base)};
 const cert=signed(checkpoint(good),2,[0,1,2]);
 check(acceptVerified(good,cert.stamp,cert.votes,authorized,trusted).ok);
 const mutated=structuredClone(good);mutated[1100].item.root=1;
 check(acceptVerified(mutated,cert.stamp,cert.votes,authorized,trusted).reason.startsWith('chain-'));
 check(!acceptVerified(good.slice(0,-1),cert.stamp,cert.votes,authorized,trusted).ok);
 const twoVotes=signed(checkpoint(good),2,[0,1]);
 check(acceptVerified(good,twoVotes.stamp,twoVotes.votes,authorized,trusted).reason==='quorum');
 const fork=append(base,[...items(envelope,46,42,1440,16)].slice(720));
 const forkCert=signed(checkpoint(fork),2,[1,2,3]);
 check(acceptVerified(fork,forkCert.stamp,forkCert.votes,authorized,trusted).ok);
 const newerTrusted={context:'oasis/main',epoch:2,...checkpoint(good)};
 const forkLater=signed(checkpoint(fork),3,[1,2,3]);
 check(acceptVerified(fork,forkLater.stamp,forkLater.votes,authorized,newerTrusted).reason==='non-descendant-fork');
 const tamperedMid=structuredClone(good);tamperedMid[800].hash='f'.repeat(64);
 check(!acceptVerified(tamperedMid,cert.stamp,cert.votes,authorized,trusted).ok);
 check(acceptVerified(append([...base],all.slice(720)),cert.stamp,cert.votes,authorized,trusted).ok);
 reports.push({envelope,records:good.length,competingQuorumsPossible:true});
}
console.log(JSON.stringify({status:'PASS',assertions,records:4320,reports}));
