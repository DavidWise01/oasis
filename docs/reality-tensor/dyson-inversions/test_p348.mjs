import assert from 'node:assert/strict';
import {RADICES,AXES,CAPACITY,TOTAL,encodeSphere,decodeSphere,encode,decode,motion} from './p348_six_axes.mjs';
assert.equal(CAPACITY,83160);assert.equal(TOTAL,498960);assert.equal(AXES.length,6);
let checked=0;
for(let i=0;i<TOTAL;i++){const a=decode(i);assert.equal(encode(a.axis,a.sphere),i);assert.equal(encodeSphere(a.digits),a.sphere);assert.deepEqual(a.digits.slice(-2),[0,0]);assert.equal(a.root,0);checked++;}
for(let a=0;a<6;a++)for(let tick=0;tick<183*360*2;tick+=13){const m=motion(tick,a);assert.equal(m.shellTurn*183+m.shell,tick);assert.equal(m.torusTurn*360+m.torus,tick);assert.equal(m.root,0);}
assert.throws(()=>decode(TOTAL));assert.throws(()=>encode(6,0));assert.throws(()=>encodeSphere([...Array(9).fill(0),1,0]));
console.log(JSON.stringify({status:'PASS',axes:6,addresses:TOTAL,checked,shellPositionsAcrossAxes:183*6,torusPositionsAcrossAxes:360*6}));
