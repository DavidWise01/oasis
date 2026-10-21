/* v13: read-only 40-bit receive witnesses layered on v12 guarded pipe.
   Two software replicas are NOT independent physical paths; ix2 stays opaque. */
(function(root){'use strict';
 const PIPE=root.HarvesterVesselPipeV12, VERSION='13.0-receiver-readback', BITS=40;
 const valid=(hex)=>typeof hex==='string'&&/^[0-9A-F]{10}$/.test(hex);
 const bits=hex=>valid(hex)?Array.from(hex,c=>parseInt(c,16).toString(2).padStart(4,'0')).join(''):null;
 const fromBits=b=>{if(typeof b!=='string'||!/^[01]{40}$/.test(b))throw Error('40 binary digits required');return Array.from({length:10},(_,i)=>parseInt(b.slice(4*i,4*i+4),2).toString(16).toUpperCase()).join('')};
 const diff=(a,b)=>Array.from({length:BITS},(_,i)=>i).filter(i=>a?.[i]!==b?.[i]);
 function defaults(){return {version:VERSION,captured:null,readA:null,readB:null,delivered:null,last:null,seq:0,receipts:[],reason:'AWAIT 1 IN',interpretation:'ix2 remains opaque; two software readback witnesses are a provisional experiment'};}
 function receipt(s,kind,tick,detail={}){const seq=s.seq+1,prev=s.receipts.at(-1)?.hash||'00000000';const r={seq,kind,tick:Number(tick),prev,...detail};r.hash=PIPE.checksum(JSON.stringify(r));return {...s,seq,receipts:[...s.receipts,r].slice(-96),reason:detail.reason||kind};}
 function compare(pipe,s){
  const ref=s.captured,source=pipe.inFlight?.hex||null;
  const aa=bits(s.readA),bb=bits(s.readB),rr=bits(ref),src=bits(source);
  if(!rr||!aa||!bb||!src)return {ready:false,matchingBits:0,errorA:40,errorB:40,sourceMismatch:true,badA:[],badB:[],reason:'NO VALID 40-BIT SOURCE / RECEIVERS'};
  const badA=diff(rr,aa),badB=diff(rr,bb),badSource=diff(rr,src);
  return {ready:badA.length===0&&badB.length===0&&badSource.length===0&&pipe.packet?.hex===ref,
   matchingBits:BITS-new Set([...badA,...badB,...badSource]).size,errorA:badA.length,errorB:badB.length,sourceMismatch:badSource.length>0||pipe.packet?.hex!==ref,
   badA,badB,badSource,referenceHex:ref,readA:s.readA,readB:s.readB,
   reason:badA.length||badB.length||badSource.length||pipe.packet?.hex!==ref?'BITWISE RECEIVER MISMATCH':'40/40 SOURCE / A / B MATCH'};
 }
 function flip(hex,bit){if(!valid(hex)||!Number.isInteger(bit)||bit<0||bit>=BITS)throw Error('bit index must be 0..39');const b=bits(hex),replaced=b.slice(0,bit)+(b[bit]==='1'?'0':'1')+b.slice(bit+1);return fromBits(replaced)}
 function command(pipe,integrity,action,{tick=0,seed=pipe.seed,witness={},bit=0}={}){
  let p=pipe,i=integrity;
  const opt={tick,seed,witness};
  if(action==='FLIP_A'||action==='FLIP_B'){
   if(!p.inFlight||!(p.phase==='IN_FLIGHT'||p.phase==='HELD'))return {pipe:p,integrity:receipt(i,'DENY',tick,{reason:'NO OCCUPIED REGISTER TO FAULT'})};
   const key=action==='FLIP_A'?'readA':'readB';
   try{i={...i,[key]:flip(i[key],Number(bit))}}catch(e){return {pipe:p,integrity:receipt(i,'DENY',tick,{reason:e.message})};}
   i=receipt(i,'INJECT',tick,{lane:key,bit:Number(bit),reason:'ONE CONTROLLED RECEIVER BIT FLIPPED'});
  }else if(action==='REPAIR'){
   if(!p.inFlight||!(p.phase==='IN_FLIGHT'||p.phase==='HELD'))return {pipe:p,integrity:receipt(i,'DENY',tick,{reason:'NO OCCUPIED REGISTER TO REPAIR'})};
   i=receipt({...i,readA:i.captured,readB:i.captured},'REPAIR',tick,{reason:'SOFTWARE RECEIVER BUFFERS RESTORED FROM CAPTURED SOURCE'});
  }else if(action==='LOAD'){
   p=PIPE.transition(p,action,opt);
   if(p.phase==='LOADED'&&p.packet?.hex===seed.toUpperCase())i={...i,captured:null,readA:null,readB:null,delivered:null,last:null};
  }else if(action==='IN'){
   const before=p.ingress;p=PIPE.transition(p,action,opt);
   if(p.ingress===before+1&&p.inFlight?.hex){const hex=p.inFlight.hex;i=receipt({...i,captured:hex,readA:hex,readB:hex,delivered:null,last:null},'CAPTURE',tick,{sourceHex:hex,bitCount:BITS,reason:'40-BIT INPUT COPIED TO TWO TEST RECEIVER REGISTERS'});}
  }else if(action==='OUT'){
   const c=compare(p,i);
   if(!c.ready){if(p.phase==='IN_FLIGHT')p=PIPE.transition(p,'OUT',{...opt,witness:{}});
     i=receipt({...i,last:c},'BLOCKED_EGRESS',tick,{errorA:c.errorA,errorB:c.errorB,sourceMismatch:c.sourceMismatch,reason:'40-BIT READBACK FAILED; ZERO EGRESS'});
   }else{
    const before=p.egress;p=PIPE.transition(p,'OUT',opt);
    if(p.egress===before+1){const data={sourceHex:i.captured,receivedHex:i.readA,readbackB:i.readB,bitMatches:40,sourceDigest:PIPE.checksum(i.captured),receiverDigest:PIPE.checksum(i.readA),reason:'EXACT 40-BIT EGRESS MATCH'};
       i=receipt({...i,delivered:i.readA,last:c},'OUT_40_MATCH',tick,data);
    }else i=receipt({...i,last:c},'NO_EGRESS',tick,{reason:'V12 INTERLOCK BLOCKED OUTPUT'});
   }
  }else if(action==='RESUME'){
   const c=compare(p,i);
   if(!c.ready)i=receipt({...i,last:c},'DENY_RESUME',tick,{reason:'RECEIVER MISMATCH MUST BE REPAIRED'});
   else{p=PIPE.transition(p,'RESUME',opt);i=receipt({...i,last:c},'RESUME_WITNESS',tick,{reason:p.phase});}
  }else if(action==='ABORT'){
   p=PIPE.transition(p,'ABORT',opt);
   if(p.phase==='ABORTED')i=receipt(i,'ABORT',tick,{reason:'NO OUTPUT; CAPTURE RETAINED AS AUDIT ONLY'});
  }else if(action==='CLEAR'){
   const occupied=!!p.inFlight;p=PIPE.transition(p,'CLEAR',opt);
   if(!occupied&&p.phase==='EMPTY')i={...i,captured:null,readA:null,readB:null,delivered:null,last:null,reason:'CLEAR'};
  }else if(action==='MONITOR'){
   p=PIPE.transition(p,'MONITOR',opt);
  }else throw Error('Unsupported v13 action '+action);
  if(p.inFlight&&(p.phase==='IN_FLIGHT'||p.phase==='HELD')){
   const c=compare(p,i);i={...i,last:c};
   if(!c.ready&&p.phase==='IN_FLIGHT'){
    p=PIPE.transition(p,'OUT',{...opt,witness:{}});
    i=receipt(i,'INTEGRITY_HOLD',tick,{errorA:c.errorA,errorB:c.errorB,sourceMismatch:c.sourceMismatch,reason:'BIT MISMATCH LATCHED; NO EGRESS'});
   }
  }
  return {pipe:p,integrity:i};
 }
 root.HarvesterIntegrityV13={VERSION,BITS,valid,bits,fromBits,diff,flip,defaults,compare,command};
})(typeof window!=='undefined'?window:globalThis);
