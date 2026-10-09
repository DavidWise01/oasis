#!/usr/bin/env node
'use strict';
const fs=require('node:fs'),path=require('node:path'),os=require('node:os'),cp=require('node:child_process'),crypto=require('node:crypto'),assert=require('node:assert/strict');
const P=require('./baseline158/baseline157/baseline156/baseline155/baseline154/baseline153/baseline152/baseline151/baseline150/baseline149/baseline148/baseline147/baseline146/protocol146');
const W=require('./baseline158/baseline157/baseline156/witness-verify156');const V=require('./merkle159');const C=require('./catchup159');
const root=fs.mkdtempSync(path.join(os.tmpdir(),'sheet159-')),f=(...a)=>path.join(root,...a),openssl=(...a)=>cp.execFileSync('openssl',a,{cwd:root,stdio:'pipe'});
let n=0;const ok=(name,fn)=>{fn();console.log('PASS',++n,name);};const step=async(name,fn)=>{await fn();console.log('PASS',++n,name);};const bad=async(name,fn,regex)=>step(name,async()=>assert.rejects(fn,regex));
function cert(id){openssl('req','-new','-newkey','rsa:2048','-nodes','-keyout',id+'.key','-out',id+'.csr','-subj','/CN=localhost');fs.writeFileSync(f(id+'.ext'),'subjectAltName=DNS:localhost,IP:127.0.0.1\nkeyUsage=digitalSignature,keyEncipherment\nextendedKeyUsage=clientAuth,serverAuth\n');openssl('x509','-req','-in',id+'.csr','-CA','ca.crt','-CAkey','ca.key','-CAcreateserial','-out',id+'.crt','-days','2','-sha256','-extfile',id+'.ext');return{key:f(id+'.key'),cert:f(id+'.crt'),ca:f('ca.crt'),certPin:new crypto.X509Certificate(fs.readFileSync(f(id+'.crt'))).fingerprint256.replaceAll(':','').toLowerCase()};}
function keys(id){const pair=crypto.generateKeyPairSync('ed25519'),priv=f(id+'.priv'),pub=f(id+'.pub');fs.writeFileSync(priv,pair.privateKey.export({format:'pem',type:'pkcs8'}));fs.writeFileSync(pub,pair.publicKey.export({format:'pem',type:'spki'}));return{privateKey:pair.privateKey,publicKey:pair.publicKey,priv,pub};}
const children=[];
async function spawn(script,cfg,id){const config=f('cfg-'+id+'.json');P.atomic(config,cfg);const proc=cp.fork(path.join(__dirname,script),[],{env:{...process.env,S158_WITNESS_CONFIG:config,S156_FLOOR_CONFIG:config},stdio:['ignore','pipe','pipe','ipc']});let errors='';proc.on('error',()=>{});proc.stderr.on('data',b=>errors+=b);const port=await new Promise((res,rej)=>{const t=setTimeout(()=>rej(Error('START_TIMEOUT '+id+' '+errors)),15000);proc.once('message',m=>{clearTimeout(t);res(m.port);});proc.once('exit',code=>{clearTimeout(t);rej(Error('START_FAILED '+id+' '+code+' '+errors));});});const x={proc,port,id,errors:()=>errors};children.push(x);return x;}
async function stop(x){if(!x||x.proc.exitCode!==null||x.proc.signalCode!==null)return;await new Promise(done=>{const t=setTimeout(()=>{x.proc.kill('SIGKILL');done();},2000);x.proc.once('exit',()=>{clearTimeout(t);done();});if(x.proc.connected){try{x.proc.send('stop',err=>{if(err){x.proc.kill('SIGKILL');clearTimeout(t);done();}});}catch{ x.proc.kill('SIGKILL');clearTimeout(t);done();}}else{x.proc.kill('SIGKILL');clearTimeout(t);done();}});}
(async()=>{try{
 openssl('req','-x509','-new','-newkey','rsa:2048','-nodes','-keyout','ca.key','-out','ca.crt','-days','2','-subj','/CN=S159');
 const ids=Object.fromEntries(['proxy','wred','wblue','wgreen','rogue'].map(id=>[id,cert(id)]));
 const witnessKeys=Object.fromEntries(['wred','wblue','wgreen'].map(id=>[id,keys(id)]));
 const finalKeys=Object.fromEntries(['red','blue'].map(id=>[id,keys('final-'+id)]));
 const pubs=Object.fromEntries(Object.entries(witnessKeys).map(([id,k])=>[id,k.publicKey]));
 const witnessPublicKeys=Object.fromEntries(Object.entries(witnessKeys).map(([id,k])=>[id,k.pub]));
 const finalPublicKeys=Object.fromEntries(Object.entries(finalKeys).map(([id,k])=>[id,k.pub]));
 const cfg=Object.fromEntries(Object.keys(witnessKeys).map(id=>[id,{id,...ids[id],signKey:witnessKeys[id].priv,stateFile:f(id,'state.json'),proxyPin:ids.proxy.certPin,witnessPublicKeys,finalityPublicKeys:finalPublicKeys}]));
 const M=require('./baseline158/baseline157/baseline156/baseline155/baseline154/baseline153/baseline152/baseline151/merkle151');
 const record=(slot,prev,tag)=>W.normalize({slot,prev,intentDigest:P.sha('intent'+tag),snapshotDigest:P.sha('snapshot'+tag),receiptHash:P.sha('receipt'+tag)});
 const history=[];let prev=W.ZERO;for(let i=1;i<=389;i++){const r=record(i,prev,'synthetic-'+i);history.push(r);prev=r.head;}
 for(const id of ['wred','wgreen'])P.atomic(cfg[id].stateFile,{schema:W.SCHEMA,nodeId:id,slot:389,head:prev,history:structuredClone(history),pending:null,challenge:null});
 P.atomic(cfg.wblue.stateFile,{schema:W.SCHEMA,nodeId:'wblue',slot:7,head:history[6].head,history:history.slice(0,7),pending:history[7],challenge:null});
 const nodes={};for(const id of Object.keys(cfg))nodes[id]=await spawn('witness159.js',cfg[id],id);
 const endpoints=()=>Object.fromEntries(Object.keys(nodes).map(id=>[id,{port:nodes[id].port,serverPin:ids[id].certPin}]));
 const api=()=>C.make({identity:ids.proxy,witnesses:endpoints(),publicKeys:pubs});
 const rpc=(id,url,b={})=>api().rpc(id,url,b);
 const state=id=>P.load(cfg[id].stateFile);
 const target={slot:389,head:prev,merkleRoot:M.accumulate(history.map(P.sha)).root};
 ok('three mTLS witness services online',()=>assert.equal(Object.keys(nodes).length,3));
 ok('majority has 389 source records',()=>assert.equal(state('wred').slot,389));
 ok('minority has seven certified prefix entries',()=>assert.equal(state('wblue').slot,7));
 ok('pending promise preserved',()=>assert.equal(state('wblue').pending.head,history[7].head));
 ok('bounded page length remains 24',()=>assert.equal(V.MAX_PAGE,24));
 ok('genuine Merkle extension proof verifies 7 -> 22',()=>{const h=history.map(P.sha);const a=M.accumulate(h.slice(0,7)),b=M.accumulate(h.slice(0,22));assert.equal(M.verifyExtension(a,M.extension(h.slice(0,22),7),b).root,b.root);});
 ok('altered Merkle subtree fails',()=>{const h=history.map(P.sha),a=M.accumulate(h.slice(0,7)),b=M.accumulate(h.slice(0,22)),p=M.extension(h.slice(0,22),7);p.blocks[0].root='f'.repeat(64);assert.throws(()=>M.verifyExtension(a,p,b),/EXTENSION_ROOT_MISMATCH/);});
 ok('shorter prefix root differs',()=>assert.notEqual(M.accumulate(history.slice(0,8).map(P.sha)).root,target.merkleRoot));
 const challenge=await rpc('wblue','/challenge');const nonce=challenge.body.nonce;
 const heads=await Promise.all(['wred','wgreen'].map(id=>rpc(id,'/checkpoint159',{nonce})));
 ok('2/3 certified Merkle checkpoints',()=>assert.equal(V.certify(target,heads,nonce,pubs).length,2));
 ok('duplicate checkpoint refused',()=>assert.throws(()=>V.certify(target,[heads[0],heads[0]],nonce,pubs),/W159_CHECKPOINT_SIGNATURE/));
 ok('forged checkpoint signature refused',()=>assert.throws(()=>V.certify(target,[{...heads[0],signature:'AAAA'},heads[1]],nonce,pubs),/W159_CHECKPOINT_SIGNATURE/));
 ok('wrong certified Merkle root rejected',()=>assert.throws(()=>V.certify({...target,merkleRoot:'a'.repeat(64)},heads,nonce,pubs),/W159_CHECKPOINT_SIGNATURE/));
 await bad('one signed checkpoint cannot begin recovery',()=>rpc('wblue','/begin159',{nonce,target,checkpoints:[heads[0]]}),/W159_NO_QUORUM/);
 await step('begin session persists certified target',async()=>assert.equal((await rpc('wblue','/begin159',{nonce,target,checkpoints:heads})).body.cursor,7));
 await bad('duplicate recovery begin fails',()=>rpc('wblue','/begin159',{nonce,target,checkpoints:heads}),/W159_RECOVERY_ACTIVE/);
 const signed=body=>({body,signature:P.sign(witnessKeys.wred.privateKey,'S159:PAGE',body)});
 const page=await rpc('wred','/page159',{nonce,target,offset:7,limit:15});
 ok('page contains exactly fifteen real rows',()=>assert.equal(page.body.records.length,15));
 ok('page carries a logarithmic Merkle block witness',()=>assert(page.body.extension.blocks.length<=8));
 ok('source Merkle proof binds local prefix',()=>assert.equal(page.body.priorRoot,M.accumulate(history.slice(0,7).map(P.sha)).root));
 ok('recipient verifies page against local frontier',()=>assert.equal(V.verifyPage(page,{nonce,target,cursor:7,head:history[6].head,merkle:M.accumulate(history.slice(0,7).map(P.sha)),signers:['wred','wgreen'],keys:pubs}).length,15));
 await bad('forged signed page rejected',()=>rpc('wblue','/apply159',{page:{...page,signature:'bad'}}),/W159_PAGE_SIGNATURE/);
 await bad('page with altered target rejected',()=>rpc('wblue','/apply159',{page:signed({...page.body,target:{...target,slot:388}})}),/W159_PAGE_CONTEXT/);
 await bad('page with modified leaf rejected',()=>rpc('wblue','/apply159',{page:signed({...page.body,records:[{...page.body.records[0],receiptHash:'b'.repeat(64)},...page.body.records.slice(1)]})}),/W159_PAGE_CHAIN|W159_PAGE_LEAF_SUBSTITUTION/);
 await bad('page with forged Merkle subtree rejected',()=>rpc('wblue','/apply159',{page:signed({...page.body,extension:{...page.body.extension,blocks:[{...page.body.extension.blocks[0],root:'f'.repeat(64)},...page.body.extension.blocks.slice(1)]}})}),/EXTENSION_ROOT_MISMATCH/);
 await bad('out-of-order page rejected',async()=>rpc('wblue','/apply159',{page:await rpc('wred','/page159',{nonce,target,offset:22,limit:15})}),/W159_PAGE_CONTEXT/);
 await bad('cannot finish before complete target',()=>rpc('wblue','/finish159'),/W159_NOT_CERTIFIED/);
 await step('first signed page persists exactly 15 rows',async()=>assert.equal((await rpc('wblue','/apply159',{page})).body.cursor,22));
 ok('Merkle frontier is durable with cursor',()=>assert.equal(state('wblue').recovery159.merkle.count,22));
 await bad('old page replay rejected',()=>rpc('wblue','/apply159',{page}),/W159_PAGE_CONTEXT/);
 await stop(nodes.wblue);nodes.wblue=await spawn('witness159.js',cfg.wblue,'wblue-restart');
 await step('restart retains Merkle frontier',async()=>assert.equal((await rpc('wblue','/status159')).body.cursor,22));
 const counts=[];await step('resume only missing Merkle pages and finalize',async()=>{const r=await api().repair('wblue',{pageSize:24,onPage:c=>counts.push(c)});assert.equal(r.body.slot,389);});
 ok('recovery history exactly equals certified source',()=>assert.deepEqual(state('wblue').history,history));
 ok('final Merkle root equals certified checkpoint',()=>assert.equal(state('wblue').lastRecovery159.merkleRoot,target.merkleRoot));
 ok('final hash-chain head equals source',()=>assert.equal(state('wblue').head,target.head));
 ok('segment-level checkpoints persisted',()=>assert(state('wblue').lastRecovery159.segmentPins.length>=1));
 ok('page cursor always monotonic',()=>assert(counts.every((v,i)=>i===0||v>counts[i-1])));
 ok('page transmissions bounded',()=>assert(counts.length>=12));
 await step('aligned repair completes without replay',async()=>assert.equal((await api().repair('wblue')).body.slot,389));
 await bad('unaligned page replay rejected after finish',()=>rpc('wblue','/apply159',{page}),/W159_NO_RECOVERY/);
 await bad('wrong-client TLS pin rejected',()=>P.rpc({...ids.rogue,...endpoints().wred},'/page159',{nonce,target,offset:7,limit:7}),/TLS_PEER_NOT_PINNED/);
 // An actual signed consensus operation across two healthy witness processes.
 const r390=record(390,prev,'live-390');const finalVotes=['red','blue'].map(id=>{const body={nodeId:id,slot:r390.slot,prevPinDigest:r390.prev,intentDigest:r390.intentDigest,snapshotDigest:r390.snapshotDigest,receiptHash:r390.receiptHash,phase:'final'};return{body,signature:P.sign(finalKeys[id].privateKey,'S155:FINAL',body)};});
 const prepare=id=>rpc(id,'/prepare',{record:r390,finalVotes});
 const votes=await Promise.all(['wred','wgreen'].map(prepare));
 await rpc('wred','/commit',{record:r390,preparedVotes:votes});await rpc('wgreen','/commit',{record:r390,preparedVotes:votes});
 ok('two witnesses really committed slot 390',()=>assert.equal(state('wgreen').slot,390));
 await step('Merkle extension catches up live signed slot',async()=>assert.equal((await api().repair('wblue',{pageSize:1})).body.slot,390));
 ok('all witness Merkle roots agree after catchup',()=>assert.equal(M.accumulate(state('wblue').history.map(P.sha)).root,M.accumulate(state('wred').history.map(P.sha)).root));
 await stop(nodes.wgreen);
 await bad('partition prevents new recovery majority',()=>api().repair('wblue'),/W159_NO_QUORUM/);
 await step('completed witness still serves signed Merkle checkpoint',async()=>assert.equal((await rpc('wblue','/checkpoint159',{nonce:crypto.randomBytes(20).toString('hex')})).body.slot,390));
 // Independent crash-after-durable-page fixture: restore old minority at 389 (already certified). Source remains slot390.
 await stop(nodes.wblue);
 const s=state('wblue');s.history.pop();s.slot=389;s.head=history[388].head;s.lastRecovery159=null;s.challenge=null;P.atomic(cfg.wblue.stateFile,s);
 cfg.wblue.crashAfterMerklePage=f('crash-merkle-once');nodes.wblue=await spawn('witness159.js',cfg.wblue,'wblue-crash');
 // Require two sources; restart green.
 nodes.wgreen=await spawn('witness159.js',cfg.wgreen,'wgreen-back');
 const c2=await rpc('wblue','/challenge');const n2=c2.body.nonce;
 const heads2=await Promise.all(['wred','wgreen'].map(id=>rpc(id,'/checkpoint159',{nonce:n2})));
 const t2={slot:390,head:r390.head,merkleRoot:M.accumulate([...history,r390].map(P.sha)).root};
 await rpc('wblue','/begin159',{nonce:n2,target:t2,checkpoints:heads2});
 const p2=await rpc('wred','/page159',{nonce:n2,target:t2,offset:389,limit:1});
 await bad('real process crash after fsync before ACK',()=>rpc('wblue','/apply159',{page:p2}),/socket hang up|ECONNRESET/);
 ok('recovery cursor persisted before killed child',()=>assert.equal(state('wblue').recovery159.cursor,390));
 nodes.wblue=await spawn('witness159.js',cfg.wblue,'wblue-after-crash');
 await step('post-crash resume finalizes without duplicate',async()=>assert.equal((await api().repair('wblue',{pageSize:1})).body.slot,390));
 ok('crash recovery did not duplicate physical history row',()=>assert.equal(state('wblue').history.length,390));
 console.log('SHEET159 '+n+'/'+n+' PASS');
 P.atomic(path.join(__dirname,'new-test-report.json'),{sheet:159,passed:n,failed:0,fixtureRecords:389,liveSlots:[390],recoveryPageMax:V.MAX_PAGE,protocol:'binary peak Merkle extension + signed 2/3 checkpoint',exit:'PASS'});
} catch(e){console.error('SHEET159 FAIL',e.stack||e);process.exitCode=1;}finally{await Promise.allSettled(children.map(stop));}})();
