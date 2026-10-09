'use strict';
const fs=require('node:fs'),https=require('node:https');const S=require('./serial142');
const cfg=JSON.parse(fs.readFileSync(process.env.SHEET142_CONFIG,'utf8'));
const pub=fs.readFileSync(cfg.pinPublicKey,'utf8');
const server=https.createServer({key:fs.readFileSync(cfg.key),cert:fs.readFileSync(cfg.cert),ca:fs.readFileSync(cfg.ca),requestCert:true,rejectUnauthorized:true,minVersion:'TLSv1.2'},(req,res)=>{
 if(req.url!=='/write'||req.method!=='POST'){res.writeHead(404);res.end();return;}
 if(!req.socket.authorized){res.writeHead(401);res.end();return;}
 let data='';req.on('data',chunk=>{data+=chunk;if(data.length>15000)req.destroy();});req.on('end',async()=>{
  try{const obj=JSON.parse(data);const delay=cfg.testMode===true?obj.testDelayMs||0:0;
    const answer=await S.commit({membershipFile:cfg.membershipFile,resourceFile:cfg.resourceFile,pinFile:cfg.pinFile,pinPublicKey:pub},obj,{delayInsideLockMs:delay});
    res.writeHead(200,{'content-type':'application/json'});res.end(JSON.stringify(answer));}
  catch(e){res.writeHead(409,{'content-type':'application/json'});res.end(JSON.stringify({error:e.message}));}
 });
});
server.listen(0,'127.0.0.1',()=>process.send?.({status:'listening',port:server.address().port}));
process.on('message',m=>{if(m==='stop')server.close(()=>process.exit(0));});
