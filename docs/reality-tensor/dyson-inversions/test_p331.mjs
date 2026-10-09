import assert from 'node:assert/strict';
import {sync,unwind,boundary,angleDegrees} from './p331_sync.mjs';
for(let i=0;i<1464;i++){
 const s=sync(i);assert.equal(unwind(s.year,s.daySlot),i);
 assert.equal(s.angleNumerator*61,(s.daySlot-1)*3660);
 assert.equal(s.orientation,s.halfSign*s.sheet);
 assert.ok(angleDegrees(i)>=0&&angleDegrees(i)<360);
}
assert.equal(sync(182).angleNumerator,10920);
assert.equal(sync(183).angleNumerator,10980);
assert.equal(sync(182).orientation,-1);assert.equal(sync(183).orientation,1);
assert.equal(sync(365).orientation,1);assert.equal(sync(366).orientation,1);
assert.equal(sync(0).sheet,1);assert.equal(sync(366).sheet,-1);assert.equal(sync(732).sheet,1);
assert.equal(boundary().calendar2024.totalDays,1461);
assert.equal(boundary().calendar2097.totalDays,1460);
console.log(JSON.stringify({status:'PASS',roundTrips:1464,halfBoundaryDegrees:[angleDegrees(182),angleDegrees(183)],degreesPerSlot:60/61,turns:4,calendar2024:1461,calendar2097:1460}));
