import net from 'node:net';
import fs from 'node:fs';
import {createPrivateKey,createPublicKey} from 'node:crypto';
import {PolicyLedger} from './p441_policy.mjs';
import {StrictCasWitness} from './p434_cas.mjs';
const c=JSON.parse(fs.readFileSync(process.argv[2],'utf8'));
const readKey=p=>createPublicKey(fs.readFileSync(p));
const ledger=new PolicyLedger(c.policyDb,c.deployment,readKey(c.admin),Object.fromEntries(Object.entries(c.clients).map(([id,p])=>[id,readKey(p)])),{cap:c.cap??12});
const witness=new StrictCasWitness(c.casDb,createPrivateKey(fs.readFileSync(c.witnessKey)),readKey(c.witnessPub),readKey(c.ownerPub));
const server=net.createServer(sock=>{let buf='';sock.setEncoding('utf8');sock.on('error',()=>{});sock.on('data',data=>{buf+=data;if(buf.length>65536){sock.end(JSON.stringify({ok:false,reason:'oversized'})+'\n');return;}if(!buf.includes('\n'))return;let result;try{const x=JSON.parse(buf.slice(0,buf.indexOf('\n')));if(x.action==='POLICY')result=ledger.apply(x.policy);else if(['READ','CAS'].includes(x.action)){
 const expectedPayload=JSON.stringify({action:x.action,intent:x.intent??null});
 const authorized=x.auth?.payload===expectedPayload?ledger.consume(x.auth):{ok:false,reason:'payload-mismatch'};
 result=!authorized.ok?authorized:(x.action==='READ'?witness.read(c.deployment):witness.cas(x.intent));
 }else result={ok:false,reason:'unsupported-operation'};}catch(e){result={ok:false,reason:'invalid-request'};}sock.end(JSON.stringify(result)+'\n');});});
server.on('error',e=>{console.error(e.message);process.exitCode=1;});
server.listen(c.socket,()=>{fs.chmodSync(c.socket,0o660);console.log('READY');});
