
const fs=require('fs');
const bytes=fs.readFileSync('/mnt/data/ringyboxy_kernel_v12.wasm');
const u=x=>x>>>0;
function rng(seed){let x=seed>>>0;return()=>{x^=x<<13;x>>>=0;x^=x>>>17;x>>>=0;x^=x<<5;x>>>=0;return x>>>0;};}

(async()=>{
 const mod=await WebAssembly.instantiate(bytes,{}); const w=mod.instance.exports; let pass=0;
 const A={s:101,c:1,t:0xA001},B={s:102,c:2,t:0xB002};
 A.x=u(w.make_crc(1,A.s,A.c,A.t)); B.x=u(w.make_crc(1,B.s,B.c,B.t));

 w.reset();w.install_fence(10,0xAAA00010);w.load_conflict_pair(A.s,A.c,A.t,A.x,B.s,B.c,B.t,B.x);
 if(w.unsafe_install_packet(A.s,A.c,A.t,A.x,10,0xAAA00010)!==1)throw Error('unsafe A');
 w.install_fence(11,0xBBB00011);
 if(w.unsafe_install_packet(B.s,B.c,B.t,B.x,11,0xBBB00011)!==1||w.child_state()!==2)throw Error('unsafe overwrite');
 pass++;

 w.reset();w.install_fence(20,0xAAA00020);w.load_conflict_pair(A.s,A.c,A.t,A.x,B.s,B.c,B.t,B.x);
 if(w.strict_install_packet(A.s,A.c,A.t,A.x,20,0xAAA00020)!==1)throw Error('strict A');
 w.install_fence(21,0xBBB00021);
 if(w.strict_install_packet(B.s,B.c,B.t,B.x,21,0xBBB00021)!==0)throw Error('B overwrote A');
 if(w.child_state()!==1||u(w.txid_state())!==u(A.t))throw Error('A finality lost'); pass++;

 if(w.strict_install_packet(A.s,A.c,A.t,A.x,21,0xBBB00021)!==1)throw Error('A replay failed');
 if(w.child_state()!==1||u(w.txid_state())!==u(A.t))throw Error('A replay mutated'); pass++;

 const A2={s:103,c:1,t:0xA099}; A2.x=u(w.make_crc(1,A2.s,A2.c,A2.t));
 w.reset();w.install_fence(30,0xCCC00030);w.load_conflict_pair(A.s,A.c,A.t,A.x,A2.s,A2.c,A2.t,A2.x);
 if(w.strict_install_packet(A.s,A.c,A.t,A.x,30,0xCCC00030)!==1)throw Error('A install');
 w.install_fence(31,0xDDD00031);
 if(w.strict_install_packet(A2.s,A2.c,A2.t,A2.x,31,0xDDD00031)!==0)throw Error('same child diff tx overwrite');
 if(u(w.txid_state())!==u(A.t))throw Error('tx finality lost'); pass++;

 if(w.strict_install_packet(A.s,A.c,A.t,A.x,30,0xCCC00030)!==0)throw Error('stale packet accepted'); pass++;

 const rounds=1000000,rand=rng(0x12F1A11D);
 let unsafeOverwrites=0,strictContradictoryOverwrites=0,strictExactReplayFailures=0,strictFinalityLoss=0;
 let epochRollovers=0,digestRollovers=0,aFinal=0,bFinal=0;
 const t0=process.hrtime.bigint();

 for(let i=0;i<rounds;i++){
   const sA=1000+i*2,sB=sA+1;
   const tA=(rand()|1)>>>0; let tB=(rand()|1)>>>0;
   if(tB===tA)tB=((tB^0x10001)>>>0)||3;
   const xA=u(w.make_crc(1,sA,1,tA)),xB=u(w.make_crc(1,sB,2,tB));
   const e0=100+(rand()%1000000),d0=(0xA5000000^rand())>>>0,mode=rand()&1;
   const e1=mode===0?e0+1:e0,d1=(d0^(mode===0?0x01010101:0x00010001))>>>0;
   if(mode===0)epochRollovers++;else digestRollovers++;
   const firstA=(rand()&1)===0;
   const fs=firstA?sA:sB,fc=firstA?1:2,ft=firstA?tA:tB,fx=firstA?xA:xB;
   const ls=firstA?sB:sA,lc=firstA?2:1,lt=firstA?tB:tA,lx=firstA?xB:xA;

   w.reset();w.install_fence(e0,d0);w.load_conflict_pair(sA,1,tA,xA,sB,2,tB,xB);
   if(w.unsafe_install_packet(fs,fc,ft,fx,e0,d0)!==1)throw Error('unsafe first');
   w.install_fence(e1,d1);
   if(w.unsafe_install_packet(ls,lc,lt,lx,e1,d1)===1 && w.child_state()===lc)unsafeOverwrites++;

   w.reset();w.install_fence(e0,d0);w.load_conflict_pair(sA,1,tA,xA,sB,2,tB,xB);
   if(w.strict_install_packet(fs,fc,ft,fx,e0,d0)!==1)throw Error('strict first');
   w.install_fence(e1,d1);
   if(w.strict_install_packet(ls,lc,lt,lx,e1,d1)===1)strictContradictoryOverwrites++;
   if(w.child_state()!==fc || u(w.txid_state())!==u(ft))strictFinalityLoss++;
   if(w.strict_install_packet(fs,fc,ft,fx,e1,d1)!==1)strictExactReplayFailures++;
   if(w.child_state()!==fc || u(w.txid_state())!==u(ft))strictFinalityLoss++;
   if(fc===1)aFinal++;else bFinal++;
 }
 const seconds=Number(process.hrtime.bigint()-t0)/1e9;
 if(unsafeOverwrites!==rounds)throw Error(`unsafe=${unsafeOverwrites}`);
 if(strictContradictoryOverwrites!==0)throw Error(`strict overwrite=${strictContradictoryOverwrites}`);
 if(strictExactReplayFailures!==0)throw Error(`replay failures=${strictExactReplayFailures}`);
 if(strictFinalityLoss!==0)throw Error(`finality loss=${strictFinalityLoss}`);
 pass++;

 console.log(`NODE=${process.version}`);
 console.log(`WASM_ENGINE=V8 WebAssembly`);
 console.log(`PASS_ASSERT_GROUPS=${pass}`);
 console.log(`DELAYED_CONTRADICTORY_RESOLUTION_OVERWRITE=REPRODUCED`);
 console.log(`STRESS_ROUNDS=${rounds}`);
 console.log(`EPOCH_ROLLOVERS=${epochRollovers}`);
 console.log(`DIGEST_ONLY_ROLLOVERS=${digestRollovers}`);
 console.log(`UNSAFE_CONTRADICTORY_OVERWRITES=${unsafeOverwrites}`);
 console.log(`STRICT_CONTRADICTORY_OVERWRITES=${strictContradictoryOverwrites}`);
 console.log(`STRICT_EXACT_REPLAY_FAILURES=${strictExactReplayFailures}`);
 console.log(`STRICT_FINALITY_LOSS=${strictFinalityLoss}`);
 console.log(`A_FINAL=${aFinal}`);
 console.log(`B_FINAL=${bFinal}`);
 console.log(`SECONDS=${seconds.toFixed(6)}`);
 console.log(`ROUNDS_PER_SEC=${Math.round(rounds/seconds)}`);
 console.log(`RESULT=xe / REOPENABLE RESOLVED-PARENT AUTHORITY FAIL`);
 console.log(`RESULT2=0e / MONOTONIC RESOLUTION FINALITY + EXACT REPLAY PASS`);
})();
