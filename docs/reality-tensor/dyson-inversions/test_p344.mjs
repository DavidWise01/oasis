import assert from 'node:assert/strict';
import {FRAMES,COMPASS_PAIRS,encode,decode,invert,embed3to4} from './p344_signed_geometry.mjs';
let checks=0;
for(const [frame,expected] of [['3d',27],['4d',81]]){
 const dims=FRAMES[frame].axes.length;
 for(let i=0;i<expected;i++){
  const s=decode(frame,i);
  assert.equal(s.root,0);
  assert.equal(encode(frame,s.signs),i);
  assert.deepEqual(invert(invert(s.signs)),s.signs);
  if(frame==='3d')assert.deepEqual(decode('4d',encode('4d',embed3to4(s.signs))).signs,[...s.signs,0]);
  checks++;
 }
 assert.equal(expected,3**dims);
}
assert.equal(COMPASS_PAIRS.length,6);
assert.throws(()=>encode('3d',[1,1]));assert.throws(()=>decode('4d',81));
console.log(JSON.stringify({status:'PASS',checks,states3d:27,states4d:81,compassPairs:6}));
