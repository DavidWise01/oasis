import assert from 'node:assert/strict';
import {mkdtemp,rm,unlink,writeFile,readdir} from 'node:fs/promises';import {join} from 'node:path';import {tmpdir} from 'node:os';
import {DurableAnchor,TOPOLOGY} from './p369_durable_anchor.mjs';
let assertions=0;const check=v=>{assert.ok(v);assertions++};
const root=await mkdtemp(join(tmpdir(),'p369-'));try{
 const dir=join(root,'anchor');const a=await DurableAnchor.provision(dir);let checkpoint=(await a.checkpoint());
 check(TOPOLOGY==='-+5 + 1');check((await a.validate()).ok);
 let r=await a.reserve('w0',1,'a'.repeat(64));check(r.ok&&!r.previous);checkpoint=r.checkpoint;
 const b=new DurableAnchor(dir,checkpoint);check((await b.validate()).ok);check((await b.reserve('w0',1,'a'.repeat(64))).previous);check((await b.reserve('w0',1,'b'.repeat(64))).reason==='double-vote');
 r=await b.reserve('w0',2,'b'.repeat(64));check(r.ok);checkpoint=r.checkpoint;
 check((await new DurableAnchor(dir,checkpoint).validate()).ok);
 const names=await readdir(dir);await unlink(join(dir,names[0]));check((await new DurableAnchor(dir,checkpoint).validate()).reason==='rollback-or-altered-history');
 check(!(await new DurableAnchor(dir,checkpoint).reserve('w0',1,'c'.repeat(64))).ok);
 await writeFile(join(dir,names[0]),'corrupted');check((await new DurableAnchor(dir,checkpoint).validate()).reason==='unavailable-or-corrupt');
 const missing=new DurableAnchor(join(root,'missing'),checkpoint);check((await missing.validate()).ok===false);
 check((await missing.reserve('w0',3,'c'.repeat(64))).ok===false);
 console.log(JSON.stringify({status:'PASS_CONDITIONAL_EXTERNAL_CHECKPOINT',assertions,topology:TOPOLOGY}));
}finally{await rm(root,{recursive:true,force:true});}