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
