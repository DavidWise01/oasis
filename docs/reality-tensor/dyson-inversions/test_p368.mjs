import assert from 'node:assert/strict';
import {TrustedAnchor,FivePlusOne,LANES,TOPOLOGY} from './p368_signed_five_plus_one.mjs';
let count=0;const yes=(x)=>{assert.ok(x);count++};
const anchor=new TrustedAnchor(),sys=new FivePlusOne(anchor),req=(epoch,head,signs=[-1,1,-1,1,-1])=>({identity:'w0',epoch,head:head.repeat(64),signs});
yes(TOPOLOGY==='-+5 + 1');yes(LANES.length===5);
yes(sys.request(req(1,'a')).ok);yes(sys.request(req(1,'a')).ok);yes(!sys.request(req(1,'b')).ok);
yes(sys.request(req(2,'b')).ok);yes(sys.request(req(2,'b',[1,-1,1,-1,1])).ok);yes(!sys.request(req(2,'c')).ok);
const prior=anchor.checkpoint();const restarted=new FivePlusOne(anchor);
yes(!restarted.request(req(1,'d')).ok);yes(anchor.checkpoint()===prior);
const wiped=new FivePlusOne(new TrustedAnchor());yes(wiped.request(req(1,'d')).ok);
for(let i=0;i<10000;i++){const epoch=10+i,head=(i%16).toString(16);yes(sys.request(req(epoch,head)).ok);yes(!sys.request(req(epoch,(i%16===15?0:i%16+1).toString(16))).ok);}
assert.throws(()=>sys.request(req(3,'a',[1,1])));count++;
console.log(JSON.stringify({status:'PASS_WITH_TRUST_BOUNDARY',assertions:count,topology:TOPOLOGY,laneCount:5,anchorCount:1,authorityLossVulnerable:true}));