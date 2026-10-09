import assert from 'node:assert/strict';
import {mkdtemp,rm} from 'node:fs/promises';
import {tmpdir} from 'node:os';import {join} from 'node:path';
import {TransactionalAnchor,GENESIS} from './p370_transactional.mjs';
let n=0;const ok=b=>{assert.ok(b);n++};const dir=await mkdtemp(join(tmpdir(),'p370-'));const path=join(dir,'anchor.db');
try{
 let trusted={count:0,head:GENESIS};const a=new TransactionalAnchor(path,trusted);
 const first=a.reserve('w0',1,'a'.repeat(64));ok(first.ok);trusted=first.checkpoint;
 ok(!a.reserve('w0',1,'b'.repeat(64)).ok);ok(a.reserve('w0',1,'a'.repeat(64)).previous);
 a.close();const restart=new TransactionalAnchor(path,trusted);ok(restart.validate());
 ok(!restart.reserve('w0',0,'c'.repeat(64)).ok);
 const stale=new TransactionalAnchor(path,{count:0,head:GENESIS});ok(!stale.reserve('w0',2,'a'.repeat(64)).ok);stale.close();
 const requests=Array.from({length:100},(_,i)=>({id:'w'+(i%5),epoch:2+Math.floor(i/5),head:(i%2?'b':'a').repeat(64)}));
 for(const q of requests){const r=restart.reserve(q.id,q.epoch,q.head);ok(r.ok);trusted=r.checkpoint;}
 ok(restart.validate());restart.close();
 const persisted=new TransactionalAnchor(path,trusted);ok(persisted.validate());ok(!persisted.reserve('w0',1,'f'.repeat(64)).ok);persisted.close();
 const rollback=new TransactionalAnchor(join(dir,'empty.db'),trusted);ok(!rollback.validate());ok(!rollback.reserve('w0',100,'f'.repeat(64)).ok);rollback.close();
 console.log(JSON.stringify({status:'PASS_CONDITIONAL_EXTERNAL_CHECKPOINT',assertions:n,transactionalWrites:101,rollbackDetected:true}));
}finally{await rm(dir,{recursive:true,force:true});}