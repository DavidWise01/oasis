import assert from 'node:assert/strict';
import {AXES,encode,decode,promote,inverse} from './p345_geometry.mjs';
let checks=0;for(const d of [3,4,5]){for(let i=0;i<3**d;i++){const s=decode(d,i);assert.equal(s.root,0);assert.equal(encode(d,s.coords),i);assert.deepEqual(inverse(inverse(s.coords)),s.coords);if(d<5){let p=promote(d,s.coords);assert.deepEqual(decode(d+1,encode(d+1,p)).coords,p);}checks++;}}
assert.deepEqual(Object.values(AXES).map(a=>a.join('')),['vxw','vxwy','vxwyz']);
assert.throws(()=>decode(5,243));assert.throws(()=>promote(5,[0,0,0,0,0]));
console.log(JSON.stringify({status:'PASS',states3D:27,states4D:81,states5D:243,totalChecks:checks}));
