import assert from 'node:assert/strict';
import {mkdtemp,mkdir,writeFile,chown,chmod,rm} from 'node:fs/promises';
import {tmpdir} from 'node:os';import {join} from 'node:path';import {spawnSync} from 'node:child_process';import {performance} from 'node:perf_hooks';
const t=performance.now(),root=await mkdtemp(join(tmpdir(),'root0-p457-'));
const actors={controller:{uid:33,gid:33},rotation:{uid:65534,gid:65534},anchor:{uid:1000,gid:1000}};
let assertions=0;const check=(v,label)=>{assert.ok(v,label);assertions++};
const read=(p,actor)=>spawnSync('setpriv',['--reuid',String(actor.uid),'--regid',String(actor.gid),'--clear-groups','node','-e',`require('fs').readFileSync(process.argv[1])`,p],{encoding:'utf8'});
try{
 await chmod(root,0o755);
 for(const [role,id] of Object.entries(actors)){
  const dir=join(root,role);await mkdir(dir,{mode:0o700});await chown(dir,id.uid,id.gid);await chmod(dir,0o700);
  const file=join(dir,'signing-key.pem');await writeFile(file,`P457_DEMO_KEY_${role}`,{mode:0o600});await chown(file,id.uid,id.gid);await chmod(file,0o600);
 }
 for(const [name,a] of Object.entries(actors))for(const [owner] of Object.entries(actors)){
  const result=read(join(root,owner,'signing-key.pem'),a);check(name===owner?result.status===0:result.status!==0,`${name} reading ${owner} private key`);
 }
 check(read(join(root,'controller','signing-key.pem'),actors.controller).status===0,'controller own key');
 check(read(join(root,'rotation','signing-key.pem'),actors.rotation).status===0,'rotation own key');
 check(read(join(root,'anchor','signing-key.pem'),actors.anchor).status===0,'anchor own key');
 console.log(JSON.stringify({gate:'P4.57',status:'PASS',assertions,elapsedMs:+(performance.now()-t).toFixed(3),separateUnixUids:true,sameKernel:true},null,2));
}finally{await rm(root,{recursive:true,force:true})}