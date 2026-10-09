import assert from 'node:assert/strict';
import {spawn} from 'node:child_process';
import {mkdtemp,writeFile,rm,readdir} from 'node:fs/promises';
import {join} from 'node:path';
import {tmpdir} from 'node:os';
import {keypair} from './p359_witness.mjs';
import {CrashWitness} from './p361_crash.mjs';
const kp=keypair();let assertions=0;const check=x=>{assert.ok(x);assertions++};
const report=[];
async function launch(dir,keyPath,head,epoch=12,kill=false){return await new Promise(resolve=>{
 const p=spawn(process.execPath,[new URL('./p363_worker.mjs',import.meta.url).pathname,dir,keyPath,head,String(epoch)]);
 let out='',err='';p.stdout.on('data',v=>out+=v);p.stderr.on('data',v=>err+=v);
 if(kill)setTimeout(()=>{if(p.exitCode===null)p.kill('SIGKILL')},1);
 p.on('close',(code,signal)=>resolve({code,signal,out,err}));
 });}
for(const mode of ['concurrent','kill-race','restart']){
 const dir=await mkdtemp(join(tmpdir(),'root0-p363-'));
 try {
 const keyPath=join(dir,'witness.pem');await writeFile(keyPath,kp.privateKey.export({format:'pem',type:'pkcs8'}),{mode:0o600});
 if(mode==='restart'){
 const w=new CrashWitness(dir,new Map([['w0',kp.publicKey]]));
 await assert.rejects(w.vote('w0',{context:'oasis/main',epoch:12,length:1440,head:'a'.repeat(64)},kp.privateKey,{crashAt:'reserved'}));assertions++;
 }
 const runs=await Promise.all(Array.from({length:24},(_,i)=>launch(dir,keyPath,i%2?'b':'a',12,mode==='kill-race'&&i%3===0)));
 const success=runs.filter(r=>r.code===0&&r.out.includes('"ok":true'));
 check(success.length<=24);
 const w=new CrashWitness(dir,new Map([['w0',kp.publicKey]]));
 const a=await w.inspect('w0',{context:'oasis/main',epoch:12,length:1440,head:'a'.repeat(64)});
 const b=await w.inspect('w0',{context:'oasis/main',epoch:12,length:1440,head:'b'.repeat(64)});
 check(!(a.status==='committed'&&b.status==='committed'));
 const ra=await w.vote('w0',{context:'oasis/main',epoch:12,length:1440,head:'a'.repeat(64)},kp.privateKey);
 const rb=await w.vote('w0',{context:'oasis/main',epoch:12,length:1440,head:'b'.repeat(64)},kp.privateKey);
 check(!(ra.ok&&rb.ok));
 const files=await readdir(dir);check(files.length>=2);
 report.push({mode,attempts:24,terminated:runs.filter(r=>r.signal==='SIGKILL').length,successfulReplies:success.length,inspectionA:a.status,inspectionB:b.status,noDoubleVote:true});
 }finally{await rm(dir,{recursive:true,force:true});}
}
console.log(JSON.stringify({status:'PASS',assertions,report},null,2));
