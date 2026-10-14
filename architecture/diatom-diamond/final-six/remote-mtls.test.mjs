/** One final local encrypted-channel acceptance run; does NOT count as physical two-device gate. */
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import tls from 'node:tls';
import {spawn} from 'node:child_process';
import {generateKeyPairSync} from 'node:crypto';
import {setTimeout as pause} from 'node:timers/promises';
import {signedEnvelope,ReceiptJournal} from './secure-relay.mjs';
import {submitRemote} from './remote-mtls.mjs';
import {encodeField} from '../astrophage-compact-v2.1.mjs';
import {SOURCE} from '../astrophage-field-v2.0.mjs';
const root=fs.mkdtempSync(path.join(os.tmpdir(),'oasis-final-mtls-'));
const script=new URL('./remote-mtls.mjs',import.meta.url).pathname;
const keys=new URL('./setup-keys.mjs',import.meta.url).pathname;
const port=32524;
const result={scope:'same-host loopback TLS; 2 independent devices NOT yet observed',mode:'TLSv1.3 mTLS + Ed25519 + OBF2 + durable ACK',checks:[],gate6:'PARTIAL'};
const cert=(which,name)=>path.join(root,which,name);
const journal=path.join(root,'server','receipts.jsonl');
function check(name){result.checks.push(name);console.log('FINAL_LOCAL_MTLS_CHECK',name)}
let child;
async function boot(crashId){
 const args=[script,'serve','127.0.0.1',String(port),journal,cert('server','server.key'),cert('server','server.crt'),cert('server','ca.crt'),cert('server','sender.pub.pem'),'OASIS_TEST'];
 if(crashId)args.push('--test-crash',crashId);
 child=spawn(process.execPath,args,{stdio:['ignore','pipe','pipe']});
 let output='';await new Promise((resolve,reject)=>{
  const timeout=setTimeout(()=>reject(new Error('server ready timeout '+output)),5000);
  child.stdout.on('data',chunk=>{output+=chunk;if(output.includes('READY OASIS mTLS')){clearTimeout(timeout);resolve()}});
  child.stderr.on('data',chunk=>output+=chunk);
  child.on('exit',code=>{clearTimeout(timeout);reject(new Error('receiver stopped before ready '+code+' '+output))});
 });return child;
}
async function stop(){if(!child||child.exitCode!==null)return;const p=child;const end=new Promise(resolve=>p.once('exit',resolve));p.kill('SIGTERM');await Promise.race([end,pause(1000)]);if(p.exitCode===null)p.kill('SIGKILL')}
const config={address:'127.0.0.1',port,caCert:cert('client','ca.crt'),clientKey:cert('client','client.key'),clientCert:cert('client','client.crt')};
const key=()=>fs.readFileSync(cert('client','sender.private.pem'),'utf8');
const packet=encodeField(SOURCE);
const env=id=>signedEnvelope({sender:'OASIS_TEST',id,frame:packet,privateKey:key()});
try{
 const prep=spawn(process.execPath,[keys,root],{stdio:'pipe'});
 let output='';for await (const c of prep.stdout)output+=c;
 const status=await new Promise(resolve=>prep.on('exit',resolve));assert.equal(status,0,'credential provisioning failed');check('private trust roots generated locally, no keys included in release');
 await boot();
 let a=await submitRemote({...config,envelope:env('final-001')});assert.equal(a.status,'APPLIED');const hash=a.receipt;
 a=await submitRemote({...config,envelope:env('final-001')});assert.equal(a.status,'DUPLICATE');assert.equal(a.receipt,hash);
 check('TLS1.3 mutual-authenticated signed field + duplicate ACK');
 const rogue=generateKeyPairSync('ed25519').privateKey;
 const bad=signedEnvelope({sender:'OASIS_TEST',id:'rogue-001',frame:packet,privateKey:rogue});
 assert.equal((await submitRemote({...config,envelope:bad})).status,'REJECTED');check('untrusted Ed25519 signature rejected over valid TLS');
 const b=await new Promise(resolve=>{
  const s=tls.connect({host:'127.0.0.1',port,servername:'oasis.local',ca:fs.readFileSync(config.caCert),rejectUnauthorized:true,minVersion:'TLSv1.3',maxVersion:'TLSv1.3'});
  let resolved=false;function done(value){if(!resolved){resolved=true;s.destroy();resolve(value)}}
  s.on('secureConnect',()=>{ // handshake should fail, but no credential = not authorized server side
    s.write(Buffer.from([0,0,0,2,123,125]));
    setTimeout(()=>done(false),300);
  });
  s.on('error',()=>done(true));s.on('close',()=>done(true));s.setTimeout(1000,()=>done(false));
 });assert.equal(b,true);check('connection without client certificate rejected by mutual TLS');
 await stop();
 await boot('final-crash');
 let lostAck=false;try{await submitRemote({...config,envelope:env('final-crash'),timeoutMs:1000})}catch{lostAck=true}
 assert.equal(lostAck,true);
 await stop();await boot();
 a=await submitRemote({...config,envelope:env('final-crash')});assert.equal(a.status,'DUPLICATE');
 const journalInspect=new ReceiptJournal(journal);assert.equal(journalInspect.size,2);journalInspect.close();
 check('process exit after fsync/before ACK -> authenticated retry gives one durable receipt');
 result.result='PASS';
}catch(e){result.result='FAIL';result.error=String(e?.stack||e);console.error(result.error);process.exitCode=1}
finally{await stop();fs.rmSync(root,{recursive:true,force:true});fs.writeFileSync(new URL('./remote-mtls-results.json',import.meta.url),JSON.stringify(result,null,2)+'\n');console.log('FINAL_LOCAL_MTLS_SUMMARY',JSON.stringify({result:result.result,checks:result.checks.length,gate6:result.gate6}));}