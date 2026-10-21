#!/usr/bin/env node
'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm'),path=require('node:path');
const html=fs.readFileSync(path.join(__dirname,'..','index.html'),'utf8'),context={window:{}};
for(const name of ['vessel-pipe-engine','exit-integrity-engine','dual-path-engine']){
 const m=html.match(new RegExp('<script id="'+name+'">([\\s\\S]*?)<\\/script>'));
 assert.ok(m,'missing '+name);vm.runInNewContext(m[1],context,{filename:name});
}
const P=context.window.HarvesterVesselPipeV12,I=context.window.HarvesterIntegrityV13,D=context.window.HarvesterDualPathV14;
let checks=0;
function ok(value,why){assert.ok(value,why);checks++;}
function eq(value,expect,why){assert.equal(value,expect,why);checks++;}
const def=D.configDefaults();
function initial(hex='01337AB4FF',cfg=def){return D.start(D.defaults(),hex,100,cfg);}
let s=initial();ok(!D.evaluate(s).ready,'not pre-delivered');
eq(s.paths.A.queue.length,5);eq(s.paths.B.queue.length,5);
s=D.advance(s,103);ok(s.paths.A.bytes.filter(x=>x!==null).length>0,'A arrived');
eq(s.paths.B.bytes.filter(x=>x!==null).length,0);
s=D.advance(s,111);ok(D.evaluate(s).ready,'both paths delivered intact');
eq(s.receipts.filter(r=>r.kind==='DELIVERED').length,10);
s=D.confirmOutput(s,112);ok(s.egressReceipt?.readA===s.egressReceipt?.readB,'matched output');
eq(D.confirmOutput(s,113).receipts.filter(r=>r.kind==='VERIFIED_EGRESS').length,1,'not duplicated');
let drop=D.advance(initial('ABCDE12345',{...def,modeB:'DROP',bitB:17}),115);
ok(!D.evaluate(drop).ready,'loss blocks output');
eq(D.evaluate(drop).bitsB,32,'four bytes cannot reconstruct forty bits');
eq(drop.paths.B.bytes[2],null,'selected byte still missing');
eq(D.confirmOutput(drop,116).egressReceipt,null,'no output from missing byte');
drop=D.advance(drop,1000);ok(!D.evaluate(drop).ready,'no spontaneous repair');
let rescue=D.retry(drop,'B',1001,def);
eq(rescue.paths.B.attempt,2,'explicit retry');ok(!D.evaluate(rescue).ready,'retry not instantaneous');
rescue=D.advance(rescue,1012);ok(D.evaluate(rescue).ready,'retransmitted path arrives');
let bad=D.advance(initial('0000000000',{...def,modeA:'FLIP',bitA:39}),120);
eq(D.evaluate(bad).errorsA,1);ok(!D.evaluate(bad).ready,'one wrong bit blocks output');
let common=D.advance(initial('FFFFFFFFFF',{...def,modeA:'FLIP',modeB:'FLIP',bitA:4,bitB:4}),120);
ok(common.paths.A.rxHex===common.paths.B.rxHex,'same corruption on both');
ok(!D.evaluate(common).ready,'must still compare original source');
let gone=D.discardSender(drop,1001);gone=D.retry(gone,'B',1002,def);
eq(gone.paths.B.attempt,1,'missing sender blocks retry');
ok(gone.receipts.some(r=>r.kind==='RETRY_DENIED'),'denied retry receipted');
for(let n=0;n<4096;n++){
 const hex=(BigInt(n)*1099511627775n/4095n).toString(16).toUpperCase().padStart(10,'0');
 const cfg={...def,delayA:1+n%14,delayB:1+(7*n)%23};
 const packet=initial(hex,cfg);
 ok(!D.evaluate(packet).ready,'queued not received');
 const p1=D.advance(packet,104);
 ok(p1.paths.A.bytes.every(v=>v===null||Number.isInteger(v)),'well-formed bytes');
 const p2=D.advance(p1,145),v=D.evaluate(p2);
 ok(v.ready,'both complete');eq(v.receivedA,hex,'exact A');eq(v.receivedB,hex,'exact B');
 eq(p2.receipts.filter(r=>r.kind==='DELIVERED').length,10,'ten arrivals');
 ok(p2.receipts.every(r=>/^[0-9a-f]{8}$/.test(r.hash)),'bounded deterministic checksum');
 const w={phase:'SECURED',clampAttached:true,interlocksReady:true,docked:true,fault:false};
 let old=P.transition(P.defaults(),'LOAD',{seed:hex,tick:1});
 old=P.transition(old,'IN',{tick:2,witness:w});
 ok(I.compare(old,{...I.defaults(),captured:hex,readA:v.receivedA,readB:v.receivedB}).ready,'v13 still checks every bit');
}
console.log('PASS '+checks+' deterministic independent software path checks');
