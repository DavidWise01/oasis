// Harvester v16.1: transport-independent, fail-closed journal.
// An adapter must atomically implement transact(id, update(current)).
const same = (a,b) => a === b;
const validId = s => typeof s === 'string' && s.length > 0 && s.length <= 256;
const hex = b => Array.from(b, x=>x.toString(16).padStart(2,'0')).join('');
const hash = async bytes => hex(new Uint8Array(await crypto.subtle.digest('SHA-256', bytes)));
function requireThat(ok, why) { if (!ok) throw new Error(why); }
function legalAcks(acks, transferId, epoch, bytes) {
  requireThat(Array.isArray(acks) && acks.length === 10, 'ACK_COUNT');
  const seen=new Set();
  for (const a of acks) {
    requireThat(a && a.transferId===transferId && a.epoch===epoch, 'STALE_ACK');
    requireThat((a.path==='A'||a.path==='B') && Number.isInteger(a.position) && a.position>=0 && a.position<5, 'ACK_ADDRESS');
    requireThat(a.byte===bytes[a.position], 'ACK_BYTE_MISMATCH');
    const k=`${a.path}:${a.position}`;
    requireThat(!seen.has(k), 'DUPLICATE_ACK'); seen.add(k);
  }
}
export class MemoryJournalStore {
  #items=new Map(); #locked=false;
  async transact(id, f) {
    requireThat(!this.#locked,'CONCURRENT_TRANSACTION');
    this.#locked=true;
    try {
      const old=this.#items.get(id);
      const next=f(old && structuredClone(old));
      if (next !== undefined) this.#items.set(id,structuredClone(next));
      return structuredClone(next===undefined?old:next);
    } finally {this.#locked=false;}
  }
  async read(id) {const x=this.#items.get(id); return x && structuredClone(x);}
}
export class IndexedDBJournalStore {
  constructor(name='harvester-journal-v16-1') {this.name=name; this.dbPromise=null;}
  async db() {
    if (!this.dbPromise) this.dbPromise=new Promise((resolve,reject)=>{
      const req=indexedDB.open(this.name,1);
      req.onupgradeneeded=()=>req.result.createObjectStore('transfers');
      req.onerror=()=>reject(req.error);
      req.onsuccess=()=>resolve(req.result);
    });
    return this.dbPromise;
  }
  async transact(id, f) {
    const db=await this.db();
    return new Promise((resolve,reject)=>{
      const tx=db.transaction('transfers','readwrite',{durability:'strict'});
      const store=tx.objectStore('transfers');
      let result;
      const get=store.get(id);
      get.onerror=()=>{ try { tx.abort(); } catch {} };
      get.onsuccess=()=>{
        try {const next=f(get.result); result=next===undefined?get.result:next; if(next!==undefined) store.put(next,id);}
        catch(e){reject(e); tx.abort();}
      };
      tx.oncomplete=()=>resolve(result);
      tx.onabort=()=>reject(tx.error||new Error('TRANSACTION_ABORTED'));
      tx.onerror=()=>reject(tx.error||new Error('TRANSACTION_FAILED'));
    });
  }
  async read(id) {return (await this.transact(id,()=>undefined));}
}
export class CommitJournal {
  constructor(store) {this.store=store;}
  async prepare({transferId,epoch,bytes,acks}) {
    requireThat(validId(transferId) && Number.isSafeInteger(epoch) && epoch>=0,'BAD_ID');
    requireThat(Array.isArray(bytes) && bytes.length===5 && bytes.every(n=>Number.isInteger(n)&&n>=0&&n<=255),'SOURCE_NOT_40_BITS');
    legalAcks(acks,transferId,epoch,bytes);
    const digest=await hash(new Uint8Array(bytes));
    const row={transferId,epoch,sourceHex:hex(bytes),digest,acks:structuredClone(acks),state:'PREPARED',deliveryKey:`${transferId}:${digest}`};
    return this.store.transact(transferId,old=>{
      if(old) {
        requireThat(old.digest===digest && old.sourceHex===row.sourceHex,'CONFLICTING_SOURCE');
        requireThat(old.epoch<=epoch,'STALE_ATTEMPT');
        if(old.epoch===epoch) {requireThat(old.state==='PREPARED','ALREADY_COMMITTED');return undefined;}
        requireThat(old.state==='PREPARED','COMMITTED_TRANSFER_IMMUTABLE');
      }
      return row;
    });
  }
  async commit(id,epoch) {return this.#advance(id,epoch,'PREPARED','COMMITTED');}
  async pending(id,epoch) {return this.#advance(id,epoch,'COMMITTED','RELEASE_PENDING');}
  async confirm(id,epoch,receipt) {
    requireThat(receipt && typeof receipt==='object','RECEIPT_REQUIRED');
    return this.store.transact(id,old=>{
      requireThat(old && old.epoch===epoch,'UNKNOWN_ATTEMPT');
      requireThat(old.state==='RELEASE_PENDING','INVALID_CONFIRM_TRANSITION');
      requireThat(same(receipt.deliveryKey,old.deliveryKey) && same(receipt.digest,old.digest),'BAD_RECEIPT');
      return {...old,state:'CONFIRMED',receipt:structuredClone(receipt)};
    });
  }
  async #advance(id,epoch,from,to) {return this.store.transact(id,old=>{
    requireThat(old && old.epoch===epoch,'UNKNOWN_ATTEMPT');
    requireThat(old.state===from || old.state===to,'INVALID_TRANSITION');
    return old.state===to?undefined:{...old,state:to};
  });}
  async read(id) {return this.store.read(id);}
}