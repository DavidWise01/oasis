/* AEON thought regression controller v0.5: virtual Hall-proxy channels and digital-pot wipers. */
(function(root){'use strict';
const ORDER=['U','D','L','R','B','A','SEL','START'],BITS={A:0,B:1,SEL:2,START:3,U:4,D:5,L:6,R:7};
const clamp=(n,a,b)=>Math.max(a,Math.min(b,Number(n)||0));
function create(opts={}){
 const fresh=k=>({key:k,hall:0,wiper:128,origin:'virtual',samples:0,negative:0,ambiguous:0,positive:0,regressions:0,lastState:0,prior:null});
 let channels=ORDER.map(fresh),history=[],port=null,reader=null,writer=null,connected=false,rx='',lastTx=0;
 const channel=k=>channels[ORDER.indexOf(String(k||'').toUpperCase())]||null;
 function snapshot(){return {schema:'aeon-thought-hall-digipot-v1',fields:[3,2,1,1,2,3],channels:channels.map(x=>({...x})),history:history.slice(-128)};}
 function restore(s){if(!Array.isArray(s?.channels))return false;s.channels.forEach((v,i)=>{const c=channels[i];if(!c||!v)return;for(const k of ['hall','wiper','samples','negative','ambiguous','positive','regressions','lastState'])if(Number.isFinite(Number(v[k])))c[k]=k==='wiper'?clamp(v[k],32,224):Number(v[k]);if(v.prior)c.prior=v.prior;});if(Array.isArray(s.history))history=s.history.slice(-128);return true;}
 function record(e){
  if(!e||e.delivered!==true||!e.before||!e.after)return null;const c=channel(e.button);if(!c)return null;
  const before={screenHash:String(e.before.screenHash??''),ramHash:String(e.before.ramHash??'')},after={screenHash:String(e.after.screenHash??''),ramHash:String(e.after.ramHash??'')};
  const result=before.screenHash!==after.screenHash?1:(before.ramHash!==after.ramHash?0:-1);
  const repeat=!!c.prior&&c.prior.before===before.screenHash&&c.prior.after===after.screenHash;
  // An unchanged state must not be classified as its own reversal.
  const regression=before.screenHash!==after.screenHash&&!!c.prior&&c.prior.before===after.screenHash&&c.prior.after===before.screenHash;
  if(c.origin==='virtual')c.hall=Math.round(.65*c.hall+.35*(result===1?220:result===0?115:12));
  c.samples++;c.negative+=+(result===-1);c.ambiguous+=+(result===0);c.positive+=+(result===1);c.regressions+=+regression;c.lastState=result;
  c.wiper=clamp(c.wiper+(result===-1?12:result===0?4:-6)-(repeat?5:0)-(regression?10:0),32,224);
  c.prior={before:before.screenHash,after:after.screenHash};
  const r={frame:Number(e.frame)||0,button:c.key,result,repeat,regression,before,after,hall:c.hall,wiper:c.wiper,source:e.source||'ternary'};
  history.push(r);if(history.length>256)history.shift();try{opts.persist?.(snapshot());}catch{}void transmit();return r;
 }
 function holdFor(k,base=2){const c=channel(k);return clamp(Math.round(Number(base)+((c?.wiper??128)-128)/48),1,6);}
 function score(mask){let n=0,sum=0;ORDER.forEach(k=>{if(mask&(1<<BITS[k])){const c=channel(k);n++;sum+=((c.wiper-128)/96)*.13+(c.hall/255-.5)*.12-(c.regressions/(c.samples+1))*.18;}});return n?clamp(sum/n,-.4,.4):0;}
 function readHall(vals){if(!Array.isArray(vals))return false;vals.slice(0,8).forEach((v,i)=>{if(Number.isFinite(Number(v))){channels[i].hall=clamp(v,0,255);channels[i].origin='hardware';}});return true;}
 function receiveLine(line){try{return readHall(JSON.parse(line).hall);}catch{return false;}}
 async function transmit(){if(!writer)return false;const now=Date.now();if(now-lastTx<150)return false;lastTx=now;try{await writer.write(new TextEncoder().encode(JSON.stringify({type:'wipers',values:channels.map(c=>c.wiper)})+'\n'));return true;}catch{return false;}}
 async function connect(){if(connected)return true;const serial=typeof navigator==='undefined'?null:navigator.serial;if(!serial)throw Error('Web Serial requires HTTPS + Chrome/Edge + bridge firmware');
  port=await serial.requestPort();await port.open({baudRate:115200});writer=port.writable.getWriter();reader=port.readable.getReader();connected=true;void transmit();
  (async()=>{try{while(connected){const part=await reader.read();if(part.done)break;rx+=new TextDecoder().decode(part.value);if(rx.length>8192)rx=rx.slice(-1024);let p;while((p=rx.indexOf('\n'))!==-1){receiveLine(rx.slice(0,p));rx=rx.slice(p+1);}}}catch{}finally{connected=false;channels.forEach(c=>c.origin='virtual');try{reader.releaseLock();}catch{}}})();return true;
 }
 async function disconnect(){connected=false;channels.forEach(c=>c.origin='virtual');try{await reader?.cancel();}catch{}try{reader?.releaseLock();}catch{}try{writer?.releaseLock();}catch{}try{await port?.close();}catch{}reader=null;writer=null;port=null;}
 function reset(){channels=ORDER.map(fresh);history=[];try{opts.persist?.(snapshot());}catch{}void transmit();}
 return {order:ORDER,record,holdFor,score,channel,snapshot,restore,readHall,receiveLine,history:()=>history.slice(),connect,disconnect,reset,transmit,mode:()=>connected?'HALL SERIAL / HARDWARE':'VIRTUAL HALL PROXY'};
}
root.AEON_THOUGHT={create};
})(window);