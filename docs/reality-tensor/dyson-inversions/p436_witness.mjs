import {readFileSync} from 'node:fs';
import {createPrivateKey,sign} from 'node:crypto';
const config=JSON.parse(readFileSync(process.argv[2],'utf8'));
const privateKey=createPrivateKey(readFileSync(config.privateKeyPath));
const payload=x=>Buffer.from(JSON.stringify({domain:'ROOT0/P436/receipt',deployment:x.deployment,nonce:x.nonce,epoch:x.epoch,head:x.head}));
const valid=x=>x&&x.deployment===config.deployment&&/^[0-9a-f]{48}$/.test(x.nonce??'')&&Number.isSafeInteger(x.epoch)&&x.epoch>=0&&/^[0-9a-f]{64}$/.test(x.head??'');
process.on('message',msg=>{
  if(msg?.action==='SIGN'&&valid(msg.request)) {
    const r=msg.request;
    process.send?.({requestId:msg.requestId,ok:true,receipt:{...r,signature:sign(null,payload(r),privateKey).toString('base64')}});
  } else process.send?.({requestId:msg?.requestId,ok:false,reason:'invalid-request'});
});
process.send?.({ready:true});
