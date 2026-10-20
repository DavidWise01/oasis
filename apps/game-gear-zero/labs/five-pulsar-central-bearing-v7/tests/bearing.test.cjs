#!/usr/bin/env node
'use strict';
// Test the exact pure model embedded in the deployed single-file viewer.
const fs=require('node:fs'),vm=require('node:vm'),path=require('node:path'),assert=require('node:assert/strict');
const src=fs.readFileSync(path.join(__dirname,'../index.html'),'utf8');
const scripts=[...src.matchAll(/<script[^>]*>([\s\S]*?)<\/script>/g)];
const code=scripts.find(x=>x[0].includes('bearing-engine'))?.[1];
assert.ok(code,'Center bearing model present');
const context={window:{}};vm.runInNewContext(code,context);
const B=context.window.CenterBearingMath;
let checks=0;
function ok(value,msg){assert.ok(value,msg);checks++}
function near(x,target=0,tol=1e-9){ok(Math.abs(x-target)<=tol,x+' vs '+target)}
const nominal=B.defaults();
for(let i=0;i<=2400;i++){
 const t=i/240,p=B.sample(t,nominal);
 near(p.carrierRate,1);near(p.ringRate,-1);near(p.sunRate,1);
 near(p.error,0);near(p.gEquivalent,1);ok(p.locked,'baseline lock');
 near(p.ringAngle,-2*Math.PI*t);near(p.sunAngle,2*Math.PI*t);
}
const release=B.anchor(nominal,1,{ringRate0:0,sunRate0:0});
const atRest=B.sample(1,release);
near(atRest.ringRate,0);near(atRest.sunRate,0);ok(atRest.gEquivalent<.5,'rest is not locked');
let last=0;
for(let i=1;i<=700;i++){
 const next=B.sample(1+i/350,release);
 ok(next.gEquivalent>=last,'monotonic recovery');
 ok(next.ringRate<=0&&next.sunRate>=0,'opposed spin');
 last=next.gEquivalent;
}
ok(B.sample(3,release).gEquivalent>.98,'natural feedback convergence in model');
near(B.sample(3,B.anchor(release,3,{ringRate0:-1,sunRate0:1})).error,0);
const kicked=B.anchor(nominal,.5,{ringRate0:-.32,sunRate0:.72});
const n0=B.sample(.5,kicked),n1=B.sample(.8,kicked),n2=B.sample(2.5,kicked);
ok(n0.gEquivalent<.6,'kick creates imbalance');
ok(n1.gEquivalent>n0.gEquivalent,'feedback responds without teleportation');
ok(n2.gEquivalent>.99,'eventual recovery');
near(n0.ringAngle,B.sample(.5,nominal).ringAngle);
const stress=B.sample(1,nominal,.5855),drained=B.sample(1,nominal,.1355);
ok(stress.gEquivalent<1,'sun stress contributes');
ok(drained.gEquivalent>stress.gEquivalent,'ground lowers imbalance');
assert.ok(!src.includes('function drawClockwiseGyro'),'old outer satellite removed');
assert.ok(src.includes('drawCentralBearing(bearing)'),'new coaxial bearing visible');
console.log('PASS '+checks+' deterministic counterspin/recovery assertions');
