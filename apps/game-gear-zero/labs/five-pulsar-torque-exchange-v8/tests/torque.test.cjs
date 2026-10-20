#!/usr/bin/env node
'use strict';
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict');
const html=fs.readFileSync(path.join(__dirname,'..','index.html'),'utf8');
const found=html.match(/<script id="bearing-engine">([\s\S]*?)<\/script>/);
assert.ok(found,'live torque model is present');
const sandbox={window:{}};vm.runInNewContext(found[1],sandbox);
const B=sandbox.window.CenterBearingMath;let checks=0;
function ok(p,msg){assert.ok(p,msg);checks++}
function near(v,goal=0,tol=1e-9,name='match'){ok(Number.isFinite(v)&&Math.abs(v-goal)<=tol,name+': '+v+' vs '+goal)}
const nominal=B.defaults();
for(let j=0;j<=2048;j++){
 const b=B.sample(j/256,nominal);
 near(b.ringRate,-1,1e-12,'nominal CW ring');
 near(b.sunRate,1,1e-12,'nominal CCW sun');
 near(b.torque,0,1e-12,'zero active torque at equilibrium');
 near(b.energyResidual,0,1e-10,'energy ledger');
 near(b.momentumResidual,0,1e-10,'momentum ledger');
 near(b.gEquivalent,1,1e-12,'balance proxy');
}
const release=B.anchor(nominal,.25,{ringRate0:0,sunRate0:0});
near(B.sample(.25,release).kinetic,0);
ok(B.sample(.25,release).gEquivalent<.5,'release is unlocked');
const after=B.sample(1.25,release);
ok(after.ringRate<-.99&&after.sunRate>.99,'powered release rotates the pair oppositely');
near(after.ringRate+after.sunRate,0,1e-12,'internal drive cannot create net momentum');
near(after.driveWork,after.kinetic,1e-9,'motor pays the energy cost');
near(after.energyResidual,0,1e-9,'released energy ledger');
const kick=B.anchor(nominal,.5,{ringRate0:-.32,sunRate0:.72});
const open=B.anchor(kick,.5,{groundConnected:false});
const grounded=B.anchor(kick,.5,{groundConnected:true});
const start=B.sample(.5,open),p1=B.sample(2.5,open),p2=B.sample(2.5,grounded);
ok(p1.counterspinError<start.counterspinError/100,'torque fixes relative spin even without ground');
near(p1.commonDrift,.2,1e-12,'disconnected ground leaves shared drift');
ok(p1.gEquivalent<.75,'drift prevents false total lock');
ok(p2.commonDrift<.01,'connected ground suppresses shared drift');
ok(p2.gEquivalent>.97,'full lock is recovered with ground');
ok(p2.groundHeat>0,'ground dissipates kinetic energy');
ok(p2.groundMomentum>.35,'ground receives angular momentum');
for(let j=0;j<=1024;j++){
 const t=.5+j/256;
 for(const c of [open,grounded,release]){
  const b=B.sample(t,c);
  near(b.energyResidual,0,1e-9,'energy conserved incl motor work and heat');
  near(b.momentumResidual,0,1e-9,'angular momentum ledger');
  near(b.ringRate+b.sunRate+b.groundMomentum,c.historyAngular0,1e-9,'pair+ground total momentum');
  ok(b.gEquivalent>0&&b.gEquivalent<=1,'bounded balance indicator');
 }
}
const off=B.anchor(release,.25,{gain:0});
near(B.sample(2,off).ringRate,0);
near(B.sample(2,off).sunRate,0);
const old=B.sample(1.25,grounded);
const tuned=B.sample(1.25,B.anchor(grounded,1.25,{gain:3.5}));
near(tuned.ringAngle,old.ringAngle,1e-9,'no ring angle teleport');
near(tuned.sunAngle,old.sunAngle,1e-9,'no sun angle teleport');
near(tuned.kinetic,old.kinetic,1e-9,'no kinetic jump');
console.log('PASS '+checks+' deterministic rotor/energy/momentum checks');
