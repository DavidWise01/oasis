/**
 * OASIS Gate 6 field launcher. Additive wrapper over the frozen-core RC1 relay.
 * Uses Node >=22; credentials are generated on an operator-controlled host.
 * No private key material is written to logs or distributed in this bundle.
 */
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import { pathToFileURL } from 'node:url';
import { createHash } from 'node:crypto';
import { spawnSync } from 'node:child_process';

const cli = process.argv.slice(2);
const action = cli.shift() || 'help';
const cfgPath = path.resolve(process.env.OASIS_GATE6_CONFIG || './gate6-config.json');
const parse = () => { const out = {}; while(cli.length){const k=cli.shift();if(!k.startsWith('--'))throw Error(`Expected --option, got ${k}`);const v=cli.shift();if(!v||v.startsWith('--'))throw Error(`Missing ${k}`);out[k.slice(2)]=v}return out; };
const opt = parse();
const fail = msg => {throw Error(msg)};
const json = obj => console.log(JSON.stringify(obj,null,2));
const cfg = fs.existsSync(cfgPath) ? JSON.parse(fs.readFileSync(cfgPath,'utf8')) : {};
const repo = path.resolve(opt.repo || cfg.repo || path.join(process.cwd(),'oasis'));
const state = path.resolve(opt.state || cfg.state || path.join(process.cwd(),'gate6-state'));
const source = path.join(repo,'architecture','diatom-diamond');
const signed = path.join(source,'final-six');
const requireSource = () => { for(const p of ['remote-mtls.mjs','setup-keys.mjs','secure-relay.mjs']) if(!fs.existsSync(path.join(signed,p)))fail(`Required source missing: ${p} in ${signed}`); };
const sha = v => createHash('sha256').update(v).digest('hex');
const hashFile = p => sha(fs.readFileSync(p));
const strictId = value => {if(!/^[A-Za-z0-9_-]{1,64}$/.test(value||''))fail(`Invalid ID: ${value}`);return value};
const integerPort = value => {const p=Number(value);if(!Number.isInteger(p)||p<1||p>65535)fail('Port must be 1..65535');return p};
const keys = name => path.join(state,name);
const file = (folder,f)=>path.join(keys(folder),f);
const recordsPath = path.join(state,'evidence','client-events.jsonl');
const journalPath = path.join(state,'receiver','receipts.jsonl');
const proofPath = path.join(state,'evidence','receiver-proof.json');
const resultsPath = path.join(state,'evidence','FINAL_RESULT.json');
const mkdir = p => fs.mkdirSync(p,{recursive:true});
const writeJson = (p,obj) => {mkdir(path.dirname(p));fs.writeFileSync(p,JSON.stringify(obj,null,2)+'\n',{flag:'w'});};
const append = (p,obj) => {mkdir(path.dirname(p));fs.appendFileSync(p,JSON.stringify(obj)+'\n',{flag:'a'});};
const git = (...args) => {const r=spawnSync('git',['-C',repo,...args],{encoding:'utf8'});return r.status===0?r.stdout.trim():null};
const gitSha=()=>git('rev-parse','HEAD')||'UNAVAILABLE';
const verifyFrozen=()=>{const frozen=path.join(source,'frozen','dual5-floor-v0.7','dual5.mjs'); if(!fs.existsSync(frozen))return {present:false,pass:false};const actual=hashFile(frozen),expected='47d4c89ac8155b9470852e0e23d2c059ad087eedc2b7949632a9431b5792fd4b';return {present:true,pass:actual===expected,actual,expected}};
const imports=async()=>{
 requireSource();
 const [transport,relay,codec,field]=await Promise.all([
  import(pathToFileURL(path.join(signed,'remote-mtls.mjs')).href),
  import(pathToFileURL(path.join(signed,'secure-relay.mjs')).href),
  import(pathToFileURL(path.join(source,'astrophage-compact-v2.1.mjs')).href),
  import(pathToFileURL(path.join(source,'astrophage-field-v2.0.mjs')).href),
 ]);
 return {transport,relay,codec,field};
};

export function readJournal(journal) {
 if(!fs.existsSync(journal)) fail(`Journal missing: ${journal}`);
 const buffer=fs.readFileSync(journal,'utf8');
 if(buffer&&!buffer.endsWith('\n'))fail('Journal has an incomplete trailing record; refuse certification');
 const lines=buffer.split('\n').filter(Boolean);
 let prev='0'.repeat(64);const seen=new Set(), events=[];
 for(const [idx,line] of lines.entries()){
  const entry=JSON.parse(line); const {v,sender,id,frameSha256,prev:p,hash}=entry;
  if(Object.keys(entry).join('|')!=='v|sender|id|frameSha256|prev|hash')fail('Invalid journal field ordering');
  if(v!==1||p!==prev||!/^[a-f0-9]{64}$/.test(frameSha256))fail(`Invalid record ${idx}`);
  const core={v,sender,id,frameSha256,prev:p};
  if(sha(Buffer.from(JSON.stringify(core),'utf8'))!==hash)fail(`Hash-chain mismatch at ${idx}`);
  const key=sender+'\0'+id;if(seen.has(key))fail(`Duplicate durable record at ${idx}`);seen.add(key);
  events.push({sender,id,receipt:hash,frameSha256});prev=hash;
 }
 return {entryCount:events.length,head:prev,events};
}

export function evaluate(events,proof,eventId,mode){
 const trace=events.filter(e=>e.eventId===eventId);
 const lostIndex=trace.findIndex(e=>e.status==='LOST_ACK_EXPECTED');
 const dupIndex=trace.findIndex(e=>e.status==='DUPLICATE'&&e.receipt);
 const lost=lostIndex!==-1&&dupIndex>lostIndex;
 const dup=trace[dupIndex];
 const applied=trace.find(e=>e.status==='APPLIED'&&e.receipt);
 const remote=proof.events?.filter(e=>e.id===eventId)||[];
 const unique=remote.length===1;
 const match=!!dup && unique && dup.receipt===remote[0].receipt && (!applied||applied.receipt===dup.receipt);
 const provenance=unique && typeof proof.sourceCommit==='string' && trace.every(e=>e.sourceCommit===proof.sourceCommit&&e.frameSha256===remote[0].frameSha256);
 const pass=lost && match && provenance && proof.entryCount>=1 && proof.journalValid===true;
 return {
  verdict:pass?'PASS_IN_REPORTED_ENVIRONMENT':'FAIL_OR_INCOMPLETE',
  environmentMode:mode, physicalIndependenceVerified:false,
  note:mode==='physical'?'PHYSICAL mode is an operator declaration requiring external device evidence':'Virtual/localhost result is not a two-physical-device certification',
  checks:{ackLostAfterCrash:lost,duplicateAcknowledged:!!dup,uniqueDurableRecord:unique,matchingReceiptHash:match,matchingSourceAndFrame:provenance,journalValid:proof.journalValid===true},
  eventId, receipt:dup?.receipt||null,
 };
}

try{
 if(action==='help'){
  console.log('OASIS Gate6: doctor | prepare | serve | send | inspect | finalize | help');
  console.log('Options: --repo PATH --state PATH --address IP --bind IP --port 32443 --event ID --sender OASIS_TEST --test-crash ID --expect-loss yes --mode vm|physical');
  process.exit(0);
 }
 if(action==='doctor'){
  requireSource();const node=Number(process.versions.node.split('.')[0]);const frozen=verifyFrozen();
  const openssl=spawnSync('openssl',['version'],{encoding:'utf8'});
  const result={node:process.version,nodeOK:node>=22,openssl:openssl.status===0?openssl.stdout.trim():'NOT FOUND',repo,commit:gitSha(),frozen,state,platform:os.platform()};
  json(result);if(!result.nodeOK||!frozen.pass||openssl.status!==0)process.exitCode=2;
 }else if(action==='prepare'){
  requireSource();if(fs.existsSync(keys('server'))||fs.existsSync(keys('client'))||fs.existsSync(keys('root-private')))fail('Credentials already exist. Refusing overwrite; use a new --state directory.');
  mkdir(state);const res=spawnSync(process.execPath,[path.join(signed,'setup-keys.mjs'),state],{encoding:'utf8'});
  if(res.status!==0)fail(res.stderr||'Credential provisioning failed');
  console.log(res.stdout);
  writeJson(path.join(state,'environment.json'),{version:1,preparedUtc:new Date().toISOString(),sourceCommit:gitSha(),hostRole:'provisioning',trust:'private-CA',shareOnly:['server/ to receiver','client/ to sender'],neverShare:['root-private/']});
 }else if(action==='serve'){
  const {transport}=await imports();const bind=opt.bind||'127.0.0.1',port=integerPort(opt.port||'32443');const sender=strictId(opt.sender||'OASIS_TEST');
  if(!fs.existsSync(file('server','server.key')))fail('Receiver server credentials missing');
  const {server}=transport.createRemoteReceiver({bindAddress:bind,port,journalFile:journalPath,serverKey:file('server','server.key'),serverCert:file('server','server.crt'),caCert:file('server','ca.crt'),allowedSenderPublicKey:file('server','sender.pub.pem'),allowedSenderId:sender,crashAfterCommitId:opt['test-crash']||null});
  server.on('listening',()=>console.log(`READY OASIS GATE6 mTLS ${bind}:${port} signer=${sender} eventCrash=${opt['test-crash']||'none'}`));
 }else if(action==='send'){
  const {transport,relay,codec,field}=await imports();const address=opt.address||'127.0.0.1',port=integerPort(opt.port||'32443');const sender=strictId(opt.sender||'OASIS_TEST'),eventId=strictId(opt.event);
  for(const name of ['ca.crt','client.crt','client.key','sender.private.pem'])if(!fs.existsSync(file('client',name)))fail(`Client credential missing: ${name}`);
  const privateKey=fs.readFileSync(file('client','sender.private.pem'),'utf8');const frame=codec.encodeField(field.SOURCE);
  const env=relay.signedEnvelope({sender,id:eventId,frame,privateKey});const evidence={utc:new Date().toISOString(),eventId,sender,address,port,sourceCommit:gitSha(),transport:'TLS1.3/mTLS + Ed25519 + OBF2',frameSha256:sha(frame)};
  try{
   const ack=await transport.submitRemote({address,port,envelope:env,caCert:file('client','ca.crt'),clientCert:file('client','client.crt'),clientKey:file('client','client.key')});
   if(!['APPLIED','DUPLICATE','CONFLICT','REJECTED'].includes(ack.status))fail('Unexpected ACK');
   const record={...evidence,status:ack.status,receipt:ack.receipt||null};append(recordsPath,record);json(record);
   if(!ack.ok)process.exitCode=2;
  }catch(err){
   const isExpected=opt['expect-loss']==='yes';const record={...evidence,status:isExpected?'LOST_ACK_EXPECTED':'TRANSPORT_ERROR',error:String(err.message||err).slice(0,160)};append(recordsPath,record);json(record);
   if(!isExpected)process.exitCode=2;
  }
 }else if(action==='inspect'){
  const result=readJournal(journalPath);
  const proof={version:1,utc:new Date().toISOString(),journalValid:true,sourceCommit:gitSha(),entryCount:result.entryCount,journalHead:result.head,events:result.events};
  writeJson(proofPath,proof);json({proofPath,entryCount:result.entryCount,journalHead:result.head,events:result.events});
 }else if(action==='finalize'){
  if(!fs.existsSync(recordsPath))fail('Client evidence missing; copy client-events.jsonl into state/evidence');
  if(!fs.existsSync(proofPath))fail('Receiver proof missing; copy receiver-proof.json into state/evidence');
  const events=fs.readFileSync(recordsPath,'utf8').trim().split('\n').filter(Boolean).map(x=>JSON.parse(x));
  const proof=JSON.parse(fs.readFileSync(proofPath,'utf8'));
  const mode=opt.mode||'vm';if(!['vm','physical','loopback'].includes(mode))fail('Mode must be vm, physical or loopback');
  const eventId=strictId(opt.event);const verdict=evaluate(events,proof,eventId,mode);
  const result={schema:'OASIS-GATE6-EVIDENCE-v1',utc:new Date().toISOString(),releaseSourceCommit:gitSha(),...verdict};
  writeJson(resultsPath,result);json({...result,resultFile:resultsPath});if(verdict.verdict!=='PASS_IN_REPORTED_ENVIRONMENT')process.exitCode=2;
 }else fail(`Unknown command ${action}`);
}catch(error){console.error('GATE6_ERROR',error.message);process.exitCode=2;}