// Node reference adapter: atomic receiver-ledger transactions; not a browser adapter.
import {mkdir,readFile,open,rename,rm} from 'node:fs/promises';
import {dirname} from 'node:path';import {randomUUID} from 'node:crypto';
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
export class FileJournalStore {
 constructor(path,{timeoutMs=4000}={}){this.path=path;this.lock=path+'.lock';this.timeoutMs=timeoutMs}
 async transact(key,update){
  await mkdir(dirname(this.path),{recursive:true});const deadline=Date.now()+this.timeoutMs;
  for(;;){try{await mkdir(this.lock);break}catch(e){if(e.code!=='EEXIST')throw e;if(Date.now()>deadline)throw Error('STORE_LOCK_TIMEOUT');await sleep(10)}}
  try{
   let rows={};try{rows=JSON.parse(await readFile(this.path,'utf8'))}catch(e){if(e.code!=='ENOENT')throw e}
   const old=rows[key]===undefined?undefined:structuredClone(rows[key]);const next=update(old);
   if(next!==undefined){
    rows[key]=structuredClone(next);const temp=this.path+'.'+randomUUID()+'.tmp';
    const f=await open(temp,'wx');try{await f.writeFile(JSON.stringify(rows));await f.sync()}finally{await f.close()}
    await rename(temp,this.path);const dir=await open(dirname(this.path),'r');try{await dir.sync()}finally{await dir.close()}
   }
   return structuredClone(next===undefined?old:next);
  }finally{await rm(this.lock,{recursive:true,force:true})}
 }
 async read(key){return this.transact(key,()=>undefined)}
}
