/* Harvester v15: receiver-originated software acknowledgements; model, not secure network hardware.
   Every packet/ACK identifies its transmission, lane, attempt, byte index, and delivered value.
   Wire queues retain late packets across retry and transfer reset. No source reconstruction. */
(function(root){'use strict';
 const P=root.HarvesterVesselPipeV12,I=root.HarvesterIntegrityV13;
 const LANES=Object.freeze(['A','B']),VERSION='15.0-sequenced-packet-ack';
 const valid=hex=>typeof hex==='string'&&/^[0-9A-F]{10}$/.test(hex);
 const configDefaults=()=>({delayA:2,delayB:6,modeA:'NORMAL',modeB:'NORMAL',bitA:17,bitB:29,ackModeA:'NORMAL',ackModeB:'NORMAL'});
 const freshPath=id=>({id,attempt:0,bytes:[null,null,null,null,null],acked:[false,false,false,false,false],queue:[],status:'EMPTY',sentAt:null,rxHex:null,seen:[],lastAccepted:null});
 const defaults=()=>({version:VERSION,nextTransferId:1,txId:null,reference:null,txSource:null,paths:{A:freshPath('A'),B:freshPath('B')},wire:[],ackWire:[],tick:0,seq:0,receipts:[],egressReceipt:null,aborted:false,reason:'AWAIT 1 IN · NO ACKNOWLEDGED PACKETS'});
 const copy=s=>({...s,paths:{A:{...s.paths.A,bytes:[...s.paths.A.bytes],acked:[...s.paths.A.acked],queue:s.paths.A.queue.map(q=>({...q})),seen:[...s.paths.A.seen],lastAccepted:s.paths.A.lastAccepted?{...s.paths.A.lastAccepted}:null},B:{...s.paths.B,bytes:[...s.paths.B.bytes],acked:[...s.paths.B.acked],queue:s.paths.B.queue.map(q=>({...q})),seen:[...s.paths.B.seen],lastAccepted:s.paths.B.lastAccepted?{...s.paths.B.lastAccepted}:null}},wire:s.wire.map(q=>({...q})),ackWire:s.ackWire.map(q=>({...q})),receipts:[...s.receipts]});
 function receipt(s,kind,tick,lane,extra={}){const seq=s.seq+1,prev=s.receipts.at(-1)?.hash||'00000000';const raw={seq,kind,tick,lane,prev,...extra};raw.hash=P.checksum(JSON.stringify(raw));s.receipts.push(raw);if(s.receipts.length>192)s.receipts.shift();s.seq=seq;return raw;}
 function config(c,lane){const delay=Number(c['delay'+lane]),bit=Number(c['bit'+lane]),mode=c['mode'+lane],ackMode=c['ackMode'+lane]||'NORMAL';if(!Number.isInteger(delay)||delay<1||delay>32)throw Error('delay must be 1..32');if(!Number.isInteger(bit)||bit<0||bit>39)throw Error('fault bit must be 0..39');if(!['NORMAL','DROP','FLIP'].includes(mode))throw Error('invalid path mode');if(!['NORMAL','DROP_ONE'].includes(ackMode))throw Error('invalid acknowledgement mode');return {delay,bit,mode,ackMode};}
 function schedule(s,lane,tick,c){const p=s.paths[lane],param=config(c,lane),source=s.txSource;
  if(!valid(source))throw Error('sender copy unavailable');const attempt=p.attempt+1;
  p.attempt=attempt;p.bytes=[null,null,null,null,null];p.acked=[false,false,false,false,false];p.seen=[];p.queue=[];p.rxHex=null;p.sentAt=tick;p.status='IN_FLIGHT';p.lastAccepted=null;
  for(let index=0;index<5;index++){
   const original=parseInt(source.slice(index*2,index*2+2),16);
   const action=param.mode!=='NORMAL'&&Math.floor(param.bit/8)===index?param.mode:'NORMAL';
   const q={txId:s.txId,lane,attempt,index,original,at:tick+param.delay+index,action,bit:param.bit,ackDrop:param.ackMode==='DROP_ONE'&&index===2};
   s.wire.push(q);p.queue.push(q);
  }
  receipt(s,attempt===1?'SEND':'RETRANSMIT',tick,lane,{txId:s.txId,attempt,delay:param.delay,mode:param.mode,ackMode:param.ackMode,packets:5});
 }
 function reset(s,tick=s.tick){const x=copy(s);if(!Number.isInteger(tick)||tick<x.tick)throw Error('clock cannot go backward');
  x.tick=tick;x.txId=null;x.reference=null;x.txSource=null;x.paths={A:freshPath('A'),B:freshPath('B')};x.egressReceipt=null;x.aborted=false;x.reason='AWAIT NEW TRANSMISSION · STALE WIRE FRAMES ARE NOT ACCEPTED';receipt(x,'EPOCH_RESET',tick,'CONTROL',{nextTransferId:x.nextTransferId});return x;}
 function start(s,hex,tick,c=configDefaults()){
  if(s.reference!==null)throw Error('one outstanding register per epoch');if(!valid(hex))throw Error('40-bit uppercase hex required');
  if(!Number.isInteger(tick)||tick<s.tick)throw Error('monotonic tick required');
  const x=copy(s);x.txId=x.nextTransferId++;x.reference=hex;x.txSource=hex;x.tick=tick;x.egressReceipt=null;x.aborted=false;
  for(const lane of LANES)schedule(x,lane,tick,c);x.reason='TRANSFER '+x.txId+' · A/B FRAMES IN FLIGHT · AWAIT ACKS';return x;
 }
 const packetKey=q=>[q.txId,q.lane,q.attempt,q.index].join(':');
 function advance(s,tick){if(!Number.isInteger(tick)||tick<s.tick)throw Error('clock cannot go backward');const x=copy(s);x.tick=tick;
  const due=x.wire.filter(q=>q.at<=tick).sort((a,b)=>a.at-b.at||a.txId-b.txId||a.lane.localeCompare(b.lane)||a.index-b.index);
  x.wire=x.wire.filter(q=>q.at>tick);
  for(const q of due){const p=x.paths[q.lane],tag={txId:q.txId,attempt:q.attempt,index:q.index};
   if(x.aborted||q.txId!==x.txId||q.attempt!==p.attempt){receipt(x,'STALE_PACKET_REJECTED',q.at,q.lane,{...tag,reason:'TX OR ATTEMPT DOES NOT MATCH CURRENT RECEIVER'});continue;}
   const key=packetKey(q);if(p.seen.includes(key)){receipt(x,'REPLAY_PACKET_REJECTED',q.at,q.lane,tag);continue;}
   p.seen.push(key);p.queue=p.queue.filter(r=>r.index!==q.index||r.attempt!==q.attempt);
   if(q.action==='DROP'){receipt(x,'DROPPED',q.at,q.lane,tag);continue;}
   const received=q.action==='FLIP'?(q.original^(1<<(7-q.bit%8))):q.original;
   p.bytes[q.index]=received;p.lastAccepted={...q,action:'NORMAL',at:q.at,received};
   receipt(x,q.action==='FLIP'?'CORRUPTED':'DELIVERED',q.at,q.lane,{...tag,byte:received.toString(16).padStart(2,'0').toUpperCase()});
   const ack={txId:q.txId,lane:q.lane,attempt:q.attempt,index:q.index,received,at:q.at+2};
   if(q.ackDrop){receipt(x,'ACK_LOST',q.at,q.lane,tag);}
   else {x.ackWire.push(ack);receipt(x,'ACK_SENT',q.at,q.lane,{...tag,arrives:ack.at});}
  }
  const ackDue=x.ackWire.filter(a=>a.at<=tick).sort((a,b)=>a.at-b.at||a.txId-b.txId||a.index-b.index);
  x.ackWire=x.ackWire.filter(a=>a.at>tick);
  for(const a of ackDue){const p=x.paths[a.lane],tag={txId:a.txId,attempt:a.attempt,index:a.index};
   if(x.aborted||a.txId!==x.txId||a.attempt!==p.attempt){receipt(x,'STALE_ACK_REJECTED',a.at,a.lane,tag);continue;}
   if(p.acked[a.index]){receipt(x,'DUPLICATE_ACK_REJECTED',a.at,a.lane,tag);continue;}
   if(p.bytes[a.index]===null||p.bytes[a.index]!==a.received){receipt(x,'INVALID_ACK_REJECTED',a.at,a.lane,tag);continue;}
   p.acked[a.index]=true;receipt(x,'ACK_ACCEPTED',a.at,a.lane,{...tag,byte:a.received.toString(16).padStart(2,'0').toUpperCase()});
  }
  for(const lane of LANES){const p=x.paths[lane],complete=p.bytes.every(v=>v!==null),allAcks=p.acked.every(Boolean);
   p.rxHex=complete?p.bytes.map(v=>v.toString(16).padStart(2,'0').toUpperCase()).join(''):null;
   p.status=complete&&!allAcks?'AWAIT_ACK':complete?(p.rxHex===x.reference?'VERIFIED':'CORRUPT'):(p.queue.length?'IN_FLIGHT':p.attempt?'MISSING_BYTES':'EMPTY');
  }
  x.reason=x.txId===null?'AWAIT NEW TRANSFER':('TX '+x.txId+' · '+x.paths.A.status+' / '+x.paths.B.status);return x;
 }
 function evaluate(s){const a=s.paths.A,b=s.paths.B,exactA=a.status==='VERIFIED'&&a.rxHex===s.reference&&a.acked.every(Boolean),exactB=b.status==='VERIFIED'&&b.rxHex===s.reference&&b.acked.every(Boolean);
  return {ready:!s.aborted&&s.reference!==null&&exactA&&exactB,txId:s.txId,source:s.reference,receivedA:a.rxHex,receivedB:b.rxHex,completeA:a.bytes.every(v=>v!==null),completeB:b.bytes.every(v=>v!==null),bitsA:a.bytes.filter(v=>v!==null).length*8,bitsB:b.bytes.filter(v=>v!==null).length*8,acksA:a.acked.filter(Boolean).length,acksB:b.acked.filter(Boolean).length,errorsA:a.rxHex?I.diff(I.bits(s.reference),I.bits(a.rxHex)).length:null,errorsB:b.rxHex?I.diff(I.bits(s.reference),I.bits(b.rxHex)).length:null,senderRetained:valid(s.txSource),reason:s.reason};
 }
 function retry(s,lane,tick,c=configDefaults()){if(!LANES.includes(lane))throw Error('invalid lane');const x=advance(s,tick);if(x.aborted){receipt(x,'RETRY_DENIED',tick,lane,{reason:'ABORTED TRANSMISSION'});return x;}if(x.egressReceipt){receipt(x,'RETRY_DENIED',tick,lane,{reason:'OUTPUT ALREADY CONFIRMED'});return x;}if(!valid(x.txSource)){receipt(x,'RETRY_DENIED',tick,lane,{reason:'SENDER SOURCE NOT RETAINED'});return x;}
  schedule(x,lane,tick,c);x.reason='TX '+x.txId+' RETRY '+lane+' ATTEMPT '+x.paths[lane].attempt+' · OLD WIRE REMAINS IN FLIGHT';return x;}
 function discardSender(s,tick){const x=advance(s,tick);x.txSource=null;receipt(x,'SOURCE_DISCARDED',tick,'SOURCE');x.reason='SENDER DISCARDED · NO FUTURE RETRY';return x;}
 function replay(s,lane,tick){if(!LANES.includes(lane))throw Error('invalid lane');const x=advance(s,tick),p=x.paths[lane];if(x.aborted||!p.lastAccepted){receipt(x,'REPLAY_DENIED',tick,lane,{reason:'NO PREVIOUS RECEIVED PACKET'});return x;}
  x.wire.push({...p.lastAccepted,at:tick+1});receipt(x,'REPLAY_INJECTED',tick,lane,{txId:p.lastAccepted.txId,attempt:p.lastAccepted.attempt,index:p.lastAccepted.index});return x;}
 function confirmOutput(s,tick){const x=advance(s,tick);if(x.egressReceipt)return x;if(!evaluate(x).ready){receipt(x,'EGRESS_DENIED',tick,'EXIT',{reason:'WAIT FOR CURRENT TRANSFER, ALL ACKS AND EXACT REGISTER'});return x;}
  const info={txId:x.txId,source:x.reference,readA:x.paths.A.rxHex,readB:x.paths.B.rxHex,attemptA:x.paths.A.attempt,attemptB:x.paths.B.attempt,acksA:5,acksB:5,bitCount:40};receipt(x,'VERIFIED_EGRESS',tick,'EXIT',info);x.egressReceipt={tick,...info};x.reason='ONE VERIFIED EGRESS · TX '+x.txId+' WITH TEN CURRENT ACKS';return x;}
 function abort(s,tick){const x=advance(s,tick);x.txSource=null;x.aborted=true;for(const lane of LANES)if(x.paths[lane].status!=='VERIFIED')x.paths[lane].status='ABORTED';receipt(x,'ABORT',tick,'PIPE',{txId:x.txId});return x;}
 root.HarvesterSequencedTransportV15={VERSION,LANES,configDefaults,defaults,reset,start,advance,evaluate,retry,discardSender,replay,confirmOutput,abort};
})(typeof window!=='undefined'?window:globalThis);
