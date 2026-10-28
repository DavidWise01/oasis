import test from 'node:test';import assert from 'node:assert/strict';
import {ANNY_GLYPH,ANNY_BANDS,observeAnny,readAnny} from './anny-observer.mjs';
const bytes=[1,2,3,4,5];
const record={transferId:'t-01',epoch:3,sourceHex:'0102030405',digest:'a'.repeat(64),deliveryKey:'t-01:'+('a'.repeat(64)),state:'CONFIRMED',acks:['A','B'].flatMap(path=>bytes.map((byte,position)=>({transferId:'t-01',epoch:3,path,position,byte})))};
const receipt={accepted:true,transferId:record.transferId,deliveryKey:record.deliveryKey,digest:record.digest};
record.receipt=structuredClone(receipt);
test('exact cubit 7 braces and 18 positions with double closure',()=>{
 assert.equal(ANNY_GLYPH,'{|12|}{|3456|}{|78|}{|910|}{|1112131415||}{|1617|}{|18|}');
 assert.deepEqual(ANNY_BANDS.flatMap(x=>x.slots),Array.from({length:18},(_,i)=>i+1));
 assert.equal(ANNY_BANDS[4].doubleClosure,true);
});
test('journal and receiver evidence populate 18 read-only slots',()=>{
 const s=observeAnny(record,receipt);assert.equal(s.slots.length,18);
 assert.equal(s.slots[2].value,'01');assert.equal(s.slots[6].value,'05');
 assert.equal(s.slots[10].value,'A/B');assert.equal(s.slots[14].value,'A/B');
 assert.equal(s.slots[16].status,'observed');assert.equal(s.slots[17].value,'VERIFIED');
 assert.equal(record.state,'CONFIRMED');
});
test('missing and stale witnesses cannot appear complete',()=>{
 const s=observeAnny({...record,acks:[...record.acks.slice(0,8),{...record.acks[8],epoch:2}]},null);
 assert.equal(s.slots[8].status,'observed');assert.equal(s.slots[9].status,'incomplete');
 assert.equal(s.slots[16].status,'pending');
});
test('readAnny uses only read and reconcile; never mutations',async()=>{
 const calls=[];
 const journal={read:async id=>{calls.push('read:'+id);return structuredClone(record)}};
 const receiver={reconcile:async key=>{calls.push('reconcile:'+key);return structuredClone(receipt)}};
 const s=await readAnny(journal,receiver,'t-01');
 assert.equal(s.phase,'CONFIRMED');
 assert.deepEqual(calls,['read:t-01','reconcile:'+record.deliveryKey]);
 await assert.rejects(readAnny(journal,receiver,''),/TRANSFER_ID_REQUIRED/);
});
