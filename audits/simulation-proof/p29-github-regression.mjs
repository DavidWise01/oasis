import assert from 'node:assert/strict';
import * as T from './p29_tensor_kernel.mjs';

assert.equal(T.SILO_SIZE,10_000);
assert.equal(T.TENSOR_SIZE,100_000_000);
for(let id=0;id<10_000;id++)assert.equal(T.encode4(T.decode4(id)),id);
let squareChecks=0,ringChecks=0;
for(let axis=0;axis<4;axis++)for(let layer=0;layer<2;layer++){
  const seen=new Uint8Array(10000);
  for(let id=0;id<10000;id++){
    const to=T.outerSwap(id,axis,layer);
    assert.equal(T.outerSwap(to,axis,layer),id);
    seen[to]++;squareChecks++;
  }
  assert(seen.every(c=>c===1));
  assert.equal(T.outerSwap(0,axis,layer),0);
}
for(const spin of T.TERNARY){
  const seen=new Uint8Array(10000);
  for(let id=0;id<10000;id++){
    const to=T.innerRotate(id,spin);
    assert.equal(T.innerRotate(to,-spin),id);
    seen[to]++;ringChecks++;
  }
  assert(seen.every(c=>c===1));
}
assert.equal(squareChecks,80_000);assert.equal(ringChecks,30_000);
const action={axis:2,layer:1,spin:+1};
const square=Int16Array.from({length:10000},(_,i)=>T.outerSwap(i,action.axis,action.layer));
const circle=Int16Array.from({length:10000},(_,i)=>T.innerRotate(i,action.spin));
const inverse=Int16Array.from({length:10000},(_,i)=>T.innerRotate(i,-1));
let count=0,checksum=0;
for(let o=0;o<10000;o++)for(let i=0;i<10000;i++){
  const mapped=square[o]*10000+circle[i];
  const decoded=square[Math.floor(mapped/10000)]*10000+inverse[mapped%10000];
  if(decoded!==o*10000+i)throw new Error('Tensor collision');
  checksum+=mapped;count++;
}
assert.equal(count,100_000_000);
assert.equal(checksum,4_999_999_950_000_000);
const root=new T.TensorRuntime(T.ZERO);
for(let i=0;i<1000;i++){root.forward();assert(T.isZero(root.pair));}
for(let i=0;i<1000;i++)root.reverse();
assert.equal(root.eventCount,2000);
console.log(JSON.stringify({status:'PASS',full_tensor:count,checksum,outer:squareChecks,inner:ringChecks,zeroPinned:true,appendOnly:root.eventCount},null,2));
