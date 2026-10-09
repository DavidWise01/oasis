import assert from 'node:assert/strict';
import {SPEC} from './p316_seeded_cross.mjs';
import {route,unroute,paths,bucket,RADIX_CAPACITY,WIDTH,STARGATE,PREFIX} from './p317_route.mjs';
assert.equal(RADIX_CAPACITY,1771561);assert.equal(WIDTH,6);assert.equal(STARGATE.join(' '),'00 11 22 33 42 24 33 22 11 00');
const seen=new Set(),buckets=new Uint32Array(4096);let max=0;
for(let seed=0;seed<SPEC.seedCount;seed++){
 const r=route(seed);assert.equal(unroute(r),seed);assert.equal(r.startsWith(PREFIX+'/'),true);
 if(seen.has(r))throw Error('full address collision at '+seed);seen.add(r);buckets[bucket(seed)]++;
 if(seed%100000===0){const x=paths(seed);assert.deepEqual(x.closure,[0,0]);assert.deepEqual(x.left.map((v,i)=>v+x.right[i]),[0,0]);}
}
for(const s of ['',PREFIX+'/ZZZZZZ',PREFIX+'/00000a',PREFIX+'/0000000','BAD/000001'])assert.throws(()=>unroute(s));
for(const x of [-1,1000000,1.2])assert.throws(()=>route(x));
max=Math.max(...buckets);const occupied=buckets.filter(n=>n>0).length;
console.log(JSON.stringify({status:'PASS',seeds:seen.size,fullRouteCollisions:SPEC.seedCount-seen.size,radixCapacity:RADIX_CAPACITY,unusedCodes:RADIX_CAPACITY-SPEC.seedCount,bucketCount:occupied,moduloBucketCollisions:SPEC.seedCount-occupied,maxBucketSize:max,lastRoute:route(999999),apex:SPEC.apex},null,2));
