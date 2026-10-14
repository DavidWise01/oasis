/** OASIS signed OBF2 relay v1; additive to frozen kernel, no external side effects.
 * Scoped semantics: one trusted public key per sender, exactly-once DURABLE RECEIPT
 * for a (sender,event ID); network delivery itself remains at-least-once.
 */
import net from 'node:net';
import fs from 'node:fs';
import path from 'node:path';
import {createHash, sign, verify} from 'node:crypto';
import {decodeDualBytes} from '../astrophage-compact-v2.1.mjs';

export const MAX_REQUEST = 512 * 1024;
export const DOMAIN = 'OASIS-SIGNED-OBF2-v1';
const ident = /^[A-Za-z0-9_-]{1,64}$/;
const digest = b => createHash('sha256').update(b).digest('hex');
const unsigned = ({v,sender,id,frame}) => Buffer.from(JSON.stringify([DOMAIN,v,sender,id,frame]), 'utf8');
const exactFields = (obj, names) => obj && !Array.isArray(obj) && typeof obj === 'object' &&
  Object.keys(obj).sort().join('|') === names.slice().sort().join('|');
function canonicalB64(s) {
  if(typeof s!=='string' || s.length>200000 || s.length%4===1 || !/^[A-Za-z0-9+/]*={0,2}$/.test(s))return false;
  return Buffer.from(s,'base64').toString('base64')===s;
}
export function signedEnvelope({sender,id,frame,privateKey}) {
  if(!ident.test(sender)||!ident.test(id)||!Buffer.isBuffer(frame))throw Error('bad sender / id / frame');
  const data={v:1,sender,id,frame:frame.toString('base64')};
  return {...data,sig:sign(null,unsigned(data),privateKey).toString('base64')};
}
export function verifyEnvelope(env,allowed) {
  if(!exactFields(env,['v','sender','id','frame','sig']) || env.v!==1 ||
      typeof env.sender!=='string'||!ident.test(env.sender)||
      typeof env.id!=='string'||!ident.test(env.id)||
      !canonicalB64(env.frame)||!canonicalB64(env.sig))throw Error('malformed envelope');
  const key=allowed.get(env.sender);
  if(!key)throw Error('untrusted sender');
  if(!verify(null,unsigned(env),key,Buffer.from(env.sig,'base64')))throw Error('invalid sender signature');
  const frame=Buffer.from(env.frame,'base64');
  if(frame.length>131088)throw Error('OBF2 frame oversized');
  const bytes=decodeDualBytes(frame); // original frozen format semantics
  return {sender:env.sender,id:env.id,frame,bytes,digest:digest(frame)};
}
function committedRecord(entry,priorHash) {
  const core={v:1,sender:entry.sender,id:entry.id,frameSha256:entry.digest,prev:priorHash};
  return {...core,hash:digest(Buffer.from(JSON.stringify(core),'utf8'))};
}
export class ReceiptJournal {
  #fd;#index=new Map();#tip='0'.repeat(64);
  constructor(filename) {
    fs.mkdirSync(path.dirname(filename),{recursive:true});
    const buf=fs.existsSync(filename)?fs.readFileSync(filename):Buffer.alloc(0);
    const finalNewline=buf.lastIndexOf(10);
    const validLength=finalNewline+1;
    if(validLength!==buf.length) {
      // A crash can leave a partial final JSON record. Never acknowledge it.
      fs.truncateSync(filename,validLength);
    }
    const lines=buf.subarray(0,validLength).toString('utf8').split('\n').filter(Boolean);
    for(const line of lines) {
      const r=JSON.parse(line);
      if(!exactFields(r,['v','sender','id','frameSha256','prev','hash']) ||
         !ident.test(r.sender)||!ident.test(r.id)||r.prev!==this.#tip ||
         !/^[a-f0-9]{64}$/.test(r.frameSha256))throw Error('invalid journal record');
      const expected=committedRecord({sender:r.sender,id:r.id,digest:r.frameSha256},this.#tip);
      if(JSON.stringify(r)!==JSON.stringify(expected))throw Error('journal hash chain mismatch');
      const key=r.sender+'\0'+r.id;
      if(this.#index.has(key))throw Error('duplicate journal event');
      this.#index.set(key,r);this.#tip=r.hash;
    }
    this.#fd=fs.openSync(filename,'a');
  }
  get size(){return this.#index.size}
  get tip(){return this.#tip}
  apply(entry) {
    const key=entry.sender+'\0'+entry.id,seen=this.#index.get(key);
    if(seen) {
      if(seen.frameSha256!==entry.digest)return {ok:false,status:'CONFLICT',id:entry.id};
      return {ok:true,status:'DUPLICATE',id:entry.id,receipt:seen.hash};
    }
    const r=committedRecord(entry,this.#tip);
    const line=Buffer.from(JSON.stringify(r)+'\n','utf8');
    // Synchronous append+fsync is the commit point, before ACK. Single writer only.
    let pos=0;
    while(pos<line.length){const n=fs.writeSync(this.#fd,line,pos,line.length-pos);if(!n)throw Error('incomplete journal write');pos+=n}
    fs.fsyncSync(this.#fd);
    this.#index.set(key,r);this.#tip=r.hash;
    return {ok:true,status:'APPLIED',id:entry.id,receipt:r.hash};
  }
  close(){if(this.#fd!==undefined){fs.closeSync(this.#fd);this.#fd=undefined}}
}
function answer(socket,obj) {
  const body=Buffer.from(JSON.stringify(obj));const header=Buffer.allocUnsafe(4);header.writeUInt32BE(body.length);
  socket.write(Buffer.concat([header,body]));
}
export function createReceiver({address='127.0.0.1',port,journalFile,trustedPublicKeys,crashAfterCommitId=null}) {
  if(!(trustedPublicKeys instanceof Map)||trustedPublicKeys.size===0)throw Error('trusted sender list required');
  const journal=new ReceiptJournal(journalFile);
  let crashUsed=false;
  const server=net.createServer(socket=>{
    socket.setNoDelay(true);socket.setTimeout(5000,()=>socket.destroy());
    let pending=Buffer.alloc(0);
    socket.on('data',chunk=>{
      pending=Buffer.concat([pending,chunk]);
      if(pending.length>MAX_REQUEST+4){socket.destroy();return}
      while(pending.length>=4){
        const len=pending.readUInt32BE(0);
        if(!len||len>MAX_REQUEST){socket.destroy();return}
        if(pending.length<len+4)break;
        const bytes=pending.subarray(4,4+len);pending=pending.subarray(len+4);
        try{
          const obj=JSON.parse(bytes.toString('utf8'));
          const valid=verifyEnvelope(obj,trustedPublicKeys);
          const result=journal.apply(valid);
          if(!crashUsed && result.status==='APPLIED' && valid.id===crashAfterCommitId){
            crashUsed=true; socket.destroy();process.exit(86); // explicit crash AFTER fsync BEFORE ACK
          }
          answer(socket,result);
        }catch(error){answer(socket,{ok:false,status:'REJECTED',error:String(error.message||error)});}
      }
    });
    socket.on('error',()=>{});
  });
  server.on('close',()=>journal.close());
  server.listen(port,address);
  return {server,journal};
}
export async function submit({address='127.0.0.1',port,envelope,timeoutMs=4000}) {
  const frame=Buffer.from(JSON.stringify(envelope),'utf8');
  if(frame.length>MAX_REQUEST)throw Error('request too large');
  return new Promise((resolve,reject)=>{
    const client=net.connect({host:address,port});
    client.setNoDelay(true);client.setTimeout(timeoutMs);
    let done=false,buf=Buffer.alloc(0);
    function fail(error){if(!done){done=true;client.destroy();reject(error)}}
    client.on('timeout',()=>fail(new Error('acknowledgement timeout')));
    client.on('error',fail);
    client.on('connect',()=>{
      const header=Buffer.allocUnsafe(4);header.writeUInt32BE(frame.length);
      client.write(Buffer.concat([header,frame]));
    });
    client.on('data',part=>{
      buf=Buffer.concat([buf,part]);
      if(buf.length>=4){const n=buf.readUInt32BE(0);
        if(n>2048){fail(new Error('oversized acknowledgement'));return}
        if(buf.length>=n+4&&!done){done=true;client.end();try{resolve(JSON.parse(buf.subarray(4,4+n).toString('utf8')))}catch(e){reject(e)}}
      }
    });
    client.on('close',()=>{if(!done)fail(new Error('connection closed before ACK'))});
  });
}
if(process.argv[1]?.endsWith('/secure-relay.mjs')&&process.argv[2]==='serve'){
  const [portText,journalPath,pubPath,sender,crashId]=process.argv.slice(3);
  if(!portText||!journalPath||!pubPath||!sender)throw Error('serve <port> <journalPath> <trustedPublicKeyPem> <senderId> [crashId]');
  const service=createReceiver({port:Number(portText),journalFile:journalPath,
    trustedPublicKeys:new Map([[sender,fs.readFileSync(pubPath,'utf8')]]),crashAfterCommitId:crashId||null});
  service.server.on('listening',()=>console.log('READY SECURE OBF2 port='+portText));
}
