import test from 'node:test';
import assert from 'node:assert/strict';
import {CommitJournal,MemoryJournalStore} from './journal.mjs';
const bytes=[1,2,3,4,5];
function packet(id,epoch=1){return {transferId:id,epoch,bytes,acks:['A','B'].flatMap(path=>bytes.map((byte,position)=>({transferId:id,epoch,path,position,byte})))}}
async function setup(id){const store=new MemoryJournalStore();const j=new CommitJournal(store);await j.prepare(packet(id));return {j,store};}
for(const boundary of ['PREPARED','COMMITTED','RELEASE_PENDING','CONFIRMED']){
 test(`crash checkpoint at ${boundary}: deterministic recovery`,async()=>{
  const {j,store}=await setup(`crash-${boundary}`);const id=`crash-${boundary}`;
  if(boundary!=='PREPARED')await j.commit(id,1);
  if(['RELEASE_PENDING','CONFIRMED'].includes(boundary))await j.pending(id,1);
  let r=await j.read(id);
  if(boundary==='CONFIRMED')await j.confirm(id,1,{deliveryKey:r.deliveryKey,digest:r.digest});
  const recovered=new CommitJournal(store);r=await recovered.read(id);
  assert.equal(r.state,boundary);
  if(boundary==='PREPARED') {await assert.rejects(recovered.pending(id,1),/INVALID_TRANSITION/);await recovered.commit(id,1);}
  if((await recovered.read(id)).state==='COMMITTED')await recovered.pending(id,1);
  const p=await recovered.read(id);
  if(p.state==='RELEASE_PENDING')await recovered.confirm(id,1,{deliveryKey:p.deliveryKey,digest:p.digest});
  assert.equal((await recovered.read(id)).state,'CONFIRMED');
 });
}
test('ambiguous commit (durable write then lost response) is idempotently recoverable',async()=>{
 const {j,store}=await setup('ambiguous'); const r=await j.commit('ambiguous',1);
 assert.equal(r.state,'COMMITTED');
 const reboot=new CommitJournal(store);const again=await reboot.commit('ambiguous',1);
 assert.equal(again.deliveryKey,r.deliveryKey);assert.equal(again.state,'COMMITTED');
});
test('wrong receipt fails; pending retry uses stable identity',async()=>{
 const {j,store}=await setup('receipt');await j.commit('receipt',1);await j.pending('receipt',1);
 const p=await j.read('receipt');await assert.rejects(j.confirm('receipt',1,{deliveryKey:'wrong',digest:p.digest}),/BAD_RECEIPT/);
 const reboot=new CommitJournal(store);const again=await reboot.pending('receipt',1);
 assert.equal(again.deliveryKey,p.deliveryKey);assert.equal(again.state,'RELEASE_PENDING');
});