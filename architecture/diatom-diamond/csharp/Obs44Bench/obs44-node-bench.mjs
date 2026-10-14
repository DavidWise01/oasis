import {performance} from 'node:perf_hooks';
import {bindOBS,recoverOBS} from '../../obs-token-bus-v1.2.mjs';
const glyphs=['n',...'abcdefghijklm',...'opqrstuvwx',...'yz',...'12345678','9','>','|',':','"','^','(','-','+','.0x'];
if(glyphs.length!==44||new Set(glyphs).size!==44) throw new Error('OBS44 registry mismatch');
const toKernel=xs=>xs.map(x=>String(glyphs.indexOf(x)));
const fromKernel=xs=>xs.map(x=>{let k=Number(x);if(!Number.isSafeInteger(k)||String(k)!==x||k<0||k>43)throw new Error('invalid code');return glyphs[k]});
const count=Number(process.argv[2]||20000),runs=Number(process.argv[3]||5);
if(!Number.isSafeInteger(count)||count<1||count>1e6||!Number.isSafeInteger(runs)||runs<1||runs>11)throw Error('args');
function once(n){
 let seq=0,done=0;const start=performance.now();
 while(done<n){
  const take=Math.min(32,n-done);
  const expected=Array.from({length:take},(_,i)=>glyphs[(done+i)%44]);
  const packet=bindOBS(toKernel(expected));
  const got=fromKernel(recoverOBS(packet));
  if(JSON.stringify(got)!==JSON.stringify(expected))throw Error('recovery');
  done+=take;seq++;
 }
 return {tokens:done,frames:seq,elapsedSeconds:(performance.now()-start)/1000};
}
once(Math.min(count,1024));
const samples=Array.from({length:runs},()=>once(count));
const rates=samples.map(x=>x.tokens/x.elapsedSeconds).sort((a,b)=>a-b);
console.log(JSON.stringify({kind:'obs44-node-baseline',node:process.version,count,runs,medianTokensPerSecond:rates[rates.length>>1],samples}));
