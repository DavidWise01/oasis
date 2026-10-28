// Harvester v16.1 Task 3 — receiver reconciliation.
// The consumer's ledger mutation and resulting receipt occur in ONE store transaction.
// This guarantees at-most-once *ledger-managed* effects, not arbitrary external I/O.
const fail = (condition, code) => { if (!condition) throw new Error(code); };
const eq = (a,b) => a === b;
const clone = x => structuredClone(x);
export class ReceiverLedger {
  constructor(transactionStore) { this.store = transactionStore; }
  async deliver({deliveryKey, transferId, digest, sourceHex}) {
    fail(typeof deliveryKey === 'string' && deliveryKey.length > 0 && deliveryKey.length <= 768, 'INVALID_DELIVERY_KEY');
    fail(typeof transferId === 'string' && transferId.length > 0, 'INVALID_TRANSFER_ID');
    fail(typeof digest === 'string' && /^[0-9a-f]{64}$/.test(digest), 'INVALID_DIGEST');
    fail(typeof sourceHex === 'string' && /^[0-9a-f]{10}$/.test(sourceHex), 'INVALID_SOURCE');
    const bytes=Uint8Array.from(sourceHex.match(/../g),h=>parseInt(h,16));
    const calculated=Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',bytes)),b=>b.toString(16).padStart(2,'0')).join('');
    fail(calculated===digest,'DIGEST_MISMATCH');
    fail(deliveryKey===`${transferId}:${digest}`,'KEY_MISMATCH');
    return this.store.transact(`receiver:${deliveryKey}`, old => {
      if (old) {
        fail(eq(old.digest,digest) && eq(old.sourceHex,sourceHex) && eq(old.transferId,transferId),'CONFLICTING_PAYLOAD');
        return undefined;
      }
      const receipt={deliveryKey,digest,transferId,accepted:true};
      return {transferId,digest,sourceHex,deliveryKey,effectCount:1,receipt};
    }).then(record=>clone(record.receipt));
  }
  async reconcile(deliveryKey) {
    const record=await this.store.read(`receiver:${deliveryKey}`);
    return record ? clone(record.receipt) : null;
  }
  async effectCount(deliveryKey) {
    const record=await this.store.read(`receiver:${deliveryKey}`);
    return record?.effectCount ?? 0;
  }
}
