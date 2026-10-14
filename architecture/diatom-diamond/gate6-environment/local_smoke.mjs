/** Platform-portable local mTLS acceptance using the additive gate6 launcher.
 * No physical-device certification is claimed. Ephemeral secrets are deleted.
 */
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import net from 'node:net';
import { spawn, spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const here=path.dirname(fileURLToPath(import.meta.url));
const cli=process.argv.slice(2),get=x=>{const i=cli.indexOf(x);return i<0?undefined:cli[i+1]};
const repo=path.resolve(get('--repo')||path.join(here,'oasis'));
const state=fs.mkdtempSync(path.join(os.tmpdir(),'oasis-gate6-smoke-'));
const gate=path.join(here,'gate6.mjs');
const port=await new Promise((resolve,reject)=>{const t=net.createServer();t.once('error',reject);t.listen(0,'127.0.0.1',()=>{const p=t.address().port;t.close(()=>resolve(p))})});
const base=['--repo',repo,'--state',state];
let server=null;
function run(action,args=[],expect=0){
 const r=spawnSync(process.execPath,[gate,action,...base,...args],{encoding:'utf8',timeout:20000});
 if(r.status!==expect)throw Error(`${action} expected code ${expect}, got ${r.status}: ${r.stderr}\n${r.stdout}`);
 const raw=r.stdout.trim();const start=raw.indexOf('{');return start>=0?JSON.parse(raw.slice(start)):raw;
}
async function boot(crashId){
 const args=[gate,'serve',...base,'--bind','127.0.0.1','--port',String(port)];
 if(crashId)args.push('--test-crash',crashId);
 server=spawn(process.execPath,args,{stdio:['ignore','pipe','pipe']});
 let output='';await new Promise((resolve,reject)=>{
  const timer=setTimeout(()=>reject(Error('receiver timeout '+output)),10000);
  server.stdout.on('data',c=>{output+=c;if(output.includes('READY OASIS GATE6 mTLS')){clearTimeout(timer);resolve()}});
  server.stderr.on('data',c=>output+=c);
  server.once('exit',code=>{clearTimeout(timer);reject(Error(`Receiver exited early ${code}: ${output}`))});
 });
}
async function stop(){if(!server||server.exitCode!==null)return;const s=server;await new Promise(resolve=>{const timer=setTimeout(()=>{s.kill('SIGKILL');resolve()},3000);s.once('exit',()=>{clearTimeout(timer);resolve()});s.kill()});}
try{
 run('prepare');
 await boot();
 const applied=run('send',['--address','127.0.0.1','--port',String(port),'--event','smoke_base']);
 assert.equal(applied.status,'APPLIED');
 const duplicate=run('send',['--address','127.0.0.1','--port',String(port),'--event','smoke_base']);
 assert.equal(duplicate.status,'DUPLICATE');assert.equal(duplicate.receipt,applied.receipt);
 await stop();await boot('smoke_crash');
 const lost=run('send',['--address','127.0.0.1','--port',String(port),'--event','smoke_crash','--expect-loss','yes']);
 assert.equal(lost.status,'LOST_ACK_EXPECTED');
 if(server.exitCode===null) await new Promise((resolve,reject)=>{const timer=setTimeout(()=>reject(Error('crash receiver did not terminate')),3000);server.once('exit',()=>{clearTimeout(timer);resolve()})});
 assert.equal(server.exitCode,86,'receiver must exit after fsync before ACK');
 await stop();await boot();
 const recovered=run('send',['--address','127.0.0.1','--port',String(port),'--event','smoke_crash']);
 assert.equal(recovered.status,'DUPLICATE');
 const inspected=run('inspect');assert.equal(inspected.entryCount,2);
 const final=run('finalize',['--event','smoke_crash','--mode','loopback']);
 assert.equal(final.verdict,'PASS_IN_REPORTED_ENVIRONMENT');assert.equal(final.physicalIndependenceVerified,false);
 assert.equal(final.receipt,recovered.receipt);
 console.log('GATE6_LOCAL_SMOKE PASS: authenticated mTLS, one durable journal record per event, deliberate post-fsync crash, same receipt on retry. LOCALHOST ONLY.');
}catch(e){console.error('GATE6_LOCAL_SMOKE FAIL',e.stack||e);process.exitCode=1}
finally{await stop();fs.rmSync(state,{recursive:true,force:true})}