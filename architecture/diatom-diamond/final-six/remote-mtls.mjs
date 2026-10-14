/** OASIS final two-device transport. TLS 1.3 mutual authentication, and signed OBF2 envelopes.
 * This is an ADDITIVE transport to frozen KET / {{i}} / OBS. One writer per journal.
 * Uses server-issued ACK over authenticated encrypted channel. Not a claim of
 * exactly-once downstream effects or of factual truth.
 */
import tls from 'node:tls';
import fs from 'node:fs';
import {signedEnvelope,verifyEnvelope,ReceiptJournal,MAX_REQUEST} from './secure-relay.mjs';
import {encodeField} from '../astrophage-compact-v2.1.mjs';
import {SOURCE} from '../astrophage-field-v2.0.mjs';
const MAX_ACK=2048;
function frame(data) { const b=Buffer.from(JSON.stringify(data),'utf8'); if(b.length>MAX_REQUEST)throw Error('oversized request'); const h=Buffer.alloc(4);h.writeUInt32BE(b.length);return Buffer.concat([h,b]); }
function readText(file){return fs.readFileSync(file,'utf8');}
export function createRemoteReceiver({bindAddress,port,journalFile,serverKey,serverCert,caCert,allowedSenderId,allowedSenderPublicKey,crashAfterCommitId=null}) {
  if(!bindAddress||!Number.isInteger(port)||port<1||port>65535)throw Error('explicit host address and TCP port required');
  if(!allowedSenderId||!allowedSenderPublicKey)throw Error('trusted signer required');
  const journal=new ReceiptJournal(journalFile);let crashUsed=false;
  const server=tls.createServer({key:readText(serverKey),cert:readText(serverCert),ca:readText(caCert),
    minVersion:'TLSv1.3',maxVersion:'TLSv1.3',requestCert:true,rejectUnauthorized:true},socket=>{
      if(!socket.authorized){socket.destroy();return}
      socket.setTimeout(12000,()=>socket.destroy()); socket.setNoDelay(true);
      let buf=Buffer.alloc(0);
      socket.on('data',chunk=>{
        buf=Buffer.concat([buf,chunk]);if(buf.length>MAX_REQUEST+4){socket.destroy();return}
        while(buf.length>=4){const size=buf.readUInt32BE(0);if(!size||size>MAX_REQUEST){socket.destroy();return}
          if(buf.length<size+4)break;
          const message=buf.subarray(4,size+4);buf=buf.subarray(size+4);
          let result;
          try{
            const env=JSON.parse(message.toString('utf8'));
            const verified=verifyEnvelope(env,new Map([[allowedSenderId,readText(allowedSenderPublicKey)]]));
            result=journal.apply(verified);
            if(!crashUsed&&result.status==='APPLIED'&&verified.id===crashAfterCommitId){
              crashUsed=true;socket.destroy();process.exit(86); // test-only crash AFTER journal fsync and BEFORE ACK
            }
          }catch(e){result={ok:false,status:'REJECTED',error:String(e.message||e).slice(0,160)};}
          socket.write(frame(result));
        }
      });
      socket.on('error',()=>{});
    });
  server.on('close',()=>journal.close());server.listen(port,bindAddress);
  return {server,journal};
}
export async function submitRemote({address,port,envelope,caCert,clientKey,clientCert,servername='oasis.local',timeoutMs=12000}) {
  if(!address||!Number.isInteger(port))throw Error('remote host/port required');
  const data=frame(envelope);
  return await new Promise((resolve,reject)=>{
    const s=tls.connect({host:address,port,servername,ca:readText(caCert),key:readText(clientKey),
      cert:readText(clientCert),minVersion:'TLSv1.3',maxVersion:'TLSv1.3',rejectUnauthorized:true});
    let b=Buffer.alloc(0),done=false;
    const fail=e=>{if(!done){done=true;s.destroy();reject(e)}};
    s.setTimeout(timeoutMs,()=>fail(Error('remote ACK timeout')));s.setNoDelay(true);
    s.on('error',fail);
    s.on('secureConnect',()=>{if(!s.authorized){fail(Error('server TLS identity not verified'));return}s.write(data)});
    s.on('data',chunk=>{
      b=Buffer.concat([b,chunk]);if(b.length>MAX_ACK+4){fail(Error('overlong ACK'));return}
      if(b.length>=4){const n=b.readUInt32BE(0);if(n>MAX_ACK){fail(Error('overlong ACK'));return}
        if(b.length>=n+4&&!done){done=true;let response;try{response=JSON.parse(b.subarray(4,4+n).toString('utf8'));}catch(e){s.destroy();reject(e);return}s.end();resolve(response)}}
    });
    s.on('close',()=>{if(!done)fail(Error('connection closed before authenticated ACK'))});
  });
}
async function main(args){
  if(args[0]==='serve'){
    const [_,bindAddress,portText,journal,serverKey,serverCert,caCert,allowedSenderPublicKey,allowedSenderId,...flags]=args;
    if(!allowedSenderId)throw Error('serve <private-LAN-address> <port> <journal> <server.key> <server.crt> <ca.crt> <sender.pub.pem> <senderId> [--test-crash <id>]');
    const index=flags.indexOf('--test-crash');const crashId=index>=0?flags[index+1]:null;
    const {server}=createRemoteReceiver({bindAddress,port:Number(portText),journalFile:journal,serverKey,serverCert,caCert,
      allowedSenderPublicKey,allowedSenderId,crashAfterCommitId:crashId});
    server.on('listening',()=>console.log(`READY OASIS mTLS ${bindAddress}:${portText}; trusted signer ${allowedSenderId}`));
  } else if(args[0]==='send') {
    const [_,address,portText,caCert,clientCert,clientKey,senderPrivateKey,senderId,eventId]=args;
    if(!eventId)throw Error('send <server-IP> <port> <ca.crt> <client.crt> <client.key> <sender.private.pem> <senderId> <eventId>');
    const envelope=signedEnvelope({sender:senderId,id:eventId,frame:encodeField(SOURCE),privateKey:readText(senderPrivateKey)});
    const ack=await submitRemote({address,port:Number(portText),envelope,caCert,clientCert,clientKey});
    console.log(JSON.stringify({tls:'TLSv1.3/mTLS',address,port:Number(portText),sender:senderId,eventId,ack},null,2));
    if(!ack.ok)process.exitCode=2;
  }else throw Error('Use serve or send, see TWO_DEVICE_SETUP.md');
}
if(process.argv[1]&&new URL(import.meta.url).pathname===process.argv[1]){
  main(process.argv.slice(2)).catch(e=>{console.error('OASIS_REMOTE_ERROR',e.message);process.exitCode=1});
}