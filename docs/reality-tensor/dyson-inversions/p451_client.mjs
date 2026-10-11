import tls from 'node:tls';
import {sign,verify,createPublicKey} from 'node:crypto';
export async function anchorRequest({port,deployment,clientPrivate,anchorPublic,cert,key,ca},action,stamp=null,nonce){
 const x={deployment,nonce,action,stamp};x.signature=sign(null,Buffer.from(JSON.stringify({domain:'ROOT0/P450/request',...x})),clientPrivate).toString('base64');
 const result=await new Promise(resolve=>{const s=tls.connect({host:'127.0.0.1',port,servername:'localhost',cert,key,ca,rejectUnauthorized:true,minVersion:'TLSv1.3'});let b='';let finished=false;const done=r=>{if(finished)return;finished=true;s.end();resolve(r)};s.setTimeout(2500,()=>done({ok:false,reason:'offline'}));s.on('error',e=>done({ok:false,reason:'offline',detail:e.message}));s.on('secureConnect',()=>s.write(JSON.stringify(x)+'\n'));s.on('data',y=>{b+=y;if(b.includes('\n')){try{done(JSON.parse(b.split('\n')[0]))}catch{done({ok:false,reason:'bad-reply'})}}});});
 if(!result.signature)return {ok:false,reason:result.reason==='offline'?'offline':'unverified-response',detail:result.detail};
 const {signature,...body}=result;let valid=false;try{const publicKey=anchorPublic?.type==='public'?anchorPublic:createPublicKey(anchorPublic);valid=body.domain==='ROOT0/P450/response'&&body.deployment===deployment&&body.nonce===nonce&&verify(null,Buffer.from(JSON.stringify(body)),publicKey,Buffer.from(signature,'base64'))}catch{}
 return valid?body.result:{ok:false,reason:'bad-anchor-signature'};
}