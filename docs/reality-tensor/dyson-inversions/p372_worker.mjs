import {SerializedAuthority} from './p372_authority.mjs';
const [path,id,epochText,hex]=process.argv.slice(2);
const start=process.hrtime.bigint();
try{const db=new SerializedAuthority(path);const result=db.reserve(id,Number(epochText),hex.repeat(64));db.close();console.log(JSON.stringify({...result,latencyMs:Number(process.hrtime.bigint()-start)/1e6}));}
catch(e){console.log(JSON.stringify({ok:false,error:e.message}));process.exitCode=1;}
