import {spawn} from 'node:child_process';
import {mkdtemp,rm} from 'node:fs/promises';import {join} from 'node:path';import {tmpdir} from 'node:os';
import {SerializedAuthority} from './p372_authority.mjs';
function child(file,id,epoch,hex){return new Promise(resolve=>{const p=spawn(process.execPath,[new URL('./worker.mjs',import.meta.url).pathname,file,id,String(epoch),hex]);let out='';p.stdout.on('data',x=>out+=x);p.on('close',(code,signal)=>{let result;try{result=JSON.parse(out.trim());}catch{result={ok:false,error:'missing output',code,signal}}resolve(result)});});}
const root=await mkdtemp(join(tmpdir(),'p372-'));const reports=[];
try{
 for(const processes of [8,32,64]){
  const file=join(root,`db${processes}.sqlite`);const init=new SerializedAuthority(file);init.close();
  const start=process.hrtime.bigint();const tasks=Array.from({length:processes},(_,i)=>child(file,'w'+i,1,(i%16).toString(16)));
  const results=await Promise.all(tasks);const ms=Number(process.hrtime.bigint()-start)/1e6;
  const db=new SerializedAuthority(file);const status=db.status();db.close();
  reports.push({scenario:'distinct-witnesses',processes,accepted:results.filter(x=>x.ok&&!x.duplicate).length,errors:results.filter(x=>!x.ok).map(x=>x.error??x.reason),elapsedMs:ms,throughputPerSec:processes/(ms/1000),checkpointCount:status.count,integrity:status.integrity,latencyMs:{min:Math.min(...results.map(x=>x.latencyMs??Infinity)),max:Math.max(...results.map(x=>x.latencyMs??0))}});
 }
 const file=join(root,'conflict.sqlite');const init=new SerializedAuthority(file);init.close();const results=await Promise.all(Array.from({length:64},(_,i)=>child(file,'same',5,i%2?'a':'b')));const db=new SerializedAuthority(file);const status=db.status();db.close();reports.push({scenario:'same-witness-conflict',processes:64,firstAcceptances:results.filter(x=>x.ok&&!x.duplicate).length,duplicateAccepted:results.filter(x=>x.ok&&x.duplicate).length,conflictsRejected:results.filter(x=>x.reason==='conflict').length,errors:results.filter(x=>x.error).map(x=>x.error),checkpointCount:status.count,integrity:status.integrity});
 console.log(JSON.stringify({reports},null,2));
}finally{await rm(root,{recursive:true,force:true});}