import net from 'node:net';
import {readFileSync,chmodSync,existsSync,unlinkSync,lstatSync} from 'node:fs';
import {createPrivateKey,createPublicKey} from 'node:crypto';
import {AtomicWitness} from './p443_atomic.mjs';
const c=JSON.parse(readFileSync(process.argv[2],'utf8'));
const key=(p,secret=false)=>secret?createPrivateKey(readFileSync(p)):createPublicKey(readFileSync(p));
const clients=Object.fromEntries(Object.entries(c.clients).map(([id,p])=>[id,key(p)]));
const witness=new AtomicWitness(c.db,{deployment:c.deployment,witnessPrivate:key(c.witnessPrivate,true),witnessPublic:key(c.witnessPublic),adminPublic:key(c.adminPublic),ownerPublic:key(c.ownerPublic),clients,cap:c.cap??32});
const server=net.createServer(socket=>{
 let input='',done=false;
 socket.setEncoding('utf8');socket.setTimeout(2000,()=>socket.destroy());socket.on('error',()=>{});
 socket.on('data',chunk=>{
  if(done)return;input+=chunk;
  if(input.length>65536){done=true;socket.end(JSON.stringify({ok:false,reason:'oversized'})+'\n');return;}
  const pos=input.indexOf('\n');if(pos<0)return;done=true;
  let out;
  try{const req=JSON.parse(input.slice(0,pos));
   if(req?.action==='POLICY')out=witness.applyPolicy(req.policy);
   else if(req?.action==='READ'||req?.action==='CAS')out=witness.execute(req);
   else out={ok:false,reason:'unsupported-action'};
  }catch{out={ok:false,reason:'invalid-request'};}
  socket.end(JSON.stringify(out)+'\n');
 });
});
if(existsSync(c.socket)){
 const st=lstatSync(c.socket);
 if(!st.isSocket())throw Error('socket-path-is-not-socket');
 if(!c.reclaimStaleSocket)throw Error('socket-already-exists');
 // Supervisor-only option: ownership alone does not establish that socket is stale.
 if(st.uid!==process.getuid())throw Error('socket-owner-mismatch');
 unlinkSync(c.socket);
}
server.on('error',e=>{console.error(e.message);process.exitCode=1;});
server.listen(c.socket,()=>{chmodSync(c.socket,c.socketMode??0o660);process.send?.({ready:true});});
process.on('SIGTERM',()=>{server.close(()=>{witness.close();process.exit(0)});});
