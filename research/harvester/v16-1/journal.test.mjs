import {test} from 'node:test';
import assert from 'node:assert/strict';
import {CommitJournal,MemoryJournalStore} from './journal.mjs';
const make=(epoch=1,bytes=[1,2,3,4,5])=>({transferId:'sample',epoch,bytes,acks:['A','B'].flatMap(path=>bytes.map((byte,position)=>({transferId:'sample',epoch,path,position,byte})))});
const fresh=()=>new CommitJournal(new MemoryJournalStore());
test('prepare, commit, release pending, confirm; retain across rehydration',async()=>{
 const s=new MemoryJournalStore(),a=new CommitJournal(s); const p=make();
 await a.prepare(p); await a.commit('sample',1); await a.pending('sample',1);
 const b=new CommitJournal(s); const row=await b.read('sample');
 assert.equal(row.state,'RELEASE_PENDING');
 await b.confirm('sample',1,{deliveryKey:row.deliveryKey,digest:row.digest});
 assert.equal((await a.read('sample')).state,'CONFIRMED');
 await assert.rejects(a.confirm('sample',1,{deliveryKey:row.deliveryKey,digest:row.digest}),/INVALID_CONFIRM/);
});
test('missing, duplicate, stale, and corrupted ACKs fail closed',async()=>{
 for(const mut of [p=>p.acks.pop(),p=>p.acks[9]=p.acks[0],p=>p.acks[0].epoch=0,p=>p.acks[0].byte=99]) {
  const p=make();mut(p);await assert.rejects(fresh().prepare(p));
 }
});
test('conflicting source and old epochs rejected; new epoch may supersede prepare',async()=>{
 const j=fresh();await j.prepare(make());
 await assert.rejects(j.prepare(make(1,[1,2,3,4,6])),/CONFLICTING_SOURCE/);
 await assert.rejects(j.prepare(make(0)),/STALE_ATTEMPT/);
 await j.prepare(make(2));await j.commit('sample',2);
 await assert.rejects(j.prepare(make(3)),/COMMITTED_TRANSFER_IMMUTABLE/);
});
test('no release path before durable commit and no invented bytes',async()=>{
 const j=fresh();await assert.rejects(j.pending('sample',1));
 await j.prepare(make());await assert.rejects(j.pending('sample',1),/INVALID_TRANSITION/);
 await assert.rejects(j.prepare({...make(),bytes:[1,2,3,4]}),/SOURCE_NOT_40_BITS/);
});
test('failed persistence cannot establish commit',async()=>{
 const store=new MemoryJournalStore(),j=new CommitJournal(store);await j.prepare(make());
 const bad=new CommitJournal({transact:async()=>{throw new Error('disk failure')}});
 await assert.rejects(bad.commit('sample',1),/disk failure/);
 assert.equal((await j.read('sample')).state,'PREPARED');
});