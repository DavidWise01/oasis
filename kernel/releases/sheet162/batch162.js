'use strict';
// SHEET 162: segment-bounded durable batch update; no cross-segment transaction pretence.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const {Store,SIZE,SCHEMA}=require('./baseline161/baseline160/indexed160');
const P=require('./baseline161/baseline160/baseline159/baseline158/baseline157/baseline156/baseline155/baseline154/baseline153/baseline152/baseline151/baseline150/baseline149/baseline148/baseline147/baseline146/protocol146');
const M=require('./baseline161/baseline160/baseline159/baseline158/baseline157/baseline156/baseline155/baseline154/baseline153/baseline152/baseline151/merkle151');
const hex=x=>typeof x==='string'&&/^[a-f0-9]{64}$/.test(x),sha=b=>crypto.createHash('sha256').update(b).digest('hex');
const segmentPath=(dir,i)=>path.join(dir,'segments',`segment-${String(i).padStart(7,'0')}.json`);
function write(file,obj){fs.mkdirSync(path.dirname(file),{recursive:true});const temp=file+'.tmp.'+process.pid+'.'+crypto.randomBytes(5).toString('hex');let fd;try{fd=fs.openSync(temp,'wx',0o600);fs.writeFileSync(fd,typeof obj==='string'?obj:JSON.stringify(obj)+'\n');fs.fsyncSync(fd);fs.closeSync(fd);fd=null;fs.renameSync(temp,file);const d=fs.openSync(path.dirname(file),'r');try{fs.fsyncSync(d);}finally{fs.closeSync(d);}}finally{if(fd!==null&&fd!==undefined)fs.closeSync(fd);if(fs.existsSync(temp))fs.unlinkSync(temp);}}
function nodes(records){const n={};let prev=records.map((r,i)=>{const h=M.leaf(r.sequence-1,r.hash);n[`${i}:1`]=h;return h;});let size=1;while(prev.length>1){const next=[];for(let i=0;i+1<prev.length;i+=2){const h=M.node(prev[i],prev[i+1]);n[`${i*size}:${size*2}`]=h;next.push(h);}prev=next;size*=2;}return n;}
function lock(file,fn){let fd;try{fd=fs.openSync(file,'wx',0o600);}catch(e){if(e.code==='EEXIST')throw Error('S162_LOCK_HELD');throw e;}try{return fn();}finally{fs.closeSync(fd);fs.unlinkSync(file);}}
const headDigest=h=>P.sha(h);
class BatchStore extends Store{
 constructor(dir,id){super(dir,id);this.batchMetrics={batches:0,records:0,segmentCommits:0,headCommits:0};}
 inspectOrphan(){if(!fs.existsSync(this.headPath))throw Error('S162_NO_HEAD');const h=JSON.parse(fs.readFileSync(this.headPath,'utf8'));const i=Math.floor(h.count/SIZE),off=h.count%SIZE,fp=segmentPath(this.dir,i);
  if(!fs.existsSync(fp))return null;const buf=fs.readFileSync(fp),seg=JSON.parse(buf);if(seg.schema!==SCHEMA||seg.id!==this.id||seg.index!==i||!Array.isArray(seg.records))throw Error('S162_ORPHAN_SHAPE');
  if(seg.records.length===off)return null;
  if(seg.records.length<=off||seg.records.length>SIZE)throw Error('S162_ORPHAN_SHAPE');
  // Authenticate committed prefix using previous head digest; do not trust orphaned records.
  if(off){const committed=h.segments[i];if(!committed||committed.count!==off)throw Error('S162_ORPHAN_COMMITTED_PREFIX');const prior=seg.records.slice(0,off);const p={...seg,records:prior,nodes:nodes(prior)};if(sha(Buffer.from(JSON.stringify(p)+'\n'))!==committed.digest)throw Error('S162_ORPHAN_PREFIX_TAMPER');}
  let prev=h.lastRecordHash;for(let j=off;j<seg.records.length;j++){const r=seg.records[j];if(r.sequence!==i*SIZE+j+1||r.prev!==prev||r.hash!==P.sha({schema:SCHEMA,id:this.id,sequence:r.sequence,prev:r.prev,txid:r.txid,payload:r.payload}))throw Error('S162_ORPHAN_CHAIN');prev=r.hash;}
  if(P.sha(seg.nodes)!==P.sha(nodes(seg.records)))throw Error('S162_ORPHAN_INDEX');
  return{schema:'oasis.sheet162.orphan.v1',resourceId:this.id,start:h.count,end:i*SIZE+seg.records.length,recordHashes:seg.records.slice(off).map(r=>r.hash),segmentDigest:sha(buf),headDigest:headDigest(h)};
 }
 _install(h,si,records,opts={}){const seg={schema:SCHEMA,id:this.id,index:si,records,nodes:nodes(records)},serialized=JSON.stringify(seg)+'\n',digest=sha(Buffer.from(serialized));
  write(segmentPath(this.dir,si),serialized);this.batchMetrics.segmentCommits++;
  if(opts.crashAfterSegment)throw Error('S162_INJECT_AFTER_SEGMENT');
  const oldLen=h.count%SIZE;const inserted=records.slice(oldLen),fullRoot=records.length===SIZE?seg.nodes['0:256']:null;const segments=h.segments.slice();segments[si]={index:si,count:records.length,digest,last:records.at(-1).hash,fullRoot};
  const upper={...h.upper};if(fullRoot){for(let size=SIZE*2;si%(size/SIZE)===size/SIZE-1;size*=2){const start=(si+1)*SIZE-size,half=size/2;const left=half===SIZE?segments[start/SIZE].fullRoot:upper[`${start}:${half}`];const right=half===SIZE?segments[(start+half)/SIZE].fullRoot:upper[`${start+half}:${half}`];if(!hex(left)||!hex(right))throw Error('S162_UPPER_INDEX');upper[`${start}:${size}`]=M.node(left,right);}}
  let state={count:h.count,frontier:h.frontier.slice()};for(const r of inserted)state=M.appendPeak(state.count,state.frontier,1,M.leaf(state.count,r.hash));
  const next={...h,count:state.count,frontier:state.frontier,root:M.root(state.count,state.frontier),lastRecordHash:records.at(-1).hash,segments,upper};
  write(this.headPath,next);this.batchMetrics.headCommits++;
  if(opts.crashAfterHead)throw Error('S162_INJECT_AFTER_HEAD');return next;
 }
 batch(rows,{expectedIndex,crashAfterSegment=false,crashAfterHead=false}={}){if(!Array.isArray(rows)||rows.length<1||rows.length>8)throw Error('S162_BATCH_BOUND');return lock(this.lockPath,()=>{
   // Store.read() fails closed if segment differs from previously durable head.
   const h=this.read(),start=expectedIndex===undefined?h.count:expectedIndex;
   if(start!==h.count)throw Error('S162_BATCH_CURSOR');
   if(h.count%SIZE+rows.length>SIZE)throw Error('S162_BATCH_CROSSES_SEGMENT');
   const si=Math.floor(h.count/SIZE),old=h.count%SIZE?(this.load(h,si).records):[],out=[],records=old.slice();let prev=h.lastRecordHash;
   for(let j=0;j<rows.length;j++){const row=rows[j];if(typeof row?.payload!=='string'||row.payload.length>256||typeof row.txid!=='string'||!/^[A-Za-z0-9_:-]{1,96}$/.test(row.txid))throw Error('S162_ROW_FORMAT');const r={sequence:h.count+j+1,prev,txid:row.txid,payload:row.payload};r.hash=P.sha({schema:SCHEMA,id:this.id,sequence:r.sequence,prev:r.prev,txid:r.txid,payload:r.payload});if(row.hash&&r.hash!==row.hash)throw Error('S162_ROW_HASH');prev=r.hash;records.push(r);out.push(r);}
   const next=this._install(h,si,records,{crashAfterSegment,crashAfterHead});this.batchMetrics.batches++;this.batchMetrics.records+=rows.length;
   return{records:out,head:next};
  });}
 reconcileOrphan(orphan,approvals,operatorKeys){return lock(this.lockPath,()=>{const actual=this.inspectOrphan();if(!actual||P.sha(actual)!==P.sha(orphan))throw Error('S162_ORPHAN_CHANGED');const seen=new Set();for(const a of approvals||[]){if(!operatorKeys[a.id]||seen.has(a.id)||!P.verify(operatorKeys[a.id],'S162:RECOVERY',orphan,a.signature))throw Error('S162_RECOVERY_SIGNATURE');seen.add(a.id);}if(seen.size<2)throw Error('S162_RECOVERY_QUORUM');
   const h=JSON.parse(fs.readFileSync(this.headPath,'utf8')),i=Math.floor(h.count/SIZE),s=JSON.parse(fs.readFileSync(segmentPath(this.dir,i),'utf8'));const next=this._installReconcile(h,i,s,actual.segmentDigest);return next;
  });}
 _installReconcile(h,si,seg,digest){ // Persist only head: never rewrite the existing orphaned segment.
  if(sha(fs.readFileSync(segmentPath(this.dir,si)))!==digest)throw Error('S162_ORPHAN_CHANGED');const fullRoot=seg.records.length===SIZE?seg.nodes['0:256']:null;
  const segments=h.segments.slice();segments[si]={index:si,count:seg.records.length,digest,last:seg.records.at(-1).hash,fullRoot};const upper={...h.upper};if(fullRoot){for(let size=SIZE*2;si%(size/SIZE)===size/SIZE-1;size*=2){const start=(si+1)*SIZE-size,half=size/2;const left=half===SIZE?segments[start/SIZE].fullRoot:upper[`${start}:${half}`];const right=half===SIZE?segments[(start+half)/SIZE].fullRoot:upper[`${start+half}:${half}`];if(!hex(left)||!hex(right))throw Error('S162_UPPER_INDEX');upper[`${start}:${size}`]=M.node(left,right);}}
  let state={count:h.count,frontier:h.frontier.slice()};for(const r of seg.records.slice(h.count%SIZE))state=M.appendPeak(state.count,state.frontier,1,M.leaf(state.count,r.hash));const next={...h,count:state.count,frontier:state.frontier,root:M.root(state.count,state.frontier),lastRecordHash:seg.records.at(-1).hash,segments,upper};write(this.headPath,next);return next;
 }
}
module.exports={BatchStore};
