'use strict';
// mTLS client with bounded keep-alive pool and pinned server certificate identity.
const https=require('node:https'),fs=require('node:fs'),tls=require('node:tls');
function make(identity,nodes){const key=fs.readFileSync(identity.key),cert=fs.readFileSync(identity.cert),ca=fs.readFileSync(identity.ca);
 const agents=Object.fromEntries(Object.keys(nodes).map(n=>[n,new https.Agent({keepAlive:true,maxSockets:2,maxFreeSockets:2,timeout:5000,maxTotalSockets:2})]));
 const sockets=new Set(),metrics={requests:0,handshakes:0,pageBytes:0};
 async function rpc(name,path,body={}){const n=nodes[name];if(!n)throw Error('S162_UNKNOWN_NODE');metrics.requests++;const bytes=Buffer.from(JSON.stringify(body));if(bytes.length>15900)throw Error('S162_REQUEST_TOO_LARGE');
  return new Promise((resolve,reject)=>{let finished=false;const req=https.request({hostname:'127.0.0.1',port:n.port,path,method:'POST',key,cert,ca,servername:'localhost',minVersion:'TLSv1.2',rejectUnauthorized:true,agent:agents[name],timeout:6000,checkServerIdentity:(name,c)=>{const err=tls.checkServerIdentity(name,c);if(err)return err;return c.fingerprint256?.replaceAll(':','').toLowerCase()===n.serverPin?undefined:Error('S162_SERVER_PIN');},headers:{'content-type':'application/json','content-length':bytes.length}},res=>{const chunks=[];res.on('data',x=>chunks.push(x));res.on('end',()=>{try{const buf=Buffer.concat(chunks);metrics.pageBytes+=buf.length;const value=JSON.parse(buf.toString());if(res.statusCode!==200)reject(Error(value.error||'S162_HTTP_'+res.statusCode));else resolve(value);}catch(e){reject(e);}});});
   req.on('socket',socket=>{if(!sockets.has(socket)){sockets.add(socket);metrics.handshakes++;socket.once('close',()=>sockets.delete(socket));}});
   req.on('error',reject);req.on('timeout',()=>req.destroy(Error('S162_RPC_TIMEOUT')));req.end(bytes);
  });}
 function close(){for(const a of Object.values(agents))a.destroy();sockets.clear();}
 return{rpc,close,metrics};}
module.exports={make};
