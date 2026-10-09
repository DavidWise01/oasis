import assert from 'node:assert/strict';
import {keypair,ledger,verifyVote,equivocation} from './p359_witness.mjs';
const ws=Array.from({length:4},(_,i)=>({id:'w'+i,...keypair()}));const keys=new Map(ws.map(w=>[w.id,w.publicKey]));
const cp=(epoch,head)=>({context:'oasis/main',epoch,length:1440,head:head.repeat(64)});
let assertions=0;const check=(cond)=>{assert.ok(cond);assertions++;};
for(let i=0;i<4;i++){const w=ws[i],l=ledger(),a=l.vote(w.id,cp(1,'a'),w.privateKey);check(a.ok&&verifyVote(a.vote,keys));check(l.vote(w.id,cp(1,'a'),w.privateKey).duplicate);check(l.vote(w.id,cp(1,'b'),w.privateKey).reason==='double-vote');const restarted=ledger(l.snapshot());check(restarted.vote(w.id,cp(1,'b'),w.privateKey).reason==='double-vote');check(restarted.vote(w.id,cp(2,'b'),w.privateKey).ok);}
const a=ledger(),b=ledger(),w=ws[0],first=a.vote(w.id,cp(7,'a'),w.privateKey).vote,second=b.vote(w.id,cp(7,'b'),w.privateKey).vote;
check(equivocation(first,second,keys));check(!equivocation(first,first,keys));check(!equivocation(first,{...second,signature:'broken'},keys));
const left=[0,1,2].map(i=>ledger().vote(ws[i].id,cp(9,'a'),ws[i].privateKey).vote);
const right=[1,2,3].map(i=>ledger().vote(ws[i].id,cp(9,'b'),ws[i].privateKey).vote);
check(left.every(x=>verifyVote(x,keys))&&right.every(x=>verifyVote(x,keys)));
check(equivocation(left[1],right[0],keys));check(equivocation(left[2],right[1],keys));
console.log(JSON.stringify({status:'PASS',assertions,quorum:3,witnesses:4,overlapEquivocators:2}));