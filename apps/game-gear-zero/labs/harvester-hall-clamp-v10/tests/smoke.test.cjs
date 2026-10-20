#!/usr/bin/env node
'use strict';
const fs=require('fs'),vm=require('vm'),assert=require('assert/strict'),path=require('path');
const html=fs.readFileSync(path.join(__dirname,'..','index.html'),'utf8'),env={window:{}};
for(const name of ['gyro-engine','sea-cable-engine','pulsar-ground-engine','bearing-engine','harvester-engine']){
 const match=html.match(new RegExp('<script id="'+name+'">([\\s\\S]*?)<\\/script>'));
 assert.ok(match, 'missing '+name);vm.runInNewContext(match[1],env,{filename:name});
}
const {GyroMath:M,SeaCableMath:SEA,PulsarGroundMath:PG,CenterBearingMath:B,HarvesterV10:H}=env.window;
const input={rates:{...M.DEFAULT_RATES},levels:{G:3,R:3,B:3,P:3},zSlip:0};
function witness(cycle,overrides={}){
 const c={...SEA.defaults(),...overrides.c},bh={...PG.defaults(),...overrides.bh};
 const g=PG.sample(input,cycle,c,bh),b=B.sample(cycle,{...B.defaults(),...overrides.bearing},g.sunResidual);
 return H.sample({g,b,c,bh},cycle,overrides.sensors||{});
}
assert.equal(H.rails.length,19);assert.equal(new Set(H.rails.map(r=>r.id)).size,19);
assert.ok(H.rails.every(r=>r.pattern==='-+000+-'));
assert.equal(H.rails.filter(r=>r.visualOnly).length,6);
const w=witness(1.25);assert.equal(w.virtualPositions,57);assert.equal(w.simulatedPositions,39);
assert.ok(w.ready,'nominal ready');
let s=H.defaults();
for(let i=1;i<=6;i++)s=H.step(s,'NEXT',witness(1.25+i/64));
assert.equal(s.phase,'SECURED');assert.equal(s.count,2);assert.equal(s.clampAttached,true);
const open=witness(1.38,{sensors:{faultRail:'HR11'}});
assert.ok(!open.ready&&open.failures.includes('sensors'));
s=H.step(s,'MONITOR',open);assert.equal(s.phase,'SAFE_HOLD');assert.equal(s.clampAttached,true);
s=H.step(s,'RESET',witness(1.40));assert.equal(s.phase,'SAFE_HOLD');
s=H.step(s,'RELEASE',witness(1.42));assert.equal(s.phase,'RELEASE');
s=H.step(s,'NEXT',witness(1.44));assert.equal(s.phase,'COMPLETE');assert.equal(s.clampAttached,false);
assert.ok(s.receipts.every(r=>/^[a-f0-9]{8}$/.test(r.witnessDigest)));
for(let i=0;i<100;i++)s=H.step(s,'NEXT',witness(2+i/64));
assert.ok(s.receipts.length<=96 && s.seq>96);
const original=B.sample(1.25,B.defaults());assert.equal(original.gEquivalent,1);assert.ok(Math.abs(original.energyResidual)<1e-12);
console.log('PASS: 19 rails, 57 virtual positions, clamp sequence, latched hold, safe retract and v8 regression');
