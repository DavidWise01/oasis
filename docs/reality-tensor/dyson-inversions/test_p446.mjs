import assert from 'node:assert/strict';
import {mkdtemp,writeFile,rm} from 'node:fs/promises';
import {tmpdir} from 'node:os';import {join} from 'node:path';
import {createServer} from 'node:net';import {performance} from 'node:perf_hooks';
import {prepareSocket} from './p446_socket.mjs';
const t=performance.now();const d=await mkdtemp(join(tmpdir(),'root0-p446-'));let count=0;
function ok(v){assert.ok(v);count++}
const live=join(d,'live.sock'),stale=join(d,'stale.sock'),ordinary=join(d,'file.txt');
async function start(p){const s=createServer(x=>x.end());await new Promise(r=>s.listen(p,r));return s}
async function stop(s){await new Promise(r=>s.close(r))}
try{
 let r=await prepareSocket(join(d,'missing.sock'));ok(r.ok&&r.action==='absent');
 await writeFile(ordinary,'protected');r=await prepareSocket(ordinary);ok(!r.ok&&r.reason==='path-not-socket');
 const s=await start(live);r=await prepareSocket(live);ok(!r.ok&&r.reason==='active-listener');
 r=await prepareSocket(live,{expectedUid:process.getuid()+1});ok(!r.ok&&r.reason==='owner-mismatch');await stop(s);
 const {fork}=await import('node:child_process');
 const helper=join(d,'helper.cjs');
 await writeFile(helper,"const net=require('node:net');const s=net.createServer();s.listen(process.argv[2],()=>process.send({ready:true}));");
 const child=fork(helper,[stale],{stdio:['ignore','ignore','ignore','ipc']});
 const ready=await new Promise((resolve,reject)=>{child.once('message',resolve);child.once('error',reject)});ok(ready.ready);
 child.kill('SIGKILL');const exit=await new Promise(resolve=>child.once('exit',(code,signal)=>resolve(signal)));ok(exit==='SIGKILL');
 r=await prepareSocket(stale);ok(r.ok&&r.action==='reclaimed-refused-socket');
 r=await prepareSocket(stale);ok(r.ok&&r.action==='absent');
 console.log(JSON.stringify({status:'PASS',assertions:count,elapsedMs:Number((performance.now()-t).toFixed(3)),activeListenerDenied:true,staleReclaimed:true,sameHost:true}));
}finally{await rm(d,{recursive:true,force:true})}