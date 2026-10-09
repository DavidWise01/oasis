'use strict';
const fs=require('node:fs'),crypto=require('node:crypto');
const P=require('./baseline155/baseline154/baseline153/baseline152/baseline151/baseline150/baseline149/baseline148/baseline147/baseline146/protocol146');
const W=require('./witness-verify156');
const cfg=P.load(process.env.S156_FLOOR_CONFIG),signing=fs.readFileSync(cfg.signKey);
const pubs=Object.fromEntries(Object.entries(cfg.witnessPublicKeys).map(([k,p])=>[k,fs.readFileSync(p)]));
const finalPubs=Object.fromEntries(Object.entries(cfg.finalityPublicKeys).map(([k,p])=>[k,fs.readFileSync(p)]));
let busy=false;
const rpc=(id,url,b)=>{const x=cfg.witnessMapFile?P.load(cfg.witnessMapFile)[id]:cfg.witnesses[id];return P.rpc({port:x.port,key:cfg.key,cert:cfg.cert,ca:cfg.ca,serverPin:x.certPin},url,b);};
async function fan(url,b){return Promise.all(Object.keys(cfg.witnesses).map(async id=>{try{return{id,v:await rpc(id,url,b)};}catch(e){return{id,error:e.message};}}));}
function selected(rows,domain,r){const good=[];for(const row of rows){const v=row.v?.body;if(v?.nodeId!==row.id||!pubs[row.id]||!P.verify(pubs[row.id],domain,v,row.v.signature))continue;if(domain==='S156:PREPARE'&&(v.slot!==r.slot||v.head!==r.head||v.prev!==r.prev||v.recordDigest!==P.sha(r)))continue;if(domain==='S156:COMMIT'&&(v.slot!==r.slot||v.head!==r.head||v.recordDigest!==P.sha(r)))continue;good.push(row.v);}return good;}
async function read(b={}){const nonce=b.nonce||crypto.randomBytes(20).toString('hex');if(!/^[0-9a-f]{32,64}$/.test(nonce))throw Error('W156_NONCE_REQUIRED');
 const rows=await fan('/read',{nonce}), groups=new Map();for(const x of rows){const v=x.v?.body;if(!pubs[x.id]||v?.nodeId!==x.id||v.nonce!==nonce||!P.verify(pubs[x.id],'S156:HEAD',v,x.v.signature))continue;const key=`${v.slot}:${v.head}`;if(!groups.has(key))groups.set(key,[]);groups.get(key).push(x.v);}
 const majority=[...groups.values()].filter(g=>g.length>=2);if(majority.length!==1)throw Error('W156_NO_CURRENT_WITNESS_MAJORITY');const votes=majority[0],{slot,head}=votes[0].body;
 return{body:{slot,head},signature:P.sign(signing,'S155:FLOOR',{slot,head}),nonce,witnessHeads:votes};
}
async function pin(b){W.verifyFinalVotes(W.normalize(b.record),b.finalVotes,finalPubs);const r=W.normalize(b.record);
 const current=await read();if(current.body.slot===r.slot&&current.body.head===r.head)return current;
 if(current.body.slot!==r.slot-1||current.body.head!==r.prev)throw Error('W156_ROLLBACK_OR_SLOT_GAP');
 const votes=selected(await fan('/prepare',{record:r,finalVotes:b.finalVotes}),'S156:PREPARE',r);
 if(votes.length<2)throw Error('W156_PREPARE_QUORUM_UNAVAILABLE');
 const committed=selected(await fan('/commit',{record:r,preparedVotes:votes}),'S156:COMMIT',r);
 if(committed.length<2)throw Error('W156_COMMIT_QUORUM_UNAVAILABLE');
 const cert=await read();if(cert.body.slot!==r.slot||cert.body.head!==r.head)throw Error('W156_UNCERTIFIED_COMMIT');return cert;
}
const server=P.serve(cfg.key,cfg.cert,cfg.ca,async(req,b)=>{if(req.url==='/read'){if(!req.socket.authorized||!cfg.readPins.includes(P.fp(req.socket.getPeerCertificate(true))))throw Error('W156_READER_NOT_PINNED');return read(b);}P.peer(req,cfg.coordinatorPin);if(req.url!=='/pin')throw Error('W156_ROUTE_INVALID');if(busy)throw Error('W156_PROXY_BUSY');busy=true;try{return await pin(b);}finally{busy=false;}});
process.on('message',v=>{if(v==='stop')server.close(()=>process.exit(0));});
module.exports={read,pin};
