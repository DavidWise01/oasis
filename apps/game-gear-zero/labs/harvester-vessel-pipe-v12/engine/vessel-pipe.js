/* Harvester vessel pipe v12 -- symbolic deterministic experiment; not a physical transfer. */
(function(root){ 'use strict';
  const LITERAL='{{lv > . . . . . > 40 bits > . . . . 2^3 > 1 1 2 4 > 1 in , 1 , out > {{ix2}} , r1,g1,b1,bk1 }}';
  const COLORS=['r1','g1','b1','bk1'],WEIGHTS=[1,1,2,4],STAGES=['lv','5 dots','40 bits','4 dots / 2^3','1 1 2 4','1 in, 1 out','{{ix2}}','r1 g1 b1 bk1'];
  const DEFAULT_HEX='01337AB4FF';
  const checksum=(value)=>{let a=2166136261>>>0;const s=String(value);for(let i=0;i<s.length;i++){a=Math.imul(a^s.charCodeAt(i),16777619)>>>0;}return a.toString(16).padStart(8,'0')};
  function encode(seed){
    if(typeof seed!=='string'||!/^[0-9a-fA-F]{10}$/.test(seed))throw Error('Requires exactly ten hex digits = 40 bits');
    const hex=seed.toUpperCase(),bytes=Array.from({length:5},(_,i)=>parseInt(hex.slice(i*2,i*2+2),16));
    const bitString=bytes.map(v=>v.toString(2).padStart(8,'0')).join('');
    const states=Array.from({length:4},(_,i)=>(bytes[i]^bytes[4])&7);
    const weighted=states.reduce((sum,val,i)=>sum+val*WEIGHTS[i],0);
    const lanes=COLORS.map((name,i)=>({name,state:states[i],bit:states[i]&1,weight:WEIGHTS[i]}));
    const activeLanes=lanes.filter(x=>x.bit).map(x=>x.name);
    return {literal:LITERAL,hex,bytes,bitString,bits:40,dotsIn:5,dotsOut:4,states,statesPerDot:8,projectedBits:12,weights:[...WEIGHTS],weightedChecksum:weighted,lanes,activeLanes,opaqueOperator:'{{ix2}}',digest:checksum(hex+'/'+states.join(',')+'/'+weighted),lossy:true};
  }
  function defaults(){return {phase:'EMPTY',seed:DEFAULT_HEX,packet:null,receipts:[],seq:0,ingress:0,egress:0,inFlight:null,reason:'AWAIT LOAD',version:'12.0-vessel-pipe'};}
  function receipt(state,kind,tick,packet,reason){
    const n=state.seq+1;
    const record={seq:n,kind,tick:Number(tick),packetDigest:packet?.digest||null,prev:state.receipts.at(-1)?.hash||'00000000',reason};
    record.hash=checksum([record.seq,record.kind,record.tick,record.packetDigest,record.prev,record.reason].join('|'));
    return {...state,seq:n,receipts:[...state.receipts,record].slice(-96),reason};
  }
  function guard(witness){return !!(witness&&witness.phase==='SECURED'&&witness.clampAttached&&witness.interlocksReady===true&&witness.docked===true&&!witness.fault);}
  function transition(s,action,{seed=s.seed,tick=0,witness={}}={}){
    let state={...s};
    if(action==='LOAD'){
      if(s.inFlight||s.phase==='HELD')return receipt(state,'REJECT',tick,s.packet,'PIPE OCCUPIED; ABORT REQUIRED');
      let p;try{p=encode(seed)}catch(e){return receipt(state,'REJECT',tick,null,'40-BIT INPUT INVALID')}
      state={...state,phase:'LOADED',seed:p.hex,packet:p,inFlight:null};
      return receipt(state,'LOAD',tick,p,'40-BIT REGISTER LOADED / READ-ONLY PROJECTION');
    }
    if(action==='IN'){
      if(!s.packet||s.phase!=='LOADED')return receipt(state,'REJECT',tick,s.packet,'LOAD FIRST / 1 IN MAX');
      if(!guard(witness))return receipt(state,'BLOCKED',tick,s.packet,'CLAMP / HALL / FORCE INTERLOCK');
      state={...state,phase:'IN_FLIGHT',ingress:s.ingress+1,inFlight:{digest:s.packet.digest,hex:s.packet.hex,inTick:tick}};
      return receipt(state,'IN',tick,s.packet,'ONE REGISTER ENTERED VESSEL PIPE');
    }
    if(action==='OUT'){
      if(!s.inFlight||s.phase!=='IN_FLIGHT')return receipt(state,'REJECT',tick,s.packet,'NO IN-FLIGHT REGISTER');
      if(!guard(witness))return receipt({...state,phase:'HELD'},'HOLD',tick,s.packet,'WITNESS LOST / MUST ABORT OR RESTORE');
      if(s.packet?.digest!==s.inFlight.digest)return receipt({...state,phase:'HELD'},'HOLD',tick,s.packet,'PAYLOAD DIGEST CHANGED');
      state={...state,phase:'COMPLETE',egress:s.egress+1,inFlight:null};
      return receipt(state,'OUT',tick,s.packet,'ONE REGISTER EXITED / RECEIPT MATCH');
    }
    if(action==='MONITOR'){
      if(s.inFlight&&!guard(witness)&&s.phase!=='HELD')return receipt({...state,phase:'HELD'},'HOLD',tick,s.packet,'LIVE INTERLOCK LOST / REGISTER HELD');
      return s;
    }
    if(action==='RESUME'){
      if(s.phase!=='HELD'||!s.inFlight)return receipt(state,'REJECT',tick,s.packet,'NO HELD REGISTER');
      if(!guard(witness))return receipt(state,'BLOCKED',tick,s.packet,'RESTORE ALL INTERLOCKS');
      return receipt({...state,phase:'IN_FLIGHT'},'RESUME',tick,s.packet,'WITNESS RESTORED; OUTPUT PENDING');
    }
    if(action==='ABORT'){
      if(!s.inFlight&&s.phase!=='HELD')return receipt(state,'REJECT',tick,s.packet,'NO IN-FLIGHT REGISTER TO ABORT');
      return receipt({...state,phase:'ABORTED',inFlight:null},'ABORT',tick,s.packet,'MODELED PACKET DISCARDED / NO OUTPUT');
    }
    if(action==='CLEAR'){
      if(s.inFlight)return receipt(state,'REJECT',tick,s.packet,'CANNOT CLEAR OCCUPIED PIPE');
      return {...defaults(),seq:s.seq,receipts:s.receipts,ingress:s.ingress,egress:s.egress,reason:'PIPE READY FOR NEW LOAD'};
    }
    throw Error('Unsupported pipe action: '+action);
  }
  root.HarvesterVesselPipeV12={LITERAL,COLORS,WEIGHTS,STAGES,DEFAULT_HEX,checksum,encode,defaults,transition,guard};
})(typeof window!=='undefined'?window:globalThis);
