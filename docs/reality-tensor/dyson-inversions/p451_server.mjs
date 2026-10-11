import tls from 'node:tls';
import fs from 'node:fs';
import {DatabaseSync} from 'node:sqlite';
import {createPrivateKey,createPublicKey,verify,sign} from 'node:crypto';
import {IndependentAnchor} from './p449_anchor.mjs';
const c=JSON.parse(fs.readFileSync(process.argv[2]));
const anchor=new IndependentAnchor(c.anchorDb,fs.readFileSync(c.primaryPublic),c.deployment);
const client=createPublicKey(fs.readFileSync(c.clientPublic));
const secret=createPrivateKey(fs.readFileSync(c.anchorPrivate));
const replay=new DatabaseSync(c.replayDb);replay.exec('PRAGMA journal_mode=WAL;PRAGMA synchronous=FULL;CREATE TABLE IF NOT EXISTS requests(deployment TEXT,nonce TEXT,PRIMARY KEY(deployment,nonce))');
const payload=x=>Buffer.from(JSON.stringify({domain:'ROOT0/P450/request',deployment:x.deployment,nonce:x.nonce,action:x.action,stamp:x.stamp??null}));
const response=(nonce,result)=>{const body={domain:'ROOT0/P450/response',deployment:c.deployment,nonce,result};return {...body,signature:sign(null,Buffer.from(JSON.stringify(body)),secret).toString('base64')}};
const s=tls.createServer({key:fs.readFileSync(c.tlsKey),cert:fs.readFileSync(c.tlsCert),ca:fs.readFileSync(c.caCert),requestCert:true,rejectUnauthorized:true,minVersion:'TLSv1.3'},sock=>{
 let b='';let done=false;sock.on('error',()=>{});sock.setEncoding('utf8');sock.setTimeout(3000,()=>sock.destroy());sock.on('data',t=>{
 if(done)return;b+=t;if(b.length>65536){done=true;sock.destroy();return;}let at=b.indexOf('\n');if(at<0)return;done=true;let r,nonce='';
 try{const x=JSON.parse(b.slice(0,at));nonce=x.nonce;
 const auth=x.deployment===c.deployment&&/^[0-9a-f]{32}$/.test(x.nonce)&&['OBSERVE','COMPARE','LATEST'].includes(x.action)&&verify(null,payload(x),client,Buffer.from(x.signature,'base64'));
 if(!auth)r={ok:false,reason:'unauthorized'};
 else {const claimed=replay.prepare('INSERT OR IGNORE INTO requests VALUES(?,?)').run(c.deployment,x.nonce);r=claimed.changes!==1?{ok:false,reason:'replay'}:x.action==='OBSERVE'?anchor.observe(x.stamp):x.action==='COMPARE'?anchor.compare(x.stamp):{ok:true,stamp:anchor.latest()};}
 }catch{r={ok:false,reason:'malformed'}}
 sock.end(JSON.stringify(response(nonce,r))+'\n');
 });});
s.on('tlsClientError',(err)=>console.error('TLSCLIENT',err.message));s.on('error',err=>console.error('SERVERERROR',err.message));
s.listen(c.port,'127.0.0.1',()=>process.send?.({ready:true,port:s.address().port}));
