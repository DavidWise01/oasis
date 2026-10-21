'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm'),path=require('node:path');
const html=fs.readFileSync(path.join(__dirname,'../index.html'),'utf8');
const scope={window:{}};
for(const name of ['vessel-pipe-engine','exit-integrity-engine']){
 const code=html.match(new RegExp(`<script id="${name}">([\\s\\S]*?)<\\/script>`))?.[1];
 assert.ok(code,'Missing '+name);vm.runInNewContext(code,scope,{filename:name});
}
const P=scope.window.HarvesterVesselPipeV12,I=scope.window.HarvesterIntegrityV13;
let checks=0;const yes=(x,msg)=>{assert.ok(x,msg);checks++};
const ready={phase:'SECURED',clampAttached:true,interlocksReady:true,docked:true,fault:false};
function step(pair,act,t,opt={}){return I.command(pair.pipe,pair.integrity,act,{seed:opt.seed||pair.pipe.seed,witness:opt.witness||ready,tick:t,bit:opt.bit??0});}
function load(hex){let pair={pipe:P.defaults(),integrity:I.defaults()};pair=step(pair,'LOAD',1,{seed:hex});pair=step(pair,'IN',2);return pair}
let clean=load('01337AB4FF');yes(clean.pipe.phase==='IN_FLIGHT','input enters');
yes(I.compare(clean.pipe,clean.integrity).ready,'readback match');
clean=step(clean,'OUT',3);yes(clean.pipe.phase==='COMPLETE'&&clean.pipe.egress===1,'clean output');
yes(clean.integrity.delivered==='01337AB4FF','receiver hex losslessly delivered');
yes(clean.integrity.receipts.at(-1).sourceHex===clean.integrity.receipts.at(-1).receivedHex,'full 40-bit receipt');
clean=step(clean,'OUT',4);yes(clean.pipe.egress===1,'no duplicate output');
let a=load('ABCDE12345');a=step(a,'FLIP_A',3,{bit:17});yes(a.pipe.phase==='HELD'&&a.pipe.egress===0,'A fault holds');
yes(I.compare(a.pipe,a.integrity).badA.join(',')==='17','exact A bit identified');
a=step(a,'RESUME',4);yes(a.pipe.phase==='HELD','mismatch prevents resume');
a=step(a,'REPAIR',5);yes(I.compare(a.pipe,a.integrity).ready,'repair restores both');
a=step(a,'RESUME',6);yes(a.pipe.phase==='IN_FLIGHT','resume with valid witness');
a=step(a,'OUT',7);yes(a.integrity.delivered==='ABCDE12345','repaired egress exact');
let b=load('FFFFFFFFFF');b=step(b,'FLIP_B',4,{bit:39});yes(b.pipe.phase==='HELD','B fault held');
yes(I.compare(b.pipe,b.integrity).errorB===1,'B mismatch found');
let common=load('0000000000');common=step(common,'FLIP_A',3,{bit:4});common=step(common,'FLIP_B',4,{bit:4});
yes(common.integrity.readA===common.integrity.readB,'two flipped copies agree');
yes(!I.compare(common.pipe,common.integrity).ready,'common corruption still rejected against captured source');
common=step(common,'OUT',5);yes(common.pipe.egress===0,'common-mode corruption no false output');
let badGuard=load('A012345678');badGuard=step(badGuard,'OUT',3,{witness:{...ready,interlocksReady:false}});
yes(badGuard.pipe.phase==='HELD'&&badGuard.pipe.egress===0,'v12 interlock still enforced');
for(let n=0;n<4096;n++){
 const hex=(BigInt(n)*1099511627775n/4095n).toString(16).toUpperCase().padStart(10,'0');
 let pair=load(hex);
 const intact=I.compare(pair.pipe,pair.integrity);yes(intact.ready&&intact.matchingBits===40,'full exact readback');
 pair=step(pair,'OUT',4);yes(pair.integrity.delivered===hex,'40 bits output');
 for(const index of [0,7,8,15,16,23,24,31,32,39]){
  const flipped=I.flip(hex,index), aa=I.bits(hex), bb=I.bits(flipped);
  yes(aa.length===40&&bb.length===40,'fixed width 40');
  yes(I.diff(aa,bb).length===1&&I.diff(aa,bb)[0]===index,'flipped exact one bit');
  yes(I.flip(flipped,index)===hex,'reversible injection');
 }
}
let prior=load('55AA55AA55');prior=step(prior,'FLIP_A',3,{bit:0});prior=step(prior,'ABORT',4);
yes(prior.pipe.phase==='ABORTED'&&prior.pipe.egress===0,'abort preserves lack of egress');
yes(prior.integrity.delivered===null,'no invented delivered hex on abort');
for(let i=0;i<140;i++){prior=step(prior,'CLEAR',10+i*4);prior=step(prior,'LOAD',11+i*4,{seed:'0102030405'});prior=step(prior,'IN',12+i*4);prior=step(prior,'OUT',13+i*4)}
yes(prior.integrity.receipts.length<=96,'bounded integrity audit');
console.log('PASS',checks,'lossless 40-bit readback assertions; independent witness failures, common-mode rejection, safe holds');
