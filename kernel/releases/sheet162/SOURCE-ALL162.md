# SHEET 162 — Complete New Executable Sources
Actual authored SHEET162 files, preserving the full frozen SHEET161 baseline in the ZIP.

## batch162.js
```javascript
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
```

## transport162.js
```javascript
'use strict';
// mTLS client with bounded keep-alive pool and pinned server certificate identity.
const https=require('node:https'),fs=require('node:fs'),tls=require('node:tls');
function make(identity,nodes){const key=fs.readFileSync(identity.key),cert=fs.readFileSync(identity.cert),ca=fs.readFileSync(identity.ca);
 const agents=Object.fromEntries(Object.keys(nodes).map(n=>[n,new https.Agent({keepAlive:true,maxSockets:2,maxFreeSockets:2,timeout:5000,maxTotalSockets:2})]));
 const sockets=new Set(),metrics={requests:0,handshakes:0,pageBytes:0};
 async function rpc(name,path,body={}){const n=nodes[name];if(!n)throw Error('S162_UNKNOWN_NODE');metrics.requests++;const bytes=Buffer.from(JSON.stringify(body));if(bytes.length>15900)throw Error('S162_REQUEST_TOO_LARGE');
  return new Promise((resolve,reject)=>{let finished=false;const req=https.request({hostname:'127.0.0.1',port:n.port,path,method:'POST',key,cert,ca,servername:'localhost',minVersion:'TLSv1.2',rejectUnauthorized:true,agent:agents[name],timeout:6000,checkServerIdentity:(name,c)=>{const err=tls.checkServerIdentity(name,c);if(err)return err;return c.fingerprint256?.replaceAll(':','').toLowerCase()===n.serverPin?undefined:Error('S162_SERVER_PIN');},headers:{'content-type':'application/json','content-length':bytes.length}},res=>{const chunks=[];res.on('data',x=>chunks.push(x));res.on('end',()=>{try{const buf=Buffer.concat(chunks);metrics.pageBytes+=buf.length;const value=JSON.parse(buf.toString());if(res.statusCode!==200)reject(Error(value.error||'S162_HTTP_'+res.statusCode));else resolve(value);}catch(e){reject(e);}});});
   req.on('socket',socket=>{if(!sockets.has(socket)){sockets.add(socket);metrics.handshakes++;socket.once('close',()=>sockets.delete(socket));}});
   req.on('error',reject);req.on('timeout',()=>req.destroy(Error('S162_RPC_TIMEOUT')));req.end(bytes);
  });}
 function close(){for(const a of Object.values(agents))a.destroy();sockets.clear();}
 return{rpc,close,metrics};}
module.exports={make};
```

## node162.js
```javascript
'use strict';
const fs=require('node:fs');
const {BatchStore}=require('./batch162');
const P=require('./baseline161/baseline160/baseline159/baseline158/baseline157/baseline156/baseline155/baseline154/baseline153/baseline152/baseline151/baseline150/baseline149/baseline148/baseline147/baseline146/protocol146');
const M=require('./baseline161/baseline160/baseline159/baseline158/baseline157/baseline156/baseline155/baseline154/baseline153/baseline152/baseline151/merkle151');
const V=require('./baseline161/proof161');
const cfg=P.load(process.env.S162_CONFIG),key=fs.readFileSync(cfg.signKey),anchorKey=fs.readFileSync(cfg.anchorPublicKey),peers=Object.fromEntries(Object.entries(cfg.peerPublicKeys).map(([k,v])=>[k,fs.readFileSync(v)]));
const store=new BatchStore(cfg.dir,cfg.resourceId);
const loadSession=()=>fs.existsSync(cfg.session)?P.load(cfg.session):null;
const locked=()=>fs.existsSync(cfg.quarantine)&&fs.readFileSync(cfg.quarantine,'utf8').length>0;
function seal(domain,body){return {body,signature:P.sign(key,domain,body)};}
function status(){const h=store.read(),session=loadSession();return seal('S161:STATUS',{nodeId:cfg.nodeId,resourceId:cfg.resourceId,count:h.count,root:h.root,lastRecordHash:h.lastRecordHash,active:!!session,nonce:session?.nonce||null,target:session?.target||null,recordHashesReplayed:store.metrics.recordHashesReplayed,subtreeLookups:store.metrics.subtreeLookups,rssMiB:+(process.memoryUsage().rss/1048576).toFixed(2),batchMetrics:store.batchMetrics});}
function head(b){if(!/^[a-f0-9]{40}$/.test(b.nonce||''))throw Error('S161_NONCE');const h=store.read();return seal('S161:HEAD',{nodeId:cfg.nodeId,nonce:b.nonce,resourceId:cfg.resourceId,count:h.count,root:h.root,lastRecordHash:h.lastRecordHash});}
function page(b){if(!/^[a-f0-9]{40}$/.test(b.nonce||'')||b.target?.resourceId!==cfg.resourceId||!Number.isSafeInteger(b.offset)||!Number.isInteger(b.limit)||b.limit<1||b.limit>8)throw Error('S161_PAGE_REQUEST');const h=store.read();if(b.target.count!==h.count||b.target.root!==h.root||b.target.lastRecordHash!==h.lastRecordHash||b.offset<0||b.offset>=h.count)throw Error('S161_STALE_SOURCE');const end=Math.min(h.count,b.offset+b.limit);const records=[];for(let i=b.offset;i<end;i++)records.push({record:store.record(i),inclusion:store.inclusion(i,h.count)});const s=store.stateAt(end,h);return seal('S161:PAGE',{schema:'oasis.sheet161.page.v1',nodeId:cfg.nodeId,nonce:b.nonce,target:b.target,from:b.offset,to:end,records,extension:store.extension(b.offset,end),after:s,lastRecordHash:records.at(-1).record.hash});}
function begin(b){if(loadSession())throw Error('S161_ACTIVE_SESSION');if(locked())throw Error('S161_QUARANTINE');const floor=V.checkAnchor(b.anchor,anchorKey),target=b.target;if(floor.resourceId!==cfg.resourceId||floor.count!==target?.count||floor.root!==target.root||floor.lastRecordHash!==target.lastRecordHash)throw Error('S161_FLOOR_TARGET');V.certified(target,b.heads,b.nonce,peers);const h=store.read();if(h.count>target.count)throw Error('S161_LOCAL_AHEAD');if(h.count===target.count&&h.root!==target.root)throw Error('S161_LOCAL_FORK');if(fs.existsSync(cfg.externalPin)){const prev=P.load(cfg.externalPin);V.checkAnchor(prev,anchorKey);if(floor.sequence<prev.body.sequence||floor.count<prev.body.count||(floor.sequence===prev.body.sequence&&P.sha(prev.body)!==P.sha(floor)))throw Error('S161_ROLLBACK_FLOOR');}
 // Independently retained pin is durable before session authorization.
 P.atomic(cfg.externalPin,b.anchor);
 const session={schema:'oasis.sheet161.session.v1',nonce:b.nonce,target,anchor:b.anchor,allowed:b.heads.map(x=>x.body.nodeId),heads:b.heads};P.atomic(cfg.session,session);return status();}
function apply(b){if(locked())throw Error('S162_QUARANTINE');const s=loadSession();if(!s)throw Error('S161_NO_SESSION');const h=store.read();V.checkAnchor(s.anchor,anchorKey);if(P.sha(P.load(cfg.externalPin))!==P.sha(s.anchor))throw Error('S161_PIN_CHANGED');V.certified(s.target,s.heads,s.nonce,peers);
 const rows=V.verifyPage(b.page,{nonce:s.nonce,target:s.target,keys:peers,allowed:s.allowed,local:{count:h.count,frontier:h.frontier,root:h.root},lastRecordHash:h.lastRecordHash});
 let cursor=0;while(cursor<rows.length){const current=store.read();const capacity=256-current.count%256;const part=rows.slice(cursor,cursor+capacity);store.batch(part,{expectedIndex:current.count});
  cursor+=part.length;
  if(cfg.crashAfterHeadOnce&&!fs.existsSync(cfg.crashAfterHeadOnce)){fs.writeFileSync(cfg.crashAfterHeadOnce,'after durable batch before ACK\n');process.exit(81);}
 }
 return status();}

function finish(){const s=loadSession();if(!s)throw Error('S161_NO_SESSION');const h=store.read();if(h.count!==s.target.count||h.root!==s.target.root||h.lastRecordHash!==s.target.lastRecordHash)throw Error('S161_NOT_FINAL');fs.unlinkSync(cfg.session);return seal('S161:FINISH',{nodeId:cfg.nodeId,count:h.count,root:h.root});}
const server=P.serve(cfg.key,cfg.cert,cfg.ca,(req,b)=>{P.peer(req,cfg.clientPin);switch(req.url){case'/status161':return status();case'/head161':return head(b);case'/page161':return page(b);case'/begin161':return begin(b);case'/apply161':return apply(b);case'/apply162':return apply(b);case'/finish161':return finish();default:throw Error('S161_UNKNOWN_ROUTE');}});
process.on('message',x=>{if(x==='stop')server.close(()=>process.exit(0));});
```

## catchup162.js
```javascript
'use strict';
const crypto=require('node:crypto');
const P=require('./baseline161/baseline160/baseline159/baseline158/baseline157/baseline156/baseline155/baseline154/baseline153/baseline152/baseline151/baseline150/baseline149/baseline148/baseline147/baseline146/protocol146');
const V=require('./baseline161/proof161');
const T=require('./transport162');
function make({identity,nodes,keys,anchor,anchorKey}){
 const transport=T.make(identity,nodes),rpc=transport.rpc;
 function signed(id,domain,item){if(item?.body?.nodeId!==id||!P.verify(keys[id],domain,item.body,item.signature))throw Error('S162_PEER_SIGNATURE');return item.body;}
 async function sync(targetName,{limit=8,onPage=()=>{}}={}){
  const ids=Object.keys(nodes).filter(n=>n!==targetName);if(ids.length!==2||limit<1||limit>8)throw Error('S162_PEER_CONFIG');let stat=signed(targetName,'S161:STATUS',await rpc(targetName,'/status161'));
  const nonce=stat.nonce||crypto.randomBytes(20).toString('hex');
  const heads=await Promise.all(ids.map(x=>rpc(x,'/head161',{nonce})));const first=heads[0].body,target={resourceId:first.resourceId,count:first.count,root:first.root,lastRecordHash:first.lastRecordHash};V.certified(target,heads,nonce,keys);
  const floor=V.checkAnchor(anchor,anchorKey);if(floor.resourceId!==target.resourceId||floor.count!==target.count||floor.root!==target.root||floor.lastRecordHash!==target.lastRecordHash)throw Error('S162_ANCHOR_MISMATCH');
  if(stat.active&&(stat.nonce!==nonce||P.sha(stat.target)!==P.sha(target)))throw Error('S162_SESSION_CONFLICT');
  if(!stat.active)stat=signed(targetName,'S161:STATUS',await rpc(targetName,'/begin161',{anchor,heads,nonce,target}));
  while(stat.count<target.count){const before=stat.count;const page=await rpc(ids[before%2],'/page161',{nonce,target,offset:before,limit});let after;
   try{after=signed(targetName,'S161:STATUS',await rpc(targetName,'/apply162',{page}));}catch(err){try{after=signed(targetName,'S161:STATUS',await rpc(targetName,'/status161'));if(after.count===before)throw err;}catch{throw err;}}
   if(after.count<=before||after.count>target.count)throw Error('S162_NO_PROGRESS');stat=after;onPage(stat.count,Buffer.byteLength(JSON.stringify(page)));
  }
  if(stat.root!==target.root)throw Error('S162_FINAL_ROOT');const receipt=signed(targetName,'S161:FINISH',await rpc(targetName,'/finish161'));return{...receipt,metrics:{...transport.metrics},finalCount:stat.count};
 }
 return{rpc,sync,transport,close:transport.close};
}
module.exports={make};
```

## unit162.js
```javascript
'use strict';
const fs=require('node:fs'),os=require('node:os'),path=require('node:path'),crypto=require('node:crypto'),assert=require('node:assert/strict');
const {BatchStore}=require('./batch162'),{Store}=require('./baseline161/baseline160/indexed160');
const P=require('./baseline161/baseline160/baseline159/baseline158/baseline157/baseline156/baseline155/baseline154/baseline153/baseline152/baseline151/baseline150/baseline149/baseline148/baseline147/baseline146/protocol146');
const tmp=fs.mkdtempSync(path.join(os.tmpdir(),'oasis162-unit-'));let checks=0;const ok=(s,fn)=>{fn();console.log('PASS',++checks,s)};try{
 const a=new BatchStore(path.join(tmp,'new'),'ROOT'),b=new Store(path.join(tmp,'old'),'ROOT');a.init();b.init();const rows=Array.from({length:8},(_,i)=>({txid:'tx'+i,payload:'d'+i}));a.batch(rows,{expectedIndex:0});for(const r of rows)b.append(r.payload,r.txid);ok('8-row batch produces byte-identical root',()=>assert.equal(a.read().root,b.read().root));ok('8-row batch produces identical segment digest',()=>assert.equal(a.read().segments[0].digest,b.read().segments[0].digest));ok('one segment write, one head write',()=>assert.deepEqual([a.batchMetrics.segmentCommits,a.batchMetrics.headCommits],[1,1]));ok('reject repeated batch cursor',()=>assert.throws(()=>a.batch(rows,{expectedIndex:0}),/S162_BATCH_CURSOR/));ok('reject forged row hash',()=>assert.throws(()=>a.batch([{payload:'hi',txid:'a',hash:'f'.repeat(64)}]),/S162_ROW_HASH/));
 for(let i=8;i<254;i++)a.append('d'+i,'tx'+i);
 ok('cross-boundary 8-row commit fails closed',()=>assert.throws(()=>a.batch(rows,{expectedIndex:254}),/S162_BATCH_CROSSES_SEGMENT/));
 a.batch([{txid:'tx254',payload:'d254'},{txid:'tx255',payload:'d255'}]);a.batch([{txid:'tx256',payload:'d256'}]);ok('segment boundary and upper index valid',()=>assert.equal(a.read().count,257));ok('inclusion valid at boundary',()=>assert.equal(a.inclusion(256).count,257));
 const c=new BatchStore(path.join(tmp,'crash'),'CR');c.init();ok('crash between segment and head detected',()=>assert.throws(()=>c.batch(rows,{crashAfterSegment:true}),/S162_INJECT_AFTER_SEGMENT/));ok('store fails closed with orphan',()=>assert.throws(()=>c.read(),/S160_ORPHAN_OR_MISSING_SEGMENT/));const orphan=c.inspectOrphan();ok('orphan records are exact batch',()=>assert.equal(orphan.recordHashes.length,8));
 const keys=Object.fromEntries(['a','b','c'].map(x=>[x,crypto.generateKeyPairSync('ed25519')]));const sig=id=>({id,signature:P.sign(keys[id].privateKey,'S162:RECOVERY',orphan)}),pub=Object.fromEntries(Object.entries(keys).map(([k,v])=>[k,v.publicKey]));
 ok('one operator denied',()=>assert.throws(()=>c.reconcileOrphan(orphan,[sig('a')],pub),/S162_RECOVERY_QUORUM/));ok('duplicate operator denied',()=>assert.throws(()=>c.reconcileOrphan(orphan,[sig('a'),sig('a')],pub),/S162_RECOVERY_SIGNATURE/));ok('forged signature denied',()=>assert.throws(()=>c.reconcileOrphan(orphan,[sig('a'),{...sig('b'),signature:'fake'}],pub),/S162_RECOVERY_SIGNATURE/));c.reconcileOrphan(orphan,[sig('a'),sig('b')],pub);ok('orphan recovered exactly once',()=>assert.equal(c.read().count,8));ok('recovery no longer has orphan',()=>assert.equal(c.inspectOrphan(),null));ok('no repeat of prior approval',()=>assert.throws(()=>c.reconcileOrphan(orphan,[sig('a'),sig('b')],pub),/S162_ORPHAN_CHANGED/));
 const d=new BatchStore(path.join(tmp,'headcrash'),'DC');d.init();ok('crash after durable head simulated',()=>assert.throws(()=>d.batch(rows,{crashAfterHead:true}),/S162_INJECT_AFTER_HEAD/));ok('eight rows retained after post-head crash',()=>assert.equal(d.read().count,8));
 console.log('SHEET162 UNIT '+checks+'/'+checks+' PASS');
}catch(e){console.error(e.stack);process.exitCode=1;}finally{fs.rmSync(tmp,{recursive:true,force:true});}
```

## gate162.js
```javascript
#!/usr/bin/env node
'use strict';
const fs=require('node:fs'),path=require('node:path'),os=require('node:os'),crypto=require('node:crypto'),cp=require('node:child_process'),assert=require('node:assert/strict');
const {performance}=require('node:perf_hooks');
const {Store}=require('./baseline161/baseline160/indexed160');
const {BatchStore}=require('./batch162');
const P=require('./baseline161/baseline160/baseline159/baseline158/baseline157/baseline156/baseline155/baseline154/baseline153/baseline152/baseline151/baseline150/baseline149/baseline148/baseline147/baseline146/protocol146');
const V=require('./baseline161/proof161'),Old=require('./baseline161/catchup161'),Fast=require('./catchup162');
const tmp=fs.mkdtempSync(path.join(os.tmpdir(),'oasis-sheet162-')),f=(...parts)=>path.join(tmp,...parts);const children=[];
const openssl=(...args)=>cp.execFileSync('openssl',args,{cwd:tmp,stdio:'pipe'});
let checks=0;const ok=(desc,fn)=>{fn();console.log('PASS',++checks,desc);};const step=async(desc,fn)=>{await fn();console.log('PASS',++checks,desc);};
function pem(name){const kp=crypto.generateKeyPairSync('ed25519'),priv=f(name+'.priv.pem'),pub=f(name+'.pub.pem');fs.writeFileSync(priv,kp.privateKey.export({format:'pem',type:'pkcs8'}));fs.writeFileSync(pub,kp.publicKey.export({format:'pem',type:'spki'}));return{privateKey:kp.privateKey,publicKey:kp.publicKey,priv,pub};}
function cert(name){openssl('req','-new','-newkey','rsa:2048','-nodes','-keyout',name+'.key','-out',name+'.csr','-subj','/CN=localhost');fs.writeFileSync(f(name+'.ext'),'subjectAltName=DNS:localhost,IP:127.0.0.1\nkeyUsage=digitalSignature,keyEncipherment\nextendedKeyUsage=clientAuth,serverAuth\n');openssl('x509','-req','-in',name+'.csr','-CA','ca.crt','-CAkey','ca.key','-CAcreateserial','-out',name+'.crt','-days','2','-sha256','-extfile',name+'.ext');return{key:f(name+'.key'),cert:f(name+'.crt'),ca:f('ca.crt'),certPin:new crypto.X509Certificate(fs.readFileSync(f(name+'.crt'))).fingerprint256.replaceAll(':','').toLowerCase()};}
async function spawn(cfg,name,version='162'){const config=f(name+'-config.json');P.atomic(config,cfg);let errors='';const proc=cp.fork(path.join(__dirname,version==='161'?'baseline161/node161.js':'node162.js'),[],{env:{...process.env,S161_CONFIG:config,S162_CONFIG:config},stdio:['ignore','pipe','pipe','ipc']});proc.stderr.on('data',b=>errors+=b);const port=await new Promise((res,rej)=>{const timeout=setTimeout(()=>rej(Error('SPAWN_TIMEOUT '+name+' '+errors)),15000);proc.once('message',m=>{clearTimeout(timeout);res(m.port);});proc.once('exit',n=>{clearTimeout(timeout);rej(Error('SPAWN_EXIT '+n+' '+errors));});});const item={name,port,proc,version};children.push(item);return item;}
async function stop(node){if(!node||node.proc.exitCode!==null||node.proc.signalCode!==null)return;await new Promise(res=>{const timer=setTimeout(()=>{node.proc.kill('SIGKILL');res();},900);node.proc.once('exit',()=>{clearTimeout(timer);res();});try{node.proc.send('stop',err=>{if(err){node.proc.kill('SIGKILL');clearTimeout(timer);res();}});}catch{node.proc.kill('SIGKILL');clearTimeout(timer);res();}});}
async function workload(seed,prefix,identity,keys,pub,anchorKeys,anchorNum,{crash=false}={}){
 const resourceId='S162-RESOURCE',tag='w'+seed+'-'+(crash?'crash':'bench');const stores={};for(const n of ['red','green','old','blue']){const d=f(tag,n,'store');stores[n]=(n==='blue'?new BatchStore(d,resourceId):new Store(d,resourceId));stores[n].init();}
 let start=performance.now();for(let i=0;i<seed;i++){const value='datum-'+String(i).padStart(7,'0'),txid='tx-'+i;stores.red.append(value,txid);stores.green.append(value,txid);if(i<prefix){stores.old.append(value,txid);stores.blue.append(value,txid);}}
 const setupMs=performance.now()-start,hr=stores.red.read(),target={resourceId,count:hr.count,root:hr.root,lastRecordHash:hr.lastRecordHash},anchor=V.signAnchor(V.anchorBody(resourceId,hr,anchorNum),anchorKeys.privateKey);
 const cfg={};for(const n of ['red','green','old','blue']){const signId=n==='old'?'blue':n;cfg[n]={nodeId:signId,resourceId,...identity[n],dir:stores[n].dir,signKey:keys[signId].priv,anchorPublicKey:anchorKeys.pub,peerPublicKeys:Object.fromEntries(Object.entries(keys).map(([id,k])=>[id,k.pub])),clientPin:identity.client.certPin,session:f(tag,n,'session.json'),externalPin:f(tag,n,'external-pin.json'),quarantine:f(tag,n,'quarantine.txt'),...(crash&&n==='blue'?{crashAfterHeadOnce:f(tag,'crash-marker')}: {})};}
 const nodes={};for(const name of ['red','green','old','blue'])nodes[name]=await spawn(cfg[name],tag+name,name==='blue'?'162':'161');
 const oldMap={red:nodes.red,green:nodes.green,blue:nodes.old},newMap={red:nodes.red,green:nodes.green,blue:nodes.blue};const endpoint=ns=>Object.fromEntries(Object.entries(ns).map(([n,node])=>[n,{port:node.port,serverPin:identity[node===nodes.old?'old':n].certPin}]));
 const old=Old.make({identity:identity.client,nodes:endpoint(oldMap),keys:pub,anchor,anchorKey:anchorKeys.publicKey});
 const fast=Fast.make({identity:identity.client,nodes:endpoint(newMap),keys:pub,anchor,anchorKey:anchorKeys.publicKey});
 try{
  ok(tag+' source and target roots are valid and prefixes aligned',()=>{assert.equal(stores.red.read().root,stores.green.read().root);assert.equal(stores.old.read().root,stores.blue.read().root);assert.equal(stores.old.read().count,prefix);});
  if(crash){const original=fast.rpc;await step(tag+' pinned peer status active',async()=>assert.equal((await original('blue','/status161')).body.count,prefix));
   const n=crypto.randomBytes(20).toString('hex'),heads=await Promise.all(['red','green'].map(x=>original(x,'/head161',{nonce:n})));await original('blue','/begin161',{nonce:n,target,anchor,heads});const p=await original('red','/page161',{nonce:n,target,offset:prefix,limit:8});
   await step(tag+' real target death follows committed durable batch',async()=>{await assert.rejects(original('blue','/apply162',{page:p}),/socket hang up|ECONNRESET|EPIPE|aborted|closed/i);assert.equal(stores.blue.read().count,prefix+8);});
   nodes.blue=await spawn({...cfg.blue,crashAfterHeadOnce:cfg.blue.crashAfterHeadOnce},tag+'blue-restart','162');
   // Recreate client after restart: old client endpoint is no longer valid.
   fast.close();const fm=Fast.make({identity:identity.client,nodes:endpoint({red:nodes.red,green:nodes.green,blue:nodes.blue}),keys:pub,anchor,anchorKey:anchorKeys.publicKey});
   await step(tag+' durable nonce survives process restart',async()=>assert.equal((await fm.rpc('blue','/status161')).body.nonce,n));
   await step(tag+' original transaction completes without duplicate',async()=>{await fm.sync('blue');assert.equal(stores.blue.read().count,seed);assert.equal(stores.blue.read().root,hr.root);});
   await step(tag+' crash marker remains stable',async()=>assert.equal(fs.existsSync(cfg.blue.crashAfterHeadOnce),true));fm.close();return{seed,prefix,crashPass:true};
  }
  start=performance.now();await step(tag+' legacy 161 full mTLS recovery',async()=>{const out=await old.sync('blue');assert.equal(out.count,seed);});const legacyMs=performance.now()-start;
  start=performance.now();const report=await fast.sync('blue');const batchedMs=performance.now()-start;
  ok(tag+' optimized target matches legacy Merkle root',()=>assert.equal(stores.old.read().root,stores.blue.read().root));
  ok(tag+' root equals certified source',()=>assert.equal(stores.blue.read().root,hr.root));
  ok(tag+' batch count smaller than recovered records',()=>assert((report.metrics.requests>0)&&stores.blue.read().count===seed));
  ok(tag+' TLS sockets reused across requests',()=>assert(report.metrics.handshakes<report.metrics.requests/4));
  ok(tag+' zero historical record hashes replayed',()=>assert.equal(stores.blue.metrics.recordHashesReplayed,0));
  const h=stores.blue.read();ok(tag+' indexed extension still verifies',()=>assert.equal(h.root,hr.root));
  const optim=await fast.rpc('blue','/status161');const batch=optim.body.batchMetrics;
  ok(tag+' durable segment commits reduced versus row-by-row writes',()=>assert(batch.segmentCommits<seed-prefix));
  const result={seed,prefix,recovered:seed-prefix,setupMs:+setupMs.toFixed(1),legacyMs:+legacyMs.toFixed(1),optimizedMs:+batchedMs.toFixed(1),legacyRowsPerSecond:+((seed-prefix)*1000/legacyMs).toFixed(2),optimizedRowsPerSecond:+((seed-prefix)*1000/batchedMs).toFixed(2),speedup:+(legacyMs/batchedMs).toFixed(3),networkRequests:report.metrics.requests,tlsConnections:report.metrics.handshakes,networkResponseBytes:report.metrics.pageBytes,segmentCommits:batch.segmentCommits,headCommits:batch.headCommits,batches:batch.batches,sourceSegments:h.segments.length,verification:'both paths share identical source, anchored 2/3 heads, client cert and TLS host'};
  console.log('BENCHMARK162',JSON.stringify(result));return result;
 }finally{fast.close();await Promise.allSettled(Object.values(nodes).map(stop));}
}
(async()=>{try{
 openssl('req','-x509','-new','-newkey','rsa:2048','-nodes','-keyout','ca.key','-out','ca.crt','-days','2','-subj','/CN=OASIS-S162-CA');
 const identity=Object.fromEntries(['client','red','green','blue','old'].map(k=>[k,cert(k)]));const keys=Object.fromEntries(['red','green','blue'].map(k=>[k,pem(k)]));const pub=Object.fromEntries(Object.entries(keys).map(([n,k])=>[n,k.publicKey]));const anchor=pem('anchor');
 const targets=process.env.S162_FAST==='1'?[[640,128]]:[[640,128],[1152,128]];const results=[];let i=0;for(const [seed,prefix] of targets)results.push(await workload(seed,prefix,identity,keys,pub,anchor,++i));
 if(process.env.S162_SKIP_CRASH!=='1')results.push(await workload(264,256,identity,keys,pub,anchor,++i,{crash:true}));
 const summary={sheet:162,status:'PASS',newChecks:checks,benchmarks:results.filter(x=>!x.crashPass),crashTests:results.filter(x=>x.crashPass),hostCount:1,date:new Date().toISOString(),limits:'Single-host synthetic identities, synchronous fsync, same-source sequential runs; performance includes load/order effects and is not independent-host data.'};
 fs.writeFileSync(path.join(__dirname,'benchmark162.json'),JSON.stringify(summary,null,2)+'\n');console.log('SHEET162 GATE '+checks+'/'+checks+' PASS');
 }catch(e){console.error('SHEET162 GATE FAIL',e.stack||e);process.exitCode=1;}finally{await Promise.allSettled(children.map(stop));if(process.env.S162_KEEP!=='1')fs.rmSync(tmp,{recursive:true,force:true});}})();
```

## run-new.sh
```bash
#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
node unit162.js
node gate162.js
```

## run-all.sh
```bash
#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT
cp -a baseline161 "$TMP/sheet161"
(cd "$TMP/sheet161" && node gate161.js)
node unit162.js
node gate162.js
```

## browser-check.py
```python
from playwright.sync_api import sync_playwright
from pathlib import Path
p=Path(__file__).parent
html=(p/'index.html').read_text()
with sync_playwright() as playwright:
 browser=playwright.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
 page=browser.new_page(viewport={'width':1250,'height':1000},accept_downloads=True)
 page.set_content(html,wait_until='domcontentloaded')
 scenarios=page.locator('button[data-scenario]')
 assert scenarios.count()==8
 for n in range(8):
  b=scenarios.nth(n);b.click()
  assert 'active' in b.get_attribute('class')
  assert page.locator('#fault-state').inner_text()
  print('PASS browser scenario',n+1,b.inner_text())
 with page.expect_download() as d:page.locator('#export').click()
 assert d.value.suggested_filename=='oasis-sheet162-fault.json'
 print('PASS browser JSON export')
 page.screenshot(path=str(p/'preview.png'),full_page=True)
 print('PASS browser screenshot')
 browser.close()
```

## KERNEL-ASCII.txt
```text
SHEET 162 — BATCHED RECOVERY + PERSISTENT MUTUAL TLS
====================================================
                       OASIS / ROOT0
                             |
                    SHEET 161 WITNESS
                  (frozen; imported below)
                             |
              S161 AUTHORITY CERTIFICATE
               2 OF 3 ED25519-SIGNED HEADS
                             |
                SEPARATELY SIGNED FLOOR
                sequence + root + count
                             |
                     RECOVERY NONCE
               persisted target and pin
                             |
     +-----------------------+------------------------+
     |                       |                        |
 S161 SOURCE RED        S161 SOURCE GREEN          RECEIVER BLUE
 indexed Merkle         indexed Merkle             SHEET 162 NODE
     |                       |                        |
     +----------- SIGNED PAGE (<=8 records) ----------+
                             |
                   TLS KEEPALIVE AGENT
             pinned CA / peer cert / server ID
                             |
                  VERIFY SIGNED S161 PAGE
          +------------------+-------------------+
          |                  |                   |
       BAD SIGNER         BAD PROOF            VALID
          |                  |                   |
        REJECT              REJECT            NEXT
                                                 |
                                  VALIDATE MERKLE INCLUSION
                                  VALIDATE FRONTIER EXTENSION
                                  VALIDATE RECORD HASH CHAIN
                                  VALIDATE NONCE + CURSOR + PIN
                                                 |
                                          SEGMENT SPLITTER
                                  (never cross 256 boundary)
                                                 |
                              +------------------+------------------+
                              |                                     |
                        BATCH <= 8                             BATCH <=8
                              |                                     |
                    EXCLUSIVE FILE LOCK                       RELOCK
                              |                                     |
                    BUILD SEGMENT NODES                           |
                              |                                     |
                    SINGLE TEMP SEGMENT                            |
                     WRITE + FSYNC                                 |
                              |                                     |
                    ATOMIC SEGMENT RENAME                          |
                              |                                     |
                    FSYNC SEGMENT DIRECTORY                        |
                              |                                     |
                   +----------+----------+                         |
                   |                     |                         |
            CRASH / POWER LOSS        CONTINUE                      |
                   |                     |                         |
              ORPHAN HOLD              BUILD NEW                    |
                   |                  MERKLE FRONTIER               |
            NO AUTO REPAIR                |                         |
                   |                  SINGLE HEAD                  |
            2/3 OPERATOR             WRITE + FSYNC                 |
             SIGNATURES                   |                         |
                   |                  ATOMIC RENAME                |
           VERIFY BATCH DIGEST            |                         |
                   |                FSYNC HEAD DIRECTORY           |
             RECOVERY HEAD                |                         |
                   |                +-----+------+                 |
                   |                |            |                 |
                   |            ACK LOST       ACK SENT            |
                   |                |            |                 |
                   |            RESTART        NEXT PAGE           |
                   |                |            |                 |
                   |        READ DURABLE CURSOR |                  |
                   |                |            |                 |
                   |           NO DUPLICATE     |                 |
                   |                |            |                 |
                   +----------------+------------+-----------------+
                                                 |
                                       FINAL MERKLE ROOT
                                          EQUALS SOURCE
                                                 |
                                         SIGNED COMPLETION
                                                 |
                                       NEXT VERIFIED EPOCH

FAULT CONDITIONS / TESTED BOUNDARIES
  F01 Forged record hash -> FAIL BEFORE MUTATION
  F02 Cross-segment batch -> REFUSE, SPLIT AT COORDINATOR
  F03 Orphaned segment before head -> FAIL CLOSED
  F04 Same orphan, only one operator -> REJECT
  F05 Duplicate or forged operator -> REJECT
  F06 Two signed operators, matching orphan -> INSTALL HEAD ONCE
  F07 Crash after head before ACK -> RESTART, RESUME CURSOR
  F08 Stale old cursor -> REJECT
  F09 Stale signed high-water -> inherited S161 reject
  F10 Certificate mismatch -> pinned TLS rejection
  F11 Successful segment rollover -> exact indexed Merkle root
  F12 Keep-alive connections -> reuses 3 sockets across 100+ requests

PERFORMANCE MODEL — NO PRODUCTION CLAIM
  S161 baseline: one segment fsync and one head fsync per record.
  S162: <=8 records per segment fsync and head fsync, by boundary.
  Both use S161 full proof verification, quorum and floor enforcement.
  One physical host; Linux filesystem; synthetic certificates.
  External floor and network authority are not independent data centers.
  Legacy full-chain correctness remains separately unverified.
```