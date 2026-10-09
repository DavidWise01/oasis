import assert from 'node:assert/strict';
import * as p from './p38_impedance_capture.mjs';
import * as old from './p37_dyson_scale.mjs';
let seed=0x38d1501;function rnd(){seed^=seed<<13;seed^=seed>>>17;seed^=seed<<5;return (seed>>>0)/4294967296;}
let maxRec=0,maxNorm=0,maxPower=0;
for(let k=0;k<12000;k++){
 const cfg={shells:1+Math.floor(rnd()*10),depth:rnd(),dtS:rnd()*1e-12,chargeSign:rnd()<.5?-1:1,startRadiusM:(100+rnd()*900)*1e-9};
 const initial=old.inputState(cfg),f=p.forward(initial,cfg),a=p.audit(cfg);
 maxRec=Math.max(maxRec,a.maxRecoveryError);maxNorm=Math.max(maxNorm,Math.abs(old.norm(f)-1));maxPower=Math.max(maxPower,a.maxPowerError);
 assert.ok(a.maxRecoveryError<1e-12 && Math.abs(old.norm(f)-1)<1e-12 && a.maxPowerError<1e-12);
 assert.ok(Math.abs(a.analytic.total-1)<1e-12);
 assert.ok(p.profile(cfg).every(x=>x.eta>=0&&x.eta<=1));
 const s=Array.from({length:cfg.shells+1},()=>[rnd()*2-1,rnd()*2-1]);
 const f2=p.forward(s,cfg),back2=p.inverse(f2,cfg);
 const err=Math.max(...s.flatMap((z,i)=>z.map((v,h)=>Math.abs(v-back2[i][h]))));
 assert.ok(err<1e-12);assert.ok(Math.abs(old.norm(s)-old.norm(f2))<1e-11);
}
const baseline=p.audit({shells:10,depth:1});
assert.equal(p.profile({shells:10,depth:0}).every(x=>x.eta===0),true);
console.log(JSON.stringify({status:'PASS',randomized:12000,maxRec,maxNorm,maxPower,baseline:{travel:baseline.analytic.travel,captured:1-baseline.analytic.travel,etaFirst:baseline.profile[0].eta,etaLast:baseline.profile[9].eta},scaledVoltageV:old.scaledPotentialV()},null,2));
