#!/usr/bin/env node
'use strict';
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict'),path=require('node:path');
const html=fs.readFileSync(path.resolve(__dirname,'../index.html'),'utf8');
const ctx={window:{}};let count=0;
for(const name of ['gyro-engine','sea-cable-engine','pulsar-ground-engine','bearing-engine','harvester-engine','harvester-motion-engine']){
 const m=html.match(new RegExp('<script id="'+name+'">([\\s\\S]*?)<\\/script>'));
 assert.ok(m,'missing '+name);vm.runInNewContext(m[1],ctx,{filename:name});
}
const {HarvesterV10:H10,HarvesterMotionV11:H11,GyroMath:M,SeaCableMath:SEA,PulsarGroundMath:PG,CenterBearingMath:BEAR}=ctx.window;
const cfg=H11.configDefaults(),zero=H11.defaults();
function verify(p,message){assert.ok(p,message);count++}
function hall(t=1.25){const input={rates:{...M.DEFAULT_RATES},levels:{G:3,R:3,B:3,P:3},zSlip:0};
 const c=SEA.defaults(),bh=PG.defaults(),g=PG.sample(input,t,c,bh),b=BEAR.sample(t,BEAR.defaults(),g.sunResidual);
 return H10.sample({g,b,c,bh},t);}
verify(H10.rails.length===19,'19 rails preserved');
verify(H11.witness(hall(),zero,cfg).ready===false,'position interlock blocks starting at x=0');
const dock=H11.advance(zero,cfg,'APPROACH',128);
verify(dock.position>.978&&Math.abs(dock.velocity)<.08,'powered dock reached');
verify(Math.abs(dock.ledgerError)<1e-9,'motor work and drag reconciled');
verify(H11.witness(hall(3.25),dock,cfg).ready,'9/9 interlocks');
let clamp=H11.control(H10,H10.defaults(),hall(3.25),zero,cfg,'NEXT');
verify(clamp.phase==='APPROACH','initiates approach');
verify(H11.control(H10,clamp,hall(3.25),zero,cfg,'NEXT').phase==='APPROACH','cannot skip motion');
for(let i=1;i<=5;i++)clamp=H11.control(H10,clamp,hall(3.25+i/64),dock,cfg,'NEXT');
verify(clamp.phase==='SECURED'&&clamp.clampAttached&&clamp.count===2,'secure requires two distinct ticks');
const overloaded=H11.witness(hall(3.5),dock,{...cfg,holdCapacity:.15});
clamp=H10.step(clamp,'MONITOR',overloaded);
verify(clamp.phase==='SAFE_HOLD'&&clamp.clampAttached,'overload latches attachment in safe hold');
clamp=H11.control(H10,clamp,hall(3.55),dock,cfg,'RESET');
verify(clamp.phase==='SAFE_HOLD'&&clamp.clampAttached,'reset cannot erase attachment');
clamp=H11.control(H10,clamp,hall(3.6),dock,cfg,'RELEASE');
verify(clamp.phase==='RELEASE','faulted attached clamp may retract');
verify(H11.control(H10,clamp,hall(3.65),dock,cfg,'NEXT').phase==='RELEASE','no instant release');
const home=H11.advance(dock,cfg,'RETRACT',128);
verify(home.position<.02&&Math.abs(home.velocity)<.08,'full retraction required');
verify(Math.abs(home.ledgerError)<1e-9,'retraction energy ledger');
clamp=H11.control(H10,clamp,hall(3.7),home,cfg,'NEXT');
verify(clamp.phase==='COMPLETE'&&!clamp.clampAttached,'completion only at home');
verify(H11.advance(zero,{...cfg,thrust:0},'APPROACH',256).position===0,'motor off stalls');
verify(H11.advance(zero,{...cfg,thrust:.2},'APPROACH',256).position===0,'insufficient thrust stalls');
console.log('PASS',count,'Harvester v11 smoke checks');
