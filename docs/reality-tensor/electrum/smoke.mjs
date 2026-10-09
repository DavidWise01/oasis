import assert from 'node:assert/strict';
import * as M from './electrum_fcc.mjs';
import * as C from './upstream/cipher208.mjs';
const f=M.buildFCC(),a=M.latticeAudit(f),base=M.opticalBoundary();
const near=(a,b,e=1e-9)=>Math.abs(a-b)<=e*Math.max(1,Math.abs(a),Math.abs(b));
assert.equal(f.sites.length,4000);
assert.equal(f.nAu,2693);assert.equal(f.nAg,1307);
assert.equal(a.degree,12);assert.equal(a.directedBonds,48000);
assert.equal(a.undirectedBonds,24000);assert.equal(a.neighborDefects,0);
assert.equal(a.inversionBrokenSpecies,1800);
assert.equal(M.buildFCC({compositionBasis:'atomic'}).nAu,3160);
assert(near(base.T,0.1747882615538272));assert(near(base.R,0.594308254619312));
assert(near(base.T+base.R+base.A,1));
assert.equal(base.bulkPockelsPhaseRad,0);
assert.throws(()=>M.requireBulkPockels({centrosymmetricAverage:true,pockelsCoefficientMPerV:30e-12}));
assert(M.opticalBoundary({kappa:2}).T!==M.opticalBoundary({kappa:4}).T);
for(let j=0;j<1000;j++){
 const p={voltageV:-.211,referenceV:0,gapM:(j%37+1)*1e-6,surfaceResponseRadPerV:(j%17)/4};
 const d=Math.sin(j)*1e3;
 const v=M.opticalBoundary(p);
 const w=M.opticalBoundary({...p,voltageV:p.voltageV+d,referenceV:d});
 assert(near(v.surfacePhaseRad,w.surfacePhaseRad));
 assert(near(v.externalFieldVPerM,w.externalFieldVPerM));
}
const c=new C.Cipher208();for(let j=0;j<208;j++)c.forward();
c.beginMirroredReverse();for(let j=0;j<208;j++)c.backward();
assert(c.recovered());assert.equal(c.totalEvents,417);
console.log(JSON.stringify({status:'PASS',sites:4000,fccBonds:24000,gaugeChecks:1000,fullCipherRecovered:true,bulkPockels:false}));
