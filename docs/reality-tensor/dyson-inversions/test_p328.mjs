import assert from 'node:assert/strict';
import {MARKER_DEG,normalize,outerPoint,step,distanceDeg,audit} from './p328_torus_angles.mjs';
assert.equal(MARKER_DEG,183);assert.equal(step(183,1),184);assert.equal(step(183,177),0);
assert.equal(distanceDeg(183,184),1);assert.deepEqual(outerPoint(183),outerPoint(543));
let rng=0x328;const rnd=()=>{rng^=rng<<13;rng^=rng>>>17;rng^=rng<<5;return rng>>>0;};
for(let i=0;i<100000;i++){const a=rnd()%360,d=(rnd()%720)-360;assert.equal(distanceDeg(a,step(step(a,d),-d)),0);}
console.log(JSON.stringify({status:'PASS',cases:100000,...audit()}));
