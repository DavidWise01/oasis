import assert from 'node:assert/strict';
import {mkdtemp,writeFile,chmod,chown,stat,rm,readFile} from 'node:fs/promises';
import {join} from 'node:path';import {tmpdir} from 'node:os';
import {generateKeyPairSync} from 'node:crypto';import {spawn} from 'node:child_process';
import {performance} from 'node:perf_hooks';
import {AtomicWitness,signPolicy,signRequest,signIntent} from './p443_atomic.mjs';
const UID_W=65534,UID_C=33,SHARED_GID=65534;
const root=await mkdtemp(join(tmpdir(),'p445-'));let n=0;const ck=(v,m)=>{assert.ok(v,m);n++};const start=performance.now();
const w=generateKeyPairSync('ed25519'),a=generateKeyPairSync('ed25519'),o=generateKeyPairSync('ed25519'),client=generateKeyPairSync('ed25519');
const dep='root0/p445',dir=join(root,'witness'),sock=join(root,'socket'),db=join(dir,'history.db');
async function write(p,k,type){await writeFile(p,k.export({format:'pem',type}),{mode:0o600});}
const pp={w:join(dir,'w.pem'),wp:join(dir,'wp.pem'),ap:join(dir,'ap.pem'),op:join(dir,'op.pem'),cp:join(dir,'cp.pem')};
let child;
function command(args,uid,group=SHARED_GID){return new Promise((resolve)=>{let so='',se='';const p=spawn('setpriv',['--reuid',String(uid),'--regid',String(group),'--clear-groups','node',...args],{stdio:['ignore','pipe','pipe']});p.stdout.on('data',x=>so+=x);p.stderr.on('data',x=>se+=x);p.on('exit',(code,signal)=>resolve({code,signal,out:so,err:se}));});}
async function rpc(req,uid=UID_C,group=SHARED_GID){const path=join(root,'request-'+Math.random().toString(16).slice(2)+'.json');await writeFile(path,JSON.stringify(req),{mode:0o644});const res=await command([new URL('./p445_client.mjs',import.meta.url).pathname,sock,path],uid,group);await rm(path);let data;try{data=JSON.parse(res.out.trim())}catch{data={ok:false,reason:'client-exit',...res}}return {res,data};}
async function launch(){child=spawn('setpriv',['--reuid',String(UID_W),'--regid',String(SHARED_GID),'--clear-groups','node',new URL('./p445_service.mjs',import.meta.url).pathname,join(root,'config.json')],{stdio:['ignore','pipe','pipe']});let err='';child.stderr.on('data',x=>err+=x);await new Promise((resolve,reject)=>{const timeout=setTimeout(()=>reject(Error('startup timeout '+err)),4000);const poll=setInterval(async()=>{try{await stat(sock);clearInterval(poll);clearTimeout(timeout);resolve()}catch{}},10);child.once('exit',code=>{clearTimeout(timeout);clearInterval(poll);reject(Error('exit '+code+' '+err))})});}
try{
 await (await import('node:fs/promises')).mkdir(dir,{mode:0o700});await chown(dir,UID_W,SHARED_GID);await chmod(dir,0o700);
 await write(pp.w,w.privateKey,'pkcs8');await write(pp.wp,w.publicKey,'spki');await write(pp.ap,a.publicKey,'spki');await write(pp.op,o.publicKey,'spki');await write(pp.cp,client.publicKey,'spki');for(const p of Object.values(pp))await chown(p,UID_W,SHARED_GID);
 const init=new AtomicWitness(db,{deployment:dep,witnessPrivate:w.privateKey,witnessPublic:w.publicKey,adminPublic:a.publicKey,ownerPublic:o.publicKey,clients:{controller:client.publicKey}});ck(init.bootstrap('a'.repeat(64)).ok,'bootstrap');init.close();for(const suffix of ['','-wal','-shm']){try{await chown(db+suffix,UID_W,SHARED_GID)}catch{}}
 await chmod(root,0o770);await chown(root,0,SHARED_GID);await writeFile(join(root,'config.json'),JSON.stringify({db,socket:sock,deployment:dep,witnessPrivate:pp.w,witnessPublic:pp.wp,adminPublic:pp.ap,ownerPublic:pp.op,clients:{controller:pp.cp},socketMode:0o660,cap:30}),{mode:0o644});
 await launch();ck((await stat(sock)).mode%512===0o660,'socket 0660');
 const deny=await command(['-e',`require('fs').readFileSync('${pp.w}')`],UID_C);ck(deny.code!==0,'private key inaccessible');
 const denyDb=await command(['-e',`require('fs').readFileSync('${db}')`],UID_C);ck(denyDb.code!==0,'db inaccessible');
 const policy=signPolicy(a.privateKey,{deployment:dep,sequence:0,epoch:0,keys:['controller']});ck((await rpc({action:'POLICY',policy})).data.ok,'policy admin request');
 const req=(nonce,action,intent=null)=>signRequest(client.privateKey,{deployment:dep,keyId:'controller',policyEpoch:0,nonce,action,intent});
 const a1=req('1'.repeat(32),'READ');ck((await rpc(a1)).data.ok,'signed cross-uid read');ck((await rpc(a1)).data.reason==='replay','replay rejected');
 const i=signIntent(o.privateKey,{deployment:dep,epoch:1,prior:'a'.repeat(64),next:'b'.repeat(64),nonce:'2'.repeat(32)});ck((await rpc(req('3'.repeat(32),'CAS',i))).data.ok,'CAS cross-uid');ck(!(await rpc(req('4'.repeat(32),'CAS',i))).data.ok,'CAS replay epoch refused');
 const no=await rpc(req('5'.repeat(32),'READ'),1000,1000);ck(!no.data.ok,'outside peer blocked');
 child.kill('SIGKILL');await new Promise(resolve=>child.once('exit',resolve));ck(!(await rpc(req('6'.repeat(32),'READ'))).data.ok,'outage fail closed');
 await rm(sock);await launch();ck((await rpc(a1)).data.reason==='replay','restart replay persisted');ck((await rpc(req('7'.repeat(32),'READ'))).data.ok,'restart live');
 console.log(JSON.stringify({status:'PASS',assertions:n,elapsedMs:Number((performance.now()-start).toFixed(3)),osUids:[UID_C,UID_W],sameHost:true},null,2));
}finally{child?.kill('SIGKILL');await rm(root,{recursive:true,force:true})}