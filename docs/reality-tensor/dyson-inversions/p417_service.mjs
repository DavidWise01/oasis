import {createServer,createConnection} from 'node:net';
import {readFile,lstat,unlink,chmod} from 'node:fs/promises';
import {createPublicKey,createPrivateKey,verify} from 'node:crypto';
import {DatabaseSync} from 'node:sqlite';
import {SeparateWitness} from './p415_witness.mjs';
const cfg=JSON.parse(await readFile(process.argv[2],'utf8'));
const pub=createPublicKey(cfg.clientPublicKey),priv=createPrivateKey(cfg.witnessPrivateKey),wpub=createPublicKey(cfg.witnessPublicKey);
const witness=new SeparateWitness(cfg.db,priv,wpub,cfg.deployment);
const db=new DatabaseSync(cfg.db,{timeout:15000});
db.exec('PRAGMA busy_timeout=15000; CREATE TABLE IF NOT EXISTS seen_nonces(deployment TEXT NOT NULL, nonce TEXT NOT NULL, PRIMARY KEY(deployment,nonce));');
const canonical=x=>Buffer.from(JSON.stringify({domain:'ROOT0/P416/request/v1',deployment:x.deployment,action:x.action,epoch:x.epoch,head:x.head,sequence:x.sequence,nonce:x.nonce}));
function valid(r){try{return r&&r.deployment===cfg.deployment&&['READ','REGISTER','RECOVERY_REVIEW'].includes(r.action)&&Number.isSafeInteger(r.sequence)&&r.sequence>=0&&typeof r.nonce==='string'&&r.nonce.length>=8&&r.nonce.length<=128&&typeof r.signature==='string'&&verify(null,canonical(r),pub,Buffer.from(r.signature,'base64'));}catch{return false;}}
const server=createServer(sock=>{let input='';let done=false;sock.setEncoding('utf8');sock.on('data',chunk=>{
 if(done)return;input+=chunk;if(input.length>16384){done=true;sock.end(JSON.stringify({ok:false,reason:'oversized-request'})+'\n');return;}
 if(!input.includes('\n'))return;done=true;let result;
 try{const r=JSON.parse(input.slice(0,input.indexOf('\n')));
 if(!valid(r))result={ok:false,reason:'unauthenticated'};
 else{const insert=db.prepare('INSERT OR IGNORE INTO seen_nonces(deployment,nonce) VALUES(?,?)').run(r.deployment,r.nonce);
 if(insert.changes!==1)result={ok:false,reason:'replay-nonce'};
 else if(r.action==='READ')result=witness.read();
 else if(r.action==='REGISTER')result=witness.register(r.epoch,r.head);
 else result={ok:false,reason:'manual-independent-witness-review-required',authenticatedIntent:true};}}
 catch(e){result={ok:false,reason:'invalid-request',detail:e.message};}
 sock.end(JSON.stringify(result)+'\n');
 });});
async function safeBind(){try{const info=await lstat(cfg.socket);if(!info.isSocket())throw Error('socket-path-not-socket');
 await new Promise((resolve,reject)=>{const s=createConnection(cfg.socket);let finished=false;function end(err){if(finished)return;finished=true;s.destroy();if(err?.code==='ECONNREFUSED'||err?.code==='ENOENT')resolve();else reject(Error('socket-owner-active-or-indeterminate'));}s.setTimeout(500,end);s.once('connect',()=>end());s.once('error',end);});
 await unlink(cfg.socket);
 }catch(e){if(e.code!=='ENOENT')throw e;}
 await new Promise((resolve,reject)=>{server.once('error',reject);server.listen(cfg.socket,resolve);});
 await chmod(cfg.socket,0o600);process.send?.({ready:true});}
await safeBind();
process.on('SIGTERM',()=>{server.close();db.close();witness.close();});