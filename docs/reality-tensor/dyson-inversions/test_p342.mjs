import assert from 'node:assert/strict';
import {COUNT,CONFIRMED,element,overlay,index,inverseIndex,C} from './p342_element_overlay.mjs';
let confirmed=0,hypothetical=0,count=0;
for(let z=1;z<=COUNT;z++){const e=element(z);if(e.status==='confirmed')confirmed++;else hypothetical++;for(let p=0;p<4;p++){const i=index(z,p),o=overlay(z,p,{hz:C/550e-9,amplitude:.5});assert.deepEqual(inverseIndex(i),{Z:z,primeIndex:p});assert.equal(o.root,0);assert.ok(Math.abs(o.spectrum.wavelengthM-550e-9)<1e-20);assert.equal(o.element.status,e.status);count++;}}
assert.equal(confirmed,CONFIRMED);assert.equal(hypothetical,66);assert.equal(count,736);assert.throws(()=>element(185));assert.throws(()=>overlay(119,4,{hz:1}));
console.log(JSON.stringify({result:'PASS',confirmed,hypothetical,carrierElementAddresses:count,physicalSpectrumAssignments:'none assumed'}));
