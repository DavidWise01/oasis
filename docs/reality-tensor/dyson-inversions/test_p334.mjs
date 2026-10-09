import assert from 'node:assert/strict';
import {MODEL,PERIOD,spinor,scalarState,point,normalized,majorBodies,minorBodies} from './p334_galactic_scalar.mjs';
assert.equal(PERIOD,1464);assert.deepEqual(MODEL.origin,[0,0,0]);
for(const [n,s] of [[0,-1],[366,1],[732,-1],[1098,1]])assert.equal(spinor(n).orientation,s);
for(let i=0;i<PERIOD;i++){const s=spinor(i);assert.equal(s.hop*366+s.offset,i);assert.notEqual(s.left,s.right);assert.ok(s.torusAngleRad>=0&&s.torusAngleRad<2*Math.PI);}
for(const b of [...majorBodies,...minorBodies])for(const t of [0,1e5,1e6,1e7]){const p=point(b,t);assert.ok(Math.abs(Math.hypot(p[0],p[1])-b.r)<1e-7);assert.ok(normalized(b,t).every(Number.isFinite));if(b.periodYears){const q=point(b,t+b.periodYears);assert.ok(Math.hypot(p[0]-q[0],p[1]-q[1])<1e-6);}}
assert.deepEqual(scalarState(1463,1e6).root,[0,0,0]);assert.throws(()=>spinor(1464));
console.log(JSON.stringify({status:'PASS',steps:PERIOD,major:majorBodies.length,minor:minorBodies.length,solarScale:0.52}));
