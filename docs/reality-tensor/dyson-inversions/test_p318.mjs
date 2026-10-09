import assert from 'node:assert/strict';
import {encode,decode,inverse,specimen,DIMENSIONS,QUADS,LEVELS} from './p318_hierarchy.mjs';
const seen=new Set();
for(let seed=0;seed<1_000_000;seed++){
 const d=seed%3,q=seed%4,coords=[BigInt(seed-500000),BigInt(seed)*-2n,BigInt(seed)%7n];
 const s=encode(seed,d,q,coords),o=decode(s);
 assert.equal(o.seed,seed);assert.equal(o.dimension,d);assert.equal(o.quad,q);assert.deepEqual(o.coords,coords);assert.equal(inverse(s),s);
 if(seen.has(s))throw Error('collision');seen.add(s);
}
for(const s of ['abc','00.11.22.33.42.24.33.22.11.00/000000|-1+|Aa|00|0|0',specimen(0).replace('|0','|-0')])assert.throws(()=>decode(s));
assert.deepEqual(DIMENSIONS,['-1+','-2+','-3+']);assert.deepEqual(QUADS,['Aa','Bb','Cc','Dd']);assert.deepEqual(LEVELS,['vogel','voxel','vector']);
console.log(JSON.stringify({pass:true,cases:seen.size,collisions:0,levels:LEVELS,example:specimen(999999)}));
