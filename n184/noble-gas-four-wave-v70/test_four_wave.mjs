import assert from 'node:assert/strict';
import {GASES,REFERENCE_NM,MODES,frequencyRatio,fieldAt,monitor} from './four_wave_model.mjs';
const tests=[];
function check(name,fn){fn();tests.push(name);}
const near=(a,b,tol=1e-12)=>assert.ok(Math.abs(a-b)<tol, `expected ${a} ~= ${b}`);
check('three verified spectral anchors + krypton',()=>{
  assert.deepEqual(GASES.map(g=>g.Z),[2,10,18,36]);
  assert.deepEqual(GASES.map(g=>g.nm),[587.56148,585.24878,696.5431,760.15457]);
  near(frequencyRatio(GASES[1]),1);
  assert.equal(MODES.length,3);assert.equal(REFERENCE_NM,585.24878);
});
check('zero-phase inverse cancels center across three distinct frequencies',()=>{
  for(let k=0;k<513;k++){
    const e=fieldAt(0,0,k/37,{mode:'cancel',reflectivity:.3,drive:1});
    near(e.firstThree+e.fourth,0);
    near(e.total,0);
  }
});
check('reinforce yields twice the three-port field at center',()=>{
  for(let k=0;k<257;k++){
    const e=fieldAt(0,0,k/41,{mode:'reinforce',reflectivity:.2,drive:1});
    near(e.fourth,e.firstThree);
    near(e.total,2*e.firstThree);
  }
});
check('krypton single line cannot cancel three frequencies over time',()=>{
  const m=monitor({mode:'krypton',reflectivity:.2,drive:1});
  assert.ok(m.rms>.05);
});
check('phase detuning breaks designed cancellation',()=>{
  const m=monitor({mode:'cancel',phaseDeg:35});
  assert.ok(m.rms>.03);
});
check('100% toy reflection prevents field and oscillator driving',()=>{
  for(const mode of MODES) {
    const m=monitor({mode,reflectivity:1});
    near(m.rms,0);near(m.peak,0);near(m.polarizationRms,0);
  }
});
check('zero drive prevents field',()=>{
  const m=monitor({mode:'reinforce',drive:0});
  near(m.rms,0);near(m.polarizationRms,0);
});
check('cancel center is a point, not a uniform spatial null',()=>{
  const e=fieldAt(.137,.23,.4,{mode:'cancel'});
  assert.ok(Math.abs(e.total)>1e-5);
});
check('inverse has zero core oscillator response in the idealized model',()=>{
  const m=monitor({mode:'cancel',phaseDeg:0});
  assert.ok(m.rms<1e-12 && m.polarizationRms<1e-12);
});
check('monitor produces reproducible, finite samples',()=>{
  const a=monitor({mode:'reinforce'}),b=monitor({mode:'reinforce'});
  assert.equal(a.history.length,768);
  assert.deepEqual(a,b);
  assert.ok(a.history.every(e=>Object.values(e).every(Number.isFinite)));
});
check('invalid parameters rejected',()=>{
  assert.throws(()=>fieldAt(0,0,0,{mode:'darkmatter'}),RangeError);
  assert.throws(()=>fieldAt(0,0,0,{reflectivity:2}),RangeError);
  assert.throws(()=>fieldAt(0,0,0,{drive:-1}),RangeError);
});
console.log(JSON.stringify({result:'PASS',passed:tests.length,failed:0,tests},null,2));
