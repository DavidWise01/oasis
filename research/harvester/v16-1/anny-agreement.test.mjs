import test from 'node:test';import assert from 'node:assert/strict';
import {observeAnny} from './anny-observer.mjs';
const digest='a'.repeat(64),transferId='proof-1',deliveryKey=transferId+':'+digest;
const receipt={accepted:true,transferId,deliveryKey,digest};
const row={transferId,epoch:1,state:'CONFIRMED',sourceHex:'0102030405',digest,deliveryKey,acks:[],receipt};
test('violet verified only for independent complete agreement',()=>{
 const s=observeAnny(row,receipt);assert.equal(s.slots[17].value,'VERIFIED');assert.equal(s.slots[17].status,'observed');
});
for(const [label,transfer,r] of [
 ['missing receiver receipt',row,null],
 ['receiver mismatch',row,{...receipt,digest:'b'.repeat(64)}],
 ['journal receipt missing',{...row,receipt:undefined},receipt],
 ['journal receipt mismatched',{...row,receipt:{...receipt,transferId:'other'}},receipt],
 ['wrong receiver identity',row,{...receipt,transferId:'other'}],
 ['pending state',{...row,state:'RELEASE_PENDING'},receipt]
]){
 test('violet fail-closed: '+label,()=>{
  const s=observeAnny(transfer,r);assert.notEqual(s.slots[17].status,'observed');
  assert.notEqual(s.slots[17].value,'VERIFIED');
 });
}
