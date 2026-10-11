import {createConnection} from 'node:net';
import {readFileSync} from 'node:fs';
const [socket,reqPath]=process.argv.slice(2);
const req=JSON.parse(readFileSync(reqPath,'utf8'));
const out=await new Promise(resolve=>{const s=createConnection(socket);let body='',done=false;const finish=x=>{if(done)return;done=true;s.destroy();resolve(x)};s.setTimeout(2500,()=>finish({ok:false,reason:'timeout'}));s.on('error',e=>finish({ok:false,reason:e.code}));s.on('connect',()=>s.write(JSON.stringify(req)+'\n'));s.on('data',x=>{body+=x;if(body.includes('\n')){try{finish(JSON.parse(body.split('\n')[0]))}catch{finish({ok:false,reason:'invalid-response'})}}});});
console.log(JSON.stringify(out));