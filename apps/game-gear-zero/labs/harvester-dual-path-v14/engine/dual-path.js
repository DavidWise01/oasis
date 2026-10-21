/* Harvester v14: two independently scheduled software paths. Symbol {{ix2}} stays opaque.
   Packets are 5 x 8-bit bytes. A retained sender copy is required for retransmission.
   The other receiver's partial data and the 12-bit projection NEVER fill missing bits. */
(function(root){'use strict';
 const P=root.HarvesterVesselPipeV12, I=root.HarvesterIntegrityV13;
 const LANES=['A','B'],VERSION='14.0-independent-software-paths';
 const valid=hex=>typeof hex==='string'&&/^[0-9A-F]{10}$/.test(hex);
 const configDefaults=()=>({delayA:2,delayB:6,modeA:'NORMAL',modeB:'NORMAL',bitA:17,bitB:17});
 const newPath=id=>({id,attempt:0,bytes:[null,null,null,null,null],queue:[],status:'EMPTY',sentAt:null,rxHex:null});
 const defaults=()=>({version:VERSION,reference:null,txSource:null,paths:{A:newPath('A'),B:newPath('B')},tick:0,seq:0,receipts:[],egressReceipt:null,reason:'AWAIT 1 IN · NO PATH PACKETS'});
 const copy=s=>({ ...s, paths:{A:{...s.paths.A,bytes:[...s.paths.A.bytes],queue:s.paths.A.queue.map(x=>({...x}))},B:{...s.paths.B,bytes:[...s.paths.B.bytes],queue:s.paths.B.queue.map(x=>({...x}))}},receipts:[...s.receipts] });
 function receipt(s,kind,tick,lane,extra={}){
  const seq=s.seq+1,prev=s.receipts.at(-1)?.hash||'00000000';
  const raw={seq,kind,tick, lane,prev,...extra};raw.hash=P.checksum(JSON.stringify(raw));
  s.receipts.push(raw);if(s.receipts.length>128)s.receipts.shift();s.seq=seq;return s;
 }
 function pathConfig(c,lane){const delay=Number(c['delay'+lane]),bit=Number(c['bit'+lane]),mode=c['mode'+lane];
  if(!Number.isInteger(delay)||delay<1||delay>32)throw Error('delay '+lane+' must be 1..32 ticks');
  if(!Number.isInteger(bit)||bit<0||bit>39)throw Error('fault bit '+lane+' must be 0..39');
  if(!['NORMAL','DROP','FLIP'].includes(mode))throw Error('mode '+lane+' is invalid');
  return {delay,bit,mode};}
 function queue(s,lane,tick,config){
  const c=pathConfig(config,lane),p=s.paths[lane],attempt=p.attempt+1,source=s.txSource;
  if(!valid(source))throw Error('sender source unavailable');
  const sourceBytes=Array.from({length:5},(_,i)=>parseInt(source.slice(i*2,i*2+2),16));
  p.attempt=attempt;p.sentAt=tick;p.bytes=[null,null,null,null,null];p.rxHex=null;p.status='IN_FLIGHT';
  p.queue=sourceBytes.map((byte,index)=>({index,byte,at:tick+c.delay+index,attempt,action:c.mode!=='NORMAL'&&Math.floor(c.bit/8)===index?c.mode:'NORMAL',bit:c.bit}));
  receipt(s,attempt===1?'SEND':'RETRANSMIT',tick,lane,{attempt,delay:c.delay,mode:c.mode,bytes:5});
 }
 function start(s,hex,tick,config=configDefaults()){
  if(s.reference!==null)throw Error('only one outstanding register per transport epoch');
  if(!valid(hex))throw Error('exact 40-bit uppercase source required');
  const x=copy(s);x.reference=hex;x.txSource=hex;x.tick=tick;x.egressReceipt=null;
  for(const lane of LANES)queue(x,lane,tick,config);
  x.reason='10 BYTE PACKETS QUEUED OVER TWO DISTINCT SOFTWARE PATHS';return x;
 }
 function advance(s,tick){
  if(!Number.isInteger(tick)||tick<s.tick)throw Error('transport tick must be monotonic');
  if(!s.reference)return s;
  const x=copy(s);x.tick=tick;
  for(const lane of LANES){const p=x.paths[lane];if(!p.queue.length)continue;
   const due=p.queue.filter(q=>q.at<=tick),remaining=p.queue.filter(q=>q.at>tick);
   for(const q of due){
    if(q.attempt!==p.attempt)continue;
    if(q.action==='DROP'){receipt(x,'DROPPED',q.at,lane,{attempt:q.attempt,index:q.index});continue;}
    let byte=q.byte;
    if(q.action==='FLIP'){const byteBit=q.bit%8;byte^=(1<<(7-byteBit));}
    p.bytes[q.index]=byte;
    receipt(x,q.action==='FLIP'?'CORRUPTED':'DELIVERED',q.at,lane,{attempt:q.attempt,index:q.index,byte:byte.toString(16).toUpperCase().padStart(2,'0')});
   }
   p.queue=remaining;
   const complete=p.bytes.every(v=>v!==null);
   p.rxHex=complete?p.bytes.map(v=>v.toString(16).toUpperCase().padStart(2,'0')).join(''):null;
   p.status=complete?(p.rxHex===x.reference?'VERIFIED':'CORRUPT'):(p.queue.length?'IN_FLIGHT':'MISSING_BYTES');
  }
  x.reason=x.paths.A.status+' / '+x.paths.B.status;return x;
 }
 function evaluate(s){
  const a=s.paths.A,b=s.paths.B;
  const exactA=a.status==='VERIFIED'&&a.rxHex===s.reference;
  const exactB=b.status==='VERIFIED'&&b.rxHex===s.reference;
  return {ready:!!s.reference&&exactA&&exactB,source:s.reference,receivedA:a.rxHex,receivedB:b.rxHex,
   completeA:a.bytes.every(v=>v!==null),completeB:b.bytes.every(v=>v!==null),
   bitsA:a.bytes.filter(v=>v!==null).length*8,bitsB:b.bytes.filter(v=>v!==null).length*8,
   errorsA:a.rxHex?I.diff(I.bits(s.reference),I.bits(a.rxHex)).length:null,
   errorsB:b.rxHex?I.diff(I.bits(s.reference),I.bits(b.rxHex)).length:null,
   senderRetained:valid(s.txSource),reason:s.reason};
 }
 function retry(s,lane,tick,config=configDefaults()){
  if(!LANES.includes(lane))throw Error('unknown lane');
  if(!Number.isInteger(tick)||tick<s.tick)throw Error('non-monotonic retry');
  const x=advance(s,tick);
  if(x.egressReceipt){receipt(x,'RETRY_DENIED',tick,lane,{reason:'ONE OUTPUT ALREADY VERIFIED'});return x;}
  if(!valid(x.txSource)){receipt(x,'RETRY_DENIED',tick,lane,{reason:'SENDER SOURCE DISCARDED · NO RECONSTRUCTION'});x.reason='NO SOURCE: CANNOT RESTORE MISSING BYTES';return x;}
  queue(x,lane,tick,config);x.reason='EXPLICIT RETRANSMISSION '+lane+' ATTEMPT '+x.paths[lane].attempt;return x;
 }
 function discardSender(s,tick){const x=advance(s,tick);x.txSource=null;receipt(x,'SOURCE_DISCARDED',tick,'SOURCE',{reason:'RETRIES IMPOSSIBLE WITHOUT RETAINED SENDER'});x.reason='SENDER SOURCE DISCARDED';return x;}
 function confirmOutput(s,tick){const x=advance(s,tick);if(x.egressReceipt)return x;
  if(!evaluate(x).ready){receipt(x,'EGRESS_DENIED',tick,'EXIT',{reason:'DUAL PATH EXACT DELIVERY NOT ESTABLISHED'});return x;}
  const data={source:x.reference,readA:x.paths.A.rxHex,readB:x.paths.B.rxHex,attemptA:x.paths.A.attempt,attemptB:x.paths.B.attempt,bitCount:40};
  receipt(x,'VERIFIED_EGRESS',tick,'EXIT',data);x.egressReceipt={tick,...data};x.reason='TWO DISTINCT PACKET QUEUES VERIFIED · 40/40 EGRESS';return x;
 }
 function abort(s,tick){const x=advance(s,tick);for(const lane of LANES){x.paths[lane].queue=[];if(x.paths[lane].status==='IN_FLIGHT')x.paths[lane].status='ABORTED';}receipt(x,'ABORT',tick,'PIPE',{reason:'NO OUTPUT'});return x;}
 root.HarvesterDualPathV14={VERSION,LANES,configDefaults,defaults,start,advance,evaluate,retry,discardSender,confirmOutput,abort};
})(typeof window!=='undefined'?window:globalThis);
