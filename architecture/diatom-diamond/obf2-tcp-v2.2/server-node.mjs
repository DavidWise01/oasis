import net from 'node:net';
import {decodeDualBytes,encodeDualBytes} from '../astrophage-compact-v2.1.mjs';
const port=Number(process.argv[2]||31024),limit=16+2*65536;
const server=net.createServer(socket=>{
 socket.setNoDelay(true);let pending=Buffer.alloc(0);socket.on('data',chunk=>{
  pending=Buffer.concat([pending,chunk]);
  while(pending.length>=4){const n=pending.readUInt32BE(0);if(n<16||n>limit){socket.write(Buffer.from([1,0,0,0,0]));socket.end();return}
   if(pending.length<4+n)break;
   const frame=pending.subarray(4,4+n); pending=pending.subarray(4+n);
   let body,pass;try{body=encodeDualBytes(decodeDualBytes(frame));pass=1}catch{body=Buffer.alloc(0);pass=0}
   const hdr=Buffer.alloc(5);hdr[0]=pass?0:1;hdr.writeUInt32BE(body.length,1);socket.write(Buffer.concat([hdr,body]));
  }
 });
 socket.on('error',()=>{});
});
server.listen(port,'127.0.0.1',()=>console.log('READY node '+port));
