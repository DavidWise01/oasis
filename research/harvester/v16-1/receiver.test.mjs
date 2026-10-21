import test from 'node:test';
import assert from 'node:assert/strict';
import {ReceiverLedger} from './receiver.mjs';
import {MemoryJournalStore} from './journal.mjs';
const bytes=[1,2,3,4,5];
const sourceHex='0102030405';
const digest=Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',new Uint8Array(bytes))), b=>b.toString(16).padStart(2,'0')).join('');
const packet={transferId:'transfer-01',digest,sourceHex,deliveryKey:`transfer-01:${digest}`};
test('1: duplicate delivery produces one consumer ledger effect',async()=>{
  const r=new ReceiverLedger(new MemoryJournalStore());
  const [a,b]=await Promise.all([r.deliver(packet),r.deliver(packet)]);
  assert.deepEqual(a,b);assert.equal(await r.effectCount(packet.deliveryKey),1);
});
test('2: lost confirmation returns the original persisted receipt',async()=>{
  const r=new ReceiverLedger(new MemoryJournalStore());
  const first=await r.deliver(packet);
  assert.deepEqual(await r.deliver(packet),first);
  assert.deepEqual(await r.reconcile(packet.deliveryKey),first);
  assert.equal(await r.effectCount(packet.deliveryKey),1);
});
test('3: sender restart reuses delivery identity and does not reapply effect',async()=>{
  const store=new MemoryJournalStore();const receiver=new ReceiverLedger(store);
  const receipt=await receiver.deliver(packet);
  const afterRestart=new ReceiverLedger(store);
  assert.deepEqual(await afterRestart.deliver({...packet}),receipt);
  assert.equal(await afterRestart.effectCount(packet.deliveryKey),1);
});
test('4: conflicting payload, digest mismatch and key mismatch are rejected',async()=>{
  const r=new ReceiverLedger(new MemoryJournalStore());await r.deliver(packet);
  await assert.rejects(r.deliver({...packet,sourceHex:'0102030406'}),/DIGEST_MISMATCH/);
  await assert.rejects(r.deliver({...packet,deliveryKey:'different-key'}),/KEY_MISMATCH/);
  await assert.rejects(r.deliver({...packet,digest:'0'.repeat(64)}),/DIGEST_MISMATCH/);
  assert.equal(await r.effectCount(packet.deliveryKey),1);
});
test('5: receiver restart preserves committed result in retained backing store',async()=>{
  const store=new MemoryJournalStore(); const before=new ReceiverLedger(store);
  const first=await before.deliver(packet);
  const after=new ReceiverLedger(store);
  assert.deepEqual(await after.reconcile(packet.deliveryKey),first);
  assert.equal(await after.effectCount(packet.deliveryKey),1);
});