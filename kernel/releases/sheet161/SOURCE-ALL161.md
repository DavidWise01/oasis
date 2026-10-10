# SHEET 161 — Exact New Executable Sources

The full SHEET160 frozen lineage is included only in the complete ZIP. Copy each fenced source to its named file or download the release.

## proof161.js

```javascript
'use strict';
const P=require('./baseline160/baseline159/baseline158/baseline157/baseline156/baseline155/baseline154/baseline153/baseline152/baseline151/baseline150/baseline149/baseline148/baseline147/baseline146/protocol146');
const M=require('./baseline160/baseline159/baseline158/baseline157/baseline156/baseline155/baseline154/baseline153/baseline152/baseline151/merkle151');
const crypto=require('node:crypto');
const SCHEMA='oasis.sheet161.anchor.v1';
function anchorBody(resourceId,head,sequence=1){return {schema:SCHEMA,resourceId,count:head.count,root:head.root,lastRecordHash:head.lastRecordHash,sequence};}
function signAnchor(body,privateKey){return {body,signature:P.sign(privateKey,'S161:ANCHOR',body)};}
function checkAnchor(signed,pub){const b=signed?.body;if(b?.schema!==SCHEMA||!Number.isSafeInteger(b.count)||b.count<0||!Number.isSafeInteger(b.sequence)||b.sequence<1||!P.verify(pub,'S161:ANCHOR',b,signed.signature))throw Error('S161_ANCHOR_SIGNATURE');return b;}
function certified(target,heads,nonce,keys){if(!/^[a-f0-9]{40}$/.test(nonce||'')||!target||!Number.isSafeInteger(target.count)||target.count<0)throw Error('S161_CERT_TARGET');let ids=new Set();for(const item of heads||[]){const b=item?.body;if(!keys[b?.nodeId]||ids.has(b.nodeId)||b.nonce!==nonce||b.resourceId!==target.resourceId||b.count!==target.count||b.root!==target.root||b.lastRecordHash!==target.lastRecordHash||!P.verify(keys[b.nodeId],'S161:HEAD',b,item.signature))throw Error('S161_CERT_SIGNATURE');ids.add(b.nodeId);}if(ids.size<2)throw Error('S161_CERT_QUORUM');return true;}
function verifyPage(page,ctx){const b=page?.body,signer=b?.nodeId;if(!ctx.keys[signer]||!ctx.allowed.includes(signer)||!P.verify(ctx.keys[signer],'S161:PAGE',b,page.signature))throw Error('S161_PAGE_SIGNATURE');if(b.schema!=='oasis.sheet161.page.v1'||b.nonce!==ctx.nonce||P.sha(b.target)!==P.sha(ctx.target)||b.from!==ctx.local.count||b.records?.length<1||b.records?.length>8||b.to!==b.from+b.records.length||b.to>ctx.target.count)throw Error('S161_PAGE_CONTEXT');
 const after=b.after; if(!after||after.count!==b.to||M.root(after.count,after.frontier)!==after.root)throw Error('S161_PAGE_AFTER');M.verifyExtension(ctx.local,b.extension,after);
 let acc={count:ctx.local.count,frontier:ctx.local.frontier.slice()};let last=ctx.lastRecordHash;
 for(let i=0;i<b.records.length;i++){
  const entry=b.records[i],r=entry.record;
  if(r.sequence!==b.from+i+1||r.prev!==last||r.hash!==P.sha({schema:'oasis.sheet160.indexed.v1',id:ctx.target.resourceId,sequence:r.sequence,prev:r.prev,txid:r.txid,payload:r.payload}))throw Error('S161_RECORD_CHAIN');
  if(entry.inclusion.index!==b.from+i||entry.inclusion.count!==ctx.target.count||!M.verifyInclusion(entry.inclusion,ctx.target.root,r.hash))throw Error('S161_RECORD_INCLUSION');
  acc=M.appendPeak(acc.count,acc.frontier,1,M.leaf(acc.count,r.hash));last=r.hash;
 }
 if(acc.count!==after.count||M.root(acc.count,acc.frontier)!==after.root||last!==b.lastRecordHash)throw Error('S161_PAGE_ROOT');
 if(b.to===ctx.target.count&&last!==ctx.target.lastRecordHash)throw Error('S161_FINAL_TAIL');
 return b.records.map(x=>x.record);
}
module.exports={SCHEMA,anchorBody,signAnchor,checkAnchor,certified,verifyPage};
```

## node161.js

```javascript
'use strict';
const fs=require('node:fs');
const {Store}=require('./baseline160/indexed160');
const P=require('./baseline160/baseline159/baseline158/baseline157/baseline156/baseline155/baseline154/baseline153/baseline152/baseline151/baseline150/baseline149/baseline148/baseline147/baseline146/protocol146');
const M=require('./baseline160/baseline159/baseline158/baseline157/baseline156/baseline155/baseline154/baseline153/baseline152/baseline151/merkle151');
const V=require('./proof161');
const cfg=P.load(process.env.S161_CONFIG),key=fs.readFileSync(cfg.signKey),anchorKey=fs.readFileSync(cfg.anchorPublicKey),peers=Object.fromEntries(Object.entries(cfg.peerPublicKeys).map(([k,v])=>[k,fs.readFileSync(v)]));
const store=new Store(cfg.dir,cfg.resourceId);
const loadSession=()=>fs.existsSync(cfg.session)?P.load(cfg.session):null;
const locked=()=>fs.existsSync(cfg.quarantine)&&fs.readFileSync(cfg.quarantine,'utf8').length>0;
function seal(domain,body){return {body,signature:P.sign(key,domain,body)};}
function status(){const h=store.read(),session=loadSession();return seal('S161:STATUS',{nodeId:cfg.nodeId,resourceId:cfg.resourceId,count:h.count,root:h.root,lastRecordHash:h.lastRecordHash,active:!!session,nonce:session?.nonce||null,target:session?.target||null,recordHashesReplayed:store.metrics.recordHashesReplayed,subtreeLookups:store.metrics.subtreeLookups,rssMiB:+(process.memoryUsage().rss/1048576).toFixed(2)});}
function head(b){if(!/^[a-f0-9]{40}$/.test(b.nonce||''))throw Error('S161_NONCE');const h=store.read();return seal('S161:HEAD',{nodeId:cfg.nodeId,nonce:b.nonce,resourceId:cfg.resourceId,count:h.count,root:h.root,lastRecordHash:h.lastRecordHash});}
function page(b){if(!/^[a-f0-9]{40}$/.test(b.nonce||'')||b.target?.resourceId!==cfg.resourceId||!Number.isSafeInteger(b.offset)||!Number.isInteger(b.limit)||b.limit<1||b.limit>8)throw Error('S161_PAGE_REQUEST');const h=store.read();if(b.target.count!==h.count||b.target.root!==h.root||b.target.lastRecordHash!==h.lastRecordHash||b.offset<0||b.offset>=h.count)throw Error('S161_STALE_SOURCE');const end=Math.min(h.count,b.offset+b.limit);const records=[];for(let i=b.offset;i<end;i++)records.push({record:store.record(i),inclusion:store.inclusion(i,h.count)});const s=store.stateAt(end,h);return seal('S161:PAGE',{schema:'oasis.sheet161.page.v1',nodeId:cfg.nodeId,nonce:b.nonce,target:b.target,from:b.offset,to:end,records,extension:store.extension(b.offset,end),after:s,lastRecordHash:records.at(-1).record.hash});}
function begin(b){if(loadSession())throw Error('S161_ACTIVE_SESSION');if(locked())throw Error('S161_QUARANTINE');const floor=V.checkAnchor(b.anchor,anchorKey),target=b.target;if(floor.resourceId!==cfg.resourceId||floor.count!==target?.count||floor.root!==target.root||floor.lastRecordHash!==target.lastRecordHash)throw Error('S161_FLOOR_TARGET');V.certified(target,b.heads,b.nonce,peers);const h=store.read();if(h.count>target.count)throw Error('S161_LOCAL_AHEAD');if(h.count===target.count&&h.root!==target.root)throw Error('S161_LOCAL_FORK');if(fs.existsSync(cfg.externalPin)){const prev=P.load(cfg.externalPin);V.checkAnchor(prev,anchorKey);if(floor.sequence<prev.body.sequence||floor.count<prev.body.count||(floor.sequence===prev.body.sequence&&P.sha(prev.body)!==P.sha(floor)))throw Error('S161_ROLLBACK_FLOOR');}
 // Independently retained pin is durable before session authorization.
 P.atomic(cfg.externalPin,b.anchor);
 const session={schema:'oasis.sheet161.session.v1',nonce:b.nonce,target,anchor:b.anchor,allowed:b.heads.map(x=>x.body.nodeId),heads:b.heads};P.atomic(cfg.session,session);return status();}
function apply(b){if(locked())throw Error('S161_QUARANTINE');const s=loadSession();if(!s)throw Error('S161_NO_SESSION');const h=store.read();V.checkAnchor(s.anchor,anchorKey);if(P.sha(P.load(cfg.externalPin))!==P.sha(s.anchor))throw Error('S161_PIN_CHANGED');V.certified(s.target,s.heads,s.nonce,peers);
 const page=b.page;
 // Authenticate proof against durable cursor BEFORE writing anything.
 const rows=V.verifyPage(page,{nonce:s.nonce,target:s.target,keys:peers,allowed:s.allowed,local:{count:h.count,frontier:h.frontier,root:h.root},lastRecordHash:h.lastRecordHash});
 let first=true;for(const row of rows){const n=store.read().count;const saved=store.append(row.payload,row.txid,{expectedIndex:n});if(saved.record.hash!==row.hash)throw Error('S161_WRITER_HASH_MISMATCH');if(cfg.crashOnce&&first&&!fs.existsSync(cfg.crashOnce)){fs.writeFileSync(cfg.crashOnce,'post-fsync-pre-ack\n');process.exit(81);}first=false;}
 return status();}
function finish(){const s=loadSession();if(!s)throw Error('S161_NO_SESSION');const h=store.read();if(h.count!==s.target.count||h.root!==s.target.root||h.lastRecordHash!==s.target.lastRecordHash)throw Error('S161_NOT_FINAL');fs.unlinkSync(cfg.session);return seal('S161:FINISH',{nodeId:cfg.nodeId,count:h.count,root:h.root});}
const server=P.serve(cfg.key,cfg.cert,cfg.ca,(req,b)=>{P.peer(req,cfg.clientPin);switch(req.url){case'/status161':return status();case'/head161':return head(b);case'/page161':return page(b);case'/begin161':return begin(b);case'/apply161':return apply(b);case'/finish161':return finish();default:throw Error('S161_UNKNOWN_ROUTE');}});
process.on('message',x=>{if(x==='stop')server.close(()=>process.exit(0));});
```

## catchup161.js

```javascript
'use strict';
const crypto=require('node:crypto');
const P=require('./baseline160/baseline159/baseline158/baseline157/baseline156/baseline155/baseline154/baseline153/baseline152/baseline151/baseline150/baseline149/baseline148/baseline147/baseline146/protocol146');
const V=require('./proof161');
function make({identity,nodes,keys,anchor,anchorKey}){
 const rpc=(name,path,body={})=>P.rpc({...identity,...nodes[name]},path,body);
 function verifySigned(id,domain,item){if(item?.body?.nodeId!==id||!P.verify(keys[id],domain,item.body,item.signature))throw Error('S161_PEER_SIGNATURE');return item.body;}
 async function sync(targetName,{limit=8,onPage=()=>{},nonce:forcedNonce}={}){
  const nodeIds=Object.keys(nodes).filter(x=>x!==targetName);
  let stat=verifySigned(targetName,'S161:STATUS',await rpc(targetName,'/status161'));
  const nonce=forcedNonce||stat.nonce||crypto.randomBytes(20).toString('hex');
  if(nodeIds.length!==2||limit<1||limit>8)throw Error('S161_SYNC_CONFIG');
  const heads=await Promise.all(nodeIds.map(id=>rpc(id,'/head161',{nonce})));const source=heads[0].body;
  const target={resourceId:source.resourceId,count:source.count,root:source.root,lastRecordHash:source.lastRecordHash};
  V.certified(target,heads,nonce,keys);const pinned=V.checkAnchor(anchor,anchorKey);
  if(pinned.resourceId!==target.resourceId||pinned.count!==target.count||pinned.root!==target.root||pinned.lastRecordHash!==target.lastRecordHash)throw Error('S161_EXTERNAL_ANCHOR_MISMATCH');
  if(stat.active&&(stat.nonce!==nonce||P.sha(stat.target)!==P.sha(target)))throw Error('S161_SESSION_TARGET_MISMATCH');
  if(!stat.active){stat=verifySigned(targetName,'S161:STATUS',await rpc(targetName,'/begin161',{anchor,heads,nonce,target}));}
  while(stat.count<target.count){const src=nodeIds[stat.count%2],page=await rpc(src,'/page161',{nonce,target,offset:stat.count,limit});let before=stat.count;
   try{stat=verifySigned(targetName,'S161:STATUS',await rpc(targetName,'/apply161',{page}));}
   catch(e){try{const after=verifySigned(targetName,'S161:STATUS',await rpc(targetName,'/status161'));if(after.count>before){stat=after;}else throw e;}catch{throw e;}}
   if(stat.count<=before||stat.count>target.count)throw Error('S161_NO_FORWARD_PROGRESS');onPage(stat.count,Buffer.byteLength(JSON.stringify(page)));
  }
  if(stat.root!==target.root)throw Error('S161_FINAL_ROOT');return verifySigned(targetName,'S161:FINISH',await rpc(targetName,'/finish161'));
 }
 return{rpc,sync};
}
module.exports={make};
```

## gate161.js

```javascript
#!/usr/bin/env node
'use strict';
const fs=require('node:fs'),path=require('node:path'),os=require('node:os'),crypto=require('node:crypto'),cp=require('node:child_process'),assert=require('node:assert/strict'),{performance}=require('node:perf_hooks');
const {Store}=require('./baseline160/indexed160');
const P=require('./baseline160/baseline159/baseline158/baseline157/baseline156/baseline155/baseline154/baseline153/baseline152/baseline151/baseline150/baseline149/baseline148/baseline147/baseline146/protocol146');
const M=require('./baseline160/baseline159/baseline158/baseline157/baseline156/baseline155/baseline154/baseline153/baseline152/baseline151/merkle151');
const V=require('./proof161'),C=require('./catchup161');
const tmp=fs.mkdtempSync(path.join(os.tmpdir(),'oasis-sheet161-'));const f=(...a)=>path.join(tmp,...a);let n=0;const ok=(s,fn)=>{fn();console.log('PASS',++n,s);};const step=async(s,fn)=>{await fn();console.log('PASS',++n,s);};const bad=async(s,fn,re)=>step(s,()=>assert.rejects(fn,re));const openssl=(...args)=>cp.execFileSync('openssl',args,{cwd:tmp,stdio:'pipe'});
const children=[];
function pem(id){const pair=crypto.generateKeyPairSync('ed25519'),priv=f(id+'.priv.pem'),pub=f(id+'.pub.pem');fs.writeFileSync(priv,pair.privateKey.export({format:'pem',type:'pkcs8'}));fs.writeFileSync(pub,pair.publicKey.export({format:'pem',type:'spki'}));return{privateKey:pair.privateKey,publicKey:pair.publicKey,priv,pub};}
function cert(id){openssl('req','-new','-newkey','rsa:2048','-nodes','-keyout',id+'.key','-out',id+'.csr','-subj','/CN=localhost');fs.writeFileSync(f(id+'.ext'),'subjectAltName=DNS:localhost,IP:127.0.0.1\nkeyUsage=digitalSignature,keyEncipherment\nextendedKeyUsage=clientAuth,serverAuth\n');openssl('x509','-req','-in',id+'.csr','-CA','ca.crt','-CAkey','ca.key','-CAcreateserial','-out',id+'.crt','-days','2','-sha256','-extfile',id+'.ext');return{key:f(id+'.key'),cert:f(id+'.crt'),ca:f('ca.crt'),certPin:new crypto.X509Certificate(fs.readFileSync(f(id+'.crt'))).fingerprint256.replaceAll(':','').toLowerCase()};}
async function spawn(cfg,name){const config=f('cfg-'+name+'.json');P.atomic(config,cfg);let err='';const proc=cp.fork(path.join(__dirname,'node161.js'),[],{env:{...process.env,S161_CONFIG:config},stdio:['ignore','pipe','pipe','ipc']});proc.stderr.on('data',b=>err+=b);const port=await new Promise((res,rej)=>{const timer=setTimeout(()=>rej(Error('START_TIMEOUT '+name+' '+err)),15000);proc.once('message',x=>{clearTimeout(timer);res(x.port);});proc.once('exit',code=>{clearTimeout(timer);rej(Error('START_EXIT '+code+' '+err));});});const item={proc,port,name};children.push(item);return item;}
async function stop(x){if(!x||x.proc.exitCode!==null||x.proc.signalCode!==null)return;await new Promise(resolve=>{const t=setTimeout(()=>{x.proc.kill('SIGKILL');resolve();},1500);x.proc.once('exit',()=>{clearTimeout(t);resolve();});try{x.proc.send('stop',e=>{if(e){x.proc.kill('SIGKILL');clearTimeout(t);resolve();}});}catch{x.proc.kill('SIGKILL');clearTimeout(t);resolve();}});}
(async()=>{try{
 openssl('req','-x509','-new','-newkey','rsa:2048','-nodes','-keyout','ca.key','-out','ca.crt','-days','2','-subj','/CN=OASIS-S161-CA');
 const ids=Object.fromEntries(['client','red','green','blue','rogue'].map(id=>[id,cert(id)]));const keys=Object.fromEntries(['red','green','blue'].map(id=>[id,pem(id)])),publicKeys=Object.fromEntries(Object.entries(keys).map(([id,k])=>[id,k.publicKey]));const anchorKeys=pem('anchor');const resourceId='S161-RESOURCE';
 const stores={};for(const id of ['red','green','blue']){stores[id]=new Store(f(id,'store'),resourceId);stores[id].init();}
 const seed=Number(process.env.S161_SEED||640),prefix=Number(process.env.S161_PREFIX||32);
 let start=performance.now();for(let i=0;i<seed;i++){const pay='datum-'+String(i).padStart(6,'0');stores.red.append(pay,'tx-'+i);stores.green.append(pay,'tx-'+i);if(i<prefix)stores.blue.append(pay,'tx-'+i);}const seedMs=performance.now()-start;
 const hr=stores.red.read(),hg=stores.green.read(),hb=stores.blue.read();const tgt={resourceId,count:hr.count,root:hr.root,lastRecordHash:hr.lastRecordHash};const anchor=V.signAnchor(V.anchorBody(resourceId,hr,1),anchorKeys.privateKey);
 ok('both mTLS sources have identical signed Merkle head',()=>assert.equal(hr.root,hg.root));
 ok('recovery target intentionally behind the quorum',()=>assert.equal(hb.count,prefix));
 ok('physical 256-record segment rollover exercised',()=>assert(hr.count>512&&hr.segments.length>=3));
 ok('externally signed floor checkpoint authentic',()=>assert.equal(V.checkAnchor(anchor,anchorKeys.publicKey).count,seed));
 ok('forged floor checkpoint denied',()=>assert.throws(()=>V.checkAnchor({...anchor,signature:'wrong'},anchorKeys.publicKey),/S161_ANCHOR_SIGNATURE/));
 const cfg={};for(const id of ['red','green','blue'])cfg[id]={nodeId:id,resourceId,...ids[id],dir:stores[id].dir,signKey:keys[id].priv,anchorPublicKey:anchorKeys.pub,peerPublicKeys:Object.fromEntries(Object.entries(keys).map(([k,v])=>[k,v.pub])),clientPin:ids.client.certPin,session:f(id,'session.json'),externalPin:f(id,'external-pin.json'),quarantine:f(id,'quarantine.txt'),...(id==='blue'?{crashOnce:f('blue-crash-once')}:{})};
 const nodes={};for(const id of ['red','green','blue'])nodes[id]=await spawn(cfg[id],id);
 const endpoints=()=>Object.fromEntries(Object.entries(nodes).map(([id,node])=>[id,{port:node.port,serverPin:ids[id].certPin}]));
 const api=()=>C.make({identity:ids.client,nodes:endpoints(),keys:publicKeys,anchor,anchorKey:anchorKeys.publicKey});const rpc=(id,p,b)=>api().rpc(id,p,b);
 await step('three pinned mTLS indexed-proof endpoints started',async()=>assert.equal((await rpc('red','/status161')).body.count,seed));
 const nonce=crypto.randomBytes(20).toString('hex'),heads=await Promise.all(['red','green'].map(x=>rpc(x,'/head161',{nonce})));
 ok('majority heads certify anchor root',()=>assert.equal(V.certified(tgt,heads,nonce,publicKeys),true));
 ok('duplicate signer cannot create majority',()=>assert.throws(()=>V.certified(tgt,[heads[0],heads[0]],nonce,publicKeys),/S161_CERT_SIGNATURE/));
 ok('one signer is not a majority',()=>assert.throws(()=>V.certified(tgt,heads.slice(0,1),nonce,publicKeys),/S161_CERT_QUORUM/));
 await bad('TLS unpinned client rejected',()=>P.rpc({...ids.rogue,...endpoints().red},'/head161',{nonce}),/TLS_PEER_NOT_PINNED/);
 const pg=(await rpc('red','/page161',{nonce,target:tgt,offset:prefix,limit:6}));
 ok('network Merkle page has bounded six records',()=>assert.equal(pg.body.records.length,6));
 await step('proof request touches no historical hash replay',async()=>assert.equal((await rpc('red','/status161')).body.recordHashesReplayed,0));
 const bstate=stores.blue.read();
 ok('network inclusion and extension verify against live indexed source',()=>assert.equal(V.verifyPage(pg,{nonce,target:tgt,keys:publicKeys,allowed:['red','green'],local:{count:bstate.count,frontier:bstate.frontier,root:bstate.root},lastRecordHash:bstate.lastRecordHash}).length,6));
 ok('tampered leaf rejected',()=>{const b=structuredClone(pg);b.body.records[0].record.payload='forged';b.signature=P.sign(keys.red.privateKey,'S161:PAGE',b.body);assert.throws(()=>V.verifyPage(b,{nonce,target:tgt,keys:publicKeys,allowed:['red','green'],local:{count:bstate.count,frontier:bstate.frontier,root:bstate.root},lastRecordHash:bstate.lastRecordHash}),/S161_RECORD_CHAIN/);});
 ok('tampered inclusion proof rejected',()=>{const b=structuredClone(pg);b.body.records[0].inclusion.siblings[0]='f'.repeat(64);b.signature=P.sign(keys.red.privateKey,'S161:PAGE',b.body);assert.throws(()=>V.verifyPage(b,{nonce,target:tgt,keys:publicKeys,allowed:['red','green'],local:{count:bstate.count,frontier:bstate.frontier,root:bstate.root},lastRecordHash:bstate.lastRecordHash}),/INCLUSION_PEAK_MISMATCH|INCLUSION_ROOT_MISMATCH/);});
 ok('tampered extension rejected',()=>{const b=structuredClone(pg);b.body.extension.blocks[0].root='f'.repeat(64);b.signature=P.sign(keys.red.privateKey,'S161:PAGE',b.body);assert.throws(()=>V.verifyPage(b,{nonce,target:tgt,keys:publicKeys,allowed:['red','green'],local:{count:bstate.count,frontier:bstate.frontier,root:bstate.root},lastRecordHash:bstate.lastRecordHash}),/EXTENSION_ROOT_MISMATCH/);});
 await bad('one signed head cannot open recovery',()=>rpc('blue','/begin161',{nonce,target:tgt,anchor,heads:[heads[0]]}),/S161_CERT_QUORUM/);
 await bad('forged external floor denies recovery',()=>rpc('blue','/begin161',{nonce,target:tgt,anchor:{...anchor,signature:'invalid'},heads}),/S161_ANCHOR_SIGNATURE/);
 await step('begin persists independent rollback pin before recovery',async()=>assert.equal((await rpc('blue','/begin161',{nonce,target:tgt,anchor,heads})).body.active,true));
 ok('rollback pin retained out of the journal',()=>assert.equal(P.load(cfg.blue.externalPin).body.root,tgt.root));
 await bad('out-of-order page rejected',async()=>rpc('blue','/apply161',{page:await rpc('green','/page161',{nonce,target:tgt,offset:prefix+8,limit:4})}),/S161_PAGE_CONTEXT/);
 await bad('forged signed page rejected',()=>rpc('blue','/apply161',{page:{...pg,signature:'bad'}}),/S161_PAGE_SIGNATURE/);
 await bad('real target process killed after fsync before ACK',()=>rpc('blue','/apply161',{page:pg}),/socket hang up|ECONNRESET|EPIPE/);
 ok('single record survived process kill',()=>assert.equal(stores.blue.read().count,prefix+1));
 nodes.blue=await spawn(cfg.blue,'blue-restart');
 await step('durable session resumes with the original signed nonce',async()=>assert.equal((await rpc('blue','/status161')).body.nonce,nonce));
 const pages=[],pageBytes=[];start=performance.now();await step('network recovery completes using indexed proofs',async()=>{const r=await api().sync('blue',{limit:8,onPage:(n,bytes)=>{pages.push(n);pageBytes.push(bytes)}});assert.equal(r.count,seed);});const recoveryMs=performance.now()-start;
 ok('target and certified source roots equal',()=>assert.equal(stores.blue.read().root,hr.root));
 ok('restart consumed exactly the missing records without duplication',()=>assert.equal(stores.blue.read().count,seed));
 ok('target no longer has an active recovery session',()=>assert.equal(fs.existsSync(cfg.blue.session),false));
 await step('network recovery never replayed historical hashes',async()=>assert.equal((await rpc('blue','/status161')).body.recordHashesReplayed,0));
 ok('more than two network pages transferred',()=>assert(pages.length>2));
 await bad('post-finalization stale page denied',()=>rpc('blue','/apply161',{page:pg}),/S161_NO_SESSION/);
 const olderHead={...tgt,count:tgt.count-1};const older=V.signAnchor({...V.anchorBody(resourceId,hr,1),count:hr.count-1},anchorKeys.privateKey);
 await bad('older signed rollback floor refused',()=>rpc('blue','/begin161',{nonce:crypto.randomBytes(20).toString('hex'),target:olderHead,anchor:older,heads}),/S161_CERT_SIGNATURE|S161_FLOOR_TARGET/);
 // New slot moves certified head forward while retaining the old signed high-water pin.
 const nextPay='datum-'+seed;stores.red.append(nextPay,'tx-'+seed);stores.green.append(nextPay,'tx-'+seed);const h2=stores.red.read();
 const anchor2=V.signAnchor(V.anchorBody(resourceId,h2,2),anchorKeys.privateKey);
 await step('next independently pinned epoch is recovered',async()=>{const a2=C.make({identity:ids.client,nodes:endpoints(),keys:publicKeys,anchor:anchor2,anchorKey:anchorKeys.publicKey});await a2.sync('blue',{limit:1});assert.equal(stores.blue.read().root,h2.root);});
 ok('pin advances monotonically to epoch two',()=>assert.equal(P.load(cfg.blue.externalPin).body.sequence,2));
 const h3=stores.red.read(),n3=crypto.randomBytes(20).toString('hex'),sameHeads=await Promise.all(['red','green'].map(id=>rpc(id,'/head161',{nonce:n3})));
 const signedOldSeq=V.signAnchor(V.anchorBody(resourceId,h3,1),anchorKeys.privateKey);
 await bad('valid but stale external anchor sequence rejected',()=>rpc('blue','/begin161',{nonce:n3,target:{resourceId,count:h3.count,root:h3.root,lastRecordHash:h3.lastRecordHash},anchor:signedOldSeq,heads:sameHeads}),/S161_ROLLBACK_FLOOR/);
 const finalStatus=(await rpc('blue','/status161')).body;const report={sheet:161,status:'PASS',newChecks:n,physicalHostCount:1,sourceNodes:2,targetNodes:1,initialRecords:seed,targetStart:prefix,caughtUpRecords:seed-prefix,sourceSegmentSize:256,networkPages:pages.length,networkPageBytes:pageBytes.reduce((a,b)=>a+b,0),meanPageBytes:+(pageBytes.reduce((a,b)=>a+b,0)/pageBytes.length).toFixed(1),maxPageBytes:Math.max(...pageBytes),receiverRssMiB:finalStatus.rssMiB,sourceSeedMs:+seedMs.toFixed(2),recoveryMs:+recoveryMs.toFixed(2),recoveryRecordsPerSecond:+((seed-prefix)/(recoveryMs/1000)).toFixed(2),meanNetworkPageMs:+(recoveryMs/pages.length).toFixed(2),currentRoot:h2.root,recordHashesReplayedOnOrdinaryPath:0,crashWindow:'after fsync, before response',note:'Single physical host. TLS handshakes per RPC. Benchmark includes per-record fsync, page proofs and network roundtrips.'};
 fs.writeFileSync(path.join(__dirname,'benchmark161.json'),JSON.stringify(report,null,2)+'\n');
 fs.writeFileSync(path.join(__dirname,'new-test-report.json'),JSON.stringify({sheet:161,passed:n,failed:0,status:'PASS'},null,2)+'\n');
 console.log('SHEET161 GATE '+n+'/'+n+' PASS');console.log('SHEET161 BENCHMARK '+JSON.stringify(report));
 }catch(e){console.error('SHEET161 GATE FAIL',e.stack||e);process.exitCode=1;}finally{await Promise.allSettled(children.map(stop));if(!process.env.S161_KEEP_FIXTURE)fs.rmSync(tmp,{recursive:true,force:true});}})();
```

## run-new.sh

```bash
#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
node gate161.js
```

## browser-check.py

```python
from playwright.sync_api import sync_playwright
from pathlib import Path
page_html=Path(__file__).with_name('index.html').read_text()
with sync_playwright() as pw:
    browser=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
    page=browser.new_page(viewport={'width':1440,'height':1000})
    page.set_content(page_html,wait_until='domcontentloaded')
    names=['certified','inclusion','extension','crash','rollback','forged','order','tls']
    for name in names:
        page.locator(f'button[data-id="{name}"]').click()
        assert page.locator('button.active').get_attribute('data-id')==name
        assert page.locator('#state b').count()==1
        print('PASS browser scenario',name)
    with page.expect_download() as event:page.locator('#export').click()
    download=event.value
    assert download.suggested_filename=='SHEET161-benchmark.json'
    print('PASS browser benchmark JSON export')
    page.screenshot(path=str(Path(__file__).with_name('preview.png')),full_page=True)
    print('PASS browser screenshot')
    browser.close()
```

## make-release161.py

```python
#!/usr/bin/env python3
"""Fail-closed SHA256-checked reproducible ZIP packager for SHEET 161."""
from pathlib import Path
import zipfile,hashlib,json,os
ROOT=Path(__file__).resolve().parent;PARENT=ROOT.parent/'sheet160'
OUT=ROOT.parent/'SHEET161-indexed-witness-recovery-benchmark.zip'
HFILE=ROOT.parent/(OUT.name+'.sha256.txt')

def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  while b:=f.read(1024*1024):h.update(b)
 return h.hexdigest()

before={p.relative_to(PARENT):sha(p) for p in PARENT.rglob('*') if p.is_file()}
after={p.relative_to(ROOT/'baseline160'):sha(p) for p in (ROOT/'baseline160').rglob('*') if p.is_file()}
assert before==after, f'SHEET160 frozen lineage mismatch: {len(before)} vs {len(after)} files'
checks=json.loads((ROOT/'new-test-report.json').read_text())
assert checks.get('passed')==36 and checks.get('failed')==0
assert 'SHEET160 GATE 71/71 PASS' in (ROOT/'inherited-gate160.log').read_text()
assert 'SHEET160 BRIDGE 19/19 PASS' in (ROOT/'inherited-bridge160.log').read_text()
assert 'PASS browser screenshot' in (ROOT/'browser-test.log').read_text()
report={
 'sheet':161,'status':'0e / PASS','newChecks':36,'inheritedGateChecks':71,
 'inheritedMigrationChecks':19,'browserChecks':10,
 'baselineSheet':160,'baselineFilesByteIdentical':len(before),
 'combinedHistoricalRunner':'not rerun',
 's160_full_benchmark_rerun':'timed out near 6144/12288 writes',
 'benchmarkFiles':['benchmark161-small.json','benchmark161.json','benchmark161-large.json'],
 'networkHostsPhysical':1,'crashWindow':'post fsync pre-ack',
 'sourcePreserved':True,'limitations':[
  '2 source witness services and a target witness run on one physical host',
  'external signed pin persists on the same test host',
  'per-row fsync and per-request mTLS handshake',
  'full historical regression chain not rerun'
 ]}
(ROOT/'release-receipt.json').write_text(json.dumps(report,indent=2)+'\n')
all_files=sorted((p for p in ROOT.rglob('*') if p.is_file() and p != ROOT/'SHA256SUMS' and p != ROOT/'release-build.log'),key=lambda p:p.relative_to(ROOT).as_posix())
lines=[f'{sha(p)}  {p.relative_to(ROOT).as_posix()}\n' for p in all_files]
(ROOT/'SHA256SUMS').write_text(''.join(lines))
all_files.append(ROOT/'SHA256SUMS')
with zipfile.ZipFile(OUT,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=7,allowZip64=True) as z:
 for p in sorted(all_files,key=lambda x:x.relative_to(ROOT).as_posix()):
  info=zipfile.ZipInfo('sheet161/'+p.relative_to(ROOT).as_posix(),date_time=(2026,10,9,12,0,0))
  info.compress_type=zipfile.ZIP_DEFLATED
  info.external_attr=(0o100644<<16)
  z.writestr(info,p.read_bytes(),compress_type=zipfile.ZIP_DEFLATED,compresslevel=7)
with zipfile.ZipFile(OUT) as z:
 assert z.testzip() is None
 names=set(z.namelist())
 for rel,digest in before.items():
  name='sheet161/baseline160/'+rel.as_posix()
  assert name in names, 'inherited file excluded: '+name
  assert hashlib.sha256(z.read(name)).hexdigest()==digest, 'inherited file differs: '+name
 for p in all_files:
  name='sheet161/'+p.relative_to(ROOT).as_posix()
  assert name in names and hashlib.sha256(z.read(name)).hexdigest()==sha(p),'release tree mismatch: '+name
assert len(before)==677, f'unexpected inherited file count {len(before)}'
HFILE.write_text(f'{sha(OUT)}  {OUT.name}\n')
print(json.dumps({'archive':str(OUT),'bytes':OUT.stat().st_size,'sha256':sha(OUT), 'inheritedFiles':len(before),'newTests':36,'verifiedFiles':len(all_files),'zipEntries':len(names)},indent=2))
```

## KERNEL-ASCII.txt

```text
OASIS / ROOT0 — SHEET 161 — LIVE INDEXED WITNESS RECOVERY
===========================================================

   CLIENT / ORCHESTRATOR (mTLS client cert + server pins)
        |
   01. READ target witness signed status
   02. IF recovering, resume original nonce and target
   03. ELSE generate cryptographic 160-bit nonce
        |
        +------------------+------------------+
        |                  |                  |
   INDEXED RED        INDEXED GREEN      LAGGING BLUE
   S160 PHYSICAL      S160 PHYSICAL      S160 PHYSICAL
   JOURNAL             JOURNAL            JOURNAL
   256 RECORDS/SEG     256 RECORDS/SEG    256 RECORDS/SEG
        |                  |                  |
   04. SIGN HEAD       05. SIGN HEAD     06. REPORT CURSOR
        |                  |                  |
        +-----------+------+                  |
                    |                         |
   07. Verify two DISTINCT pinned Ed25519 HEAD signatures
   08. Match count, root, lastRecordHash, nonce, resource ID
   09. Check independently signed external checkpoint anchor
   10. Reject floor rollback (sequence and count monotonic)
   11. Persist external floor atomically OUTSIDE journal
   12. Persist session nonce + target + quorum proof
                    |                         |
                    +-------------------------+
                                              |
                 FOR EACH BOUNDED PAGE (1..8 RECORDS)
                                              |
   13. Source fetches indexed subtree hashes from S160 nodes
   14. Source builds S151 inclusion proof for each actual record
   15. Source creates bounded S151 Merkle extension witness
   16. Source signs nonce-bound page over Ed25519
   17. Transmit via pinned mTLS to recovering witness
   18. Verify signer belongs to certified source quorum
   19. Verify page matches cursor and immutable target
   20. Verify EVERY record's P.sha physical record hash
   21. Verify chain continuity (prev and sequence)
   22. Verify EVERY inclusion against certified final root
   23. Verify Merkle extension from target's durable frontier
   24. Verify extension equals hashes of actual page leaves
   25. Check lastRecordHash of page
   26. Reject gap, duplicate, stale signer, invalid signature
   27. Acquire exclusive S160 physical-store writer lock
   28. Append rows one at a time using fsync/rename/dir fsync
   29. Update 256-record segment index and upper Merkle nodes
   30. Persist head/frontier and rollback-aware cursor
   31. Acknowledge signed current count/root/cursor
   32. Alternate page sources, repeat until certified target
                                              |
   33. Verify final count/root/lastRecordHash EXACTLY match
   34. Complete recovery, remove active session
   35. Retain external floor pin in separate persistent file
   36. Next physical slot may be certified and appended
                                              |
                      CRASH / ADVERSARIAL BRANCHES
                                              |
   A. POST-FSYNC PRE-ACK CRASH --> process killed (exit 81)
        -> restart -> retain original session + pinned nonce
        -> source requests only remaining missing suffix
        -> no duplicate physical append
   B. REORDERED PAGE ------------> REJECT (cursor mismatch)
   C. FORGED SOURCE SIGNATURE ---> REJECT
   D. TAMPERED LEAF / SIBLING --> REJECT
   E. FORGED MERKLE EXTENSION --> REJECT
   F. ONE HEAD / WITNESS LOSS --> FAIL CLOSED
   G. RESTORED OLDER ANCHOR ----> REJECT, regardless valid signature
   H. UNPINNED TLS CLIENT ------> REJECT
   I. COMPLETE SESSION REPLAY --> REJECT

NETWORK BENCHMARKS — SINGLE HOST, SYNTHETIC RECORDS
---------------------------------------------------
Workload             Small       Medium      Large
Source records       640         2,048       4,096
Target prefix        32          1,024       3,072
Recovered records    608         1,024       1,024
Pages transferred    76          128         128
Recovery seconds     4.683       9.386       8.307
Recovered rows/s     129.84      109.10      123.28
Ordinary replay      0           0           0
Medium transfer      1,433,259 JSON page bytes
Medium target RSS    63.22 MiB

EVIDENCE BOUNDARIES
-------------------
- Three processes on one physical host; independently hosted consensus NOT tested.
- S160 index proof reads avoid full-history scans but can read the indexed segment files.
- Full verification (verifyFull) intentionally DOES replay rows and is not a hot-path benchmark.
- Missing suffix transfer and durable row-by-row fsync still cost O(missing_records).
- Single external anchor signing key remains a trust dependency.
- SHEET160 71/71 gate and 19/19 migration suite passed independently.
- SHEET160 12,288-record benchmark rerun timed out around 6,144 records.
- Full older 159+ chain NOT rerun; no inherited combined-pass claim.
```
