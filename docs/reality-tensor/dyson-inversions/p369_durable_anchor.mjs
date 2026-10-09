import {mkdir,open,readFile,readdir} from 'node:fs/promises';
import {join} from 'node:path';
import {createHash} from 'node:crypto';
const digest=x=>createHash('sha256').update(x).digest('hex');
const key=(id,epoch)=>Buffer.from(id+'|'+epoch).toString('hex')+'.json';
export const TOPOLOGY='-+5 + 1';
export class DurableAnchor {
 constructor(directory, trustedCheckpoint){if(!trustedCheckpoint||!Number.isInteger(trustedCheckpoint.count)||typeof trustedCheckpoint.head!=='string')throw Error('external trusted checkpoint required');this.dir=directory;this.trusted=trustedCheckpoint;}
 static async provision(directory){await mkdir(directory,{recursive:true});return new DurableAnchor(directory,{count:0,head:digest('ROOT0:P369:GENESIS')});}
 async records(){const files=(await readdir(this.dir)).filter(n=>n.endsWith('.json')).sort();const entries=[];for(const file of files){const x=JSON.parse(await readFile(join(this.dir,file),'utf8'));if(file!==key(x.id,x.epoch)||!(/^[a-f0-9]{64}$/.test(x.head)))throw Error('corrupt-record');entries.push(x);}return entries;}
 async checkpoint(){const items=await this.records();let head=digest('ROOT0:P369:GENESIS');for(const x of items)head=digest(head+'|'+JSON.stringify(x));return {count:items.length,head};}
 async validate(){try{const c=await this.checkpoint();if(c.count!==this.trusted.count||c.head!==this.trusted.head)return {ok:false,reason:'rollback-or-altered-history'};return {ok:true,checkpoint:c};}catch{return {ok:false,reason:'unavailable-or-corrupt'};}}
 async reserve(id,epoch,head){const v=await this.validate();if(!v.ok)return v;if(typeof id!=='string'||!id||!Number.isSafeInteger(epoch)||epoch<0||!(/^[a-f0-9]{64}$/.test(head)))throw new RangeError('reservation');
  const p=join(this.dir,key(id,epoch));const entries=await this.records();const old=entries.find(x=>x.id===id&&x.epoch===epoch);if(old)return old.head===head?{ok:true,previous:true,checkpoint:this.trusted}:{ok:false,reason:'double-vote'};
  if(entries.some(x=>x.id===id&&x.epoch>epoch))return {ok:false,reason:'epoch-rollback'};
  let h;try{h=await open(p,'wx',0o600);await h.writeFile(JSON.stringify({id,epoch,head}));await h.sync();}catch(e){return {ok:false,reason:e.code==='EEXIST'?'concurrent-reservation':'write-error'};}finally{await h?.close();}
  try{const d=await open(this.dir,'r');try{await d.sync();}finally{await d.close();}}catch{return {ok:false,reason:'directory-sync-failed'};}
  const cp=await this.checkpoint();this.trusted=cp;return {ok:true,previous:false,checkpoint:cp};
 }
}