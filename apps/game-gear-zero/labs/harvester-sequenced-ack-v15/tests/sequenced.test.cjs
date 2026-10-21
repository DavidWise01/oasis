#!/usr/bin/env node
'use strict';
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict'),path=require('node:path');
const page=fs.readFileSync(path.join(__dirname,'..','index.html'),'utf8'),context={window:{}};
for(const name of ['vessel-pipe-engine','exit-integrity-engine','dual-path-engine','sequenced-transport-engine']){
 const fragment=page.match(new RegExp('<script id="'+name+'">([\\s\\S]*?)<\\/script>'));
 assert.ok(fragment,'missing pure model '+name);
 vm.runInNewContext(fragment[1],context,{filename:name});
}
const D=context.window.HarvesterSequencedTransportV15,c=D.configDefaults();let checks=0;
function ok(v,reason){assert.ok(v,reason);checks++}
function eq(a,b,reason){assert.equal(a,b,reason);checks++}
let s=D.start(D.defaults(),'01337AB4FF',100,c);
eq(s.txId,1);eq(s.paths.A.queue.length,5);eq(s.paths.B.queue.length,5);
ok(!D.evaluate(s).ready,'no packet pre-delivery');
s=D.advance(s,106);eq(D.evaluate(s).acksA,3);eq(D.evaluate(s).acksB,0);
s=D.advance(s,112);ok(D.evaluate(s).ready,'10 acknowledgements and exact payload');
s=D.confirmOutput(s,113);eq(s.egressReceipt.txId,1);eq(s.egressReceipt.acksA,5);eq(s.egressReceipt.acksB,5);
s=D.confirmOutput(s,114);eq(s.receipts.filter(x=>x.kind==='VERIFIED_EGRESS').length,1,'one egress');
let replay=D.replay(s,'A',115);replay=D.advance(replay,116);
ok(replay.receipts.some(x=>x.kind==='REPLAY_PACKET_REJECTED'),'replayed frame rejected');
let lost=D.start(D.defaults(),'ABCDE12345',100,{...c,ackModeB:'DROP_ONE'});
lost=D.advance(lost,112);eq(D.evaluate(lost).bitsB,40);eq(D.evaluate(lost).acksB,4);
ok(!D.evaluate(lost).ready,'complete data without one ACK is insufficient');
eq(D.confirmOutput(lost,113).egressReceipt,null);
lost=D.retry(lost,'B',114,c);eq(lost.paths.B.attempt,2);eq(D.evaluate(lost).acksB,0);
lost=D.advance(lost,126);ok(D.evaluate(lost).ready,'explicit retransmission ACKs complete');
let delayed=D.start(D.defaults(),'76543210FE',100,{...c,delayB:32});
delayed=D.advance(delayed,103);delayed=D.retry(delayed,'B',104,{...c,delayB:1});
delayed=D.advance(delayed,115);ok(D.evaluate(delayed).ready,'new attempt wins');
delayed=D.advance(delayed,140);
ok(delayed.receipts.some(x=>x.kind==='STALE_PACKET_REJECTED'&&x.lane==='B'&&x.attempt===1),'old attempt late packet blocked');
let oldAck=D.start(D.defaults(),'1111111111',100,{...c,delayA:1});
oldAck=D.advance(oldAck,101);oldAck=D.retry(oldAck,'A',102,{...c,delayA:4});
oldAck=D.advance(oldAck,105);
ok(oldAck.receipts.some(x=>x.kind==='STALE_ACK_REJECTED'),'old attempt ACK blocked');
let oldTransfer=D.start(D.defaults(),'FFFFFFFFFF',100,{...c,delayB:32});
oldTransfer=D.reset(oldTransfer,101);
let newTransfer=D.start(oldTransfer,'0000000000',102,{...c,delayA:1,delayB:1});
eq(newTransfer.txId,2);newTransfer=D.advance(newTransfer,150);
ok(newTransfer.receipts.some(x=>x.kind==='STALE_PACKET_REJECTED'&&x.txId===1),'old transfer blocked');
eq(D.evaluate(newTransfer).receivedA,'0000000000');eq(D.evaluate(newTransfer).receivedB,'0000000000');
let erased=D.start(D.defaults(),'FFFFFFFFFF',100,{...c,modeA:'DROP',bitA:0});
erased=D.discardSender(D.advance(erased,120),121);
erased=D.retry(erased,'A',122,c);eq(erased.paths.A.attempt,1);
ok(erased.receipts.some(x=>x.kind==='RETRY_DENIED'),'no source no invented bytes');
let aborted=D.abort(D.start(D.defaults(),'AAAAAAAAAA',100,c),101);
aborted=D.advance(aborted,140);ok(!D.evaluate(aborted).ready,'abort does not produce valid output');
for(let n=0;n<2048;n++){
 const hex=(BigInt(n)*0xFFFFFFFFFFn/2047n).toString(16).toUpperCase().padStart(10,'0');
 const opt={...c,delayA:1+n%31,delayB:1+(n*7)%31};
 let run=D.start(D.defaults(),hex,100,opt);ok(!D.evaluate(run).ready,'no eager ACK');
 run=D.advance(run,150);const score=D.evaluate(run);
 ok(score.ready,'both ACKed and exact');eq(score.receivedA,hex);eq(score.receivedB,hex);eq(score.acksA,5);eq(score.acksB,5);
 const out=D.confirmOutput(run,151);eq(out.egressReceipt.txId,run.txId);
 eq(out.receipts.filter(x=>x.kind==='ACK_ACCEPTED').length,10);
}
console.log('PASS '+checks+' v15 deterministic ACK/attempt/replay/source checks');
