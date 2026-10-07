
const fs=require('fs');
const bytes=fs.readFileSync('/mnt/data/ringyboxy_kernel_v10.wasm');
function rng(seed){let x=seed>>>0;return()=>{x^=x<<13;x>>>=0;x^=x>>>17;x>>>=0;x^=x<<5;x>>>=0;return x>>>0;};}
(async()=>{
 const mod=await WebAssembly.instantiate(bytes,{}); const w=mod.instance.exports; let pass=0;
 const A={m:1,s:101,c:1,t:0xA001},B={m:1,s:102,c:2,t:0xB002};
 A.x=w.make_crc(A.m,A.s,A.c,A.t)>>>0; B.x=w.make_crc(B.m,B.s,B.c,B.t)>>>0;

 w.reset(); if(w.unsafe_restore_one(A.m,A.s,A.c,A.t,A.x)!==1)throw Error('A unsafe fail'); const l=w.child_state();
 w.reset(); if(w.unsafe_restore_one(B.m,B.s,B.c,B.t,B.x)!==1)throw Error('B unsafe fail'); const r=w.child_state();
 if(l===r)throw Error('split not reproduced'); pass++;

 if(w.strict_restore_pair(A.m,A.s,A.c,A.t,A.x,B.m,B.s,B.c,B.t,B.x)!==0)throw Error('strict opened');
 if(w.open_state()!==0||w.conflict_state()!==1)throw Error('hold missing');
 if(w.try_commit(1,A.t)!==0||w.try_commit(2,B.t)!==0)throw Error('hold escape'); pass++;

 if(w.strict_restore_pair(B.m,B.s,B.c,B.t,B.x,A.m,A.s,A.c,A.t,A.x)!==0)throw Error('reverse opened');
 if(w.open_state()!==0||w.conflict_state()!==1)throw Error('reverse hold missing'); pass++;

 if(w.resolve_exact(A.s,A.c,A.t,A.x)!==1)throw Error('resolve A fail');
 if(w.child_state()!==1||w.txid_state()!==A.t)throw Error('resolved A wrong');
 if(w.try_commit(2,B.t)!==0||w.try_commit(1,A.t)!==1)throw Error('post-resolution wrong'); pass++;

 const D1={m:1,s:201,c:2,t:0xCAFE},D2={m:1,s:202,c:2,t:0xCAFE};
 D1.x=w.make_crc(D1.m,D1.s,D1.c,D1.t)>>>0;D2.x=w.make_crc(D2.m,D2.s,D2.c,D2.t)>>>0;
 if(w.strict_restore_pair(D1.m,D1.s,D1.c,D1.t,D1.x,D2.m,D2.s,D2.c,D2.t,D2.x)!==1)throw Error('duplicate fail');
 if(w.conflict_state()!==0||w.child_state()!==2)throw Error('duplicate state wrong'); pass++;

 const C1={m:1,s:301,c:1,t:0x1111},C2={m:1,s:302,c:1,t:0x2222};
 C1.x=w.make_crc(C1.m,C1.s,C1.c,C1.t)>>>0;C2.x=w.make_crc(C2.m,C2.s,C2.c,C2.t)>>>0;
 if(w.strict_restore_pair(C1.m,C1.s,C1.c,C1.t,C1.x,C2.m,C2.s,C2.c,C2.t,C2.x)!==0)throw Error('same child diff txid opened');
 if(w.conflict_state()!==1||w.open_state()!==0)throw Error('same child conflict missing'); pass++;

 const rounds=800000,rand=rng(0xC0F11C7);
 let unsafe=0,strictOpens=0,holdEsc=0,resolutions=0,loserEsc=0,aCan=0,bCan=0;
 const t0=process.hrtime.bigint();
 for(let i=0;i<rounds;i++){
   const sA=1000+i*2,sB=sA+1,txA=(rand()|1)>>>0; let txB=(rand()|1)>>>0;
   if(txB===txA)txB=((txB^0x10001)>>>0)||3;
   const xA=w.make_crc(1,sA,1,txA)>>>0,xB=w.make_crc(1,sB,2,txB)>>>0;

   w.reset();w.unsafe_restore_one(1,sA,1,txA,xA);const ll=w.child_state();
   w.reset();w.unsafe_restore_one(1,sB,2,txB,xB);const rr=w.child_state();
   if(ll!==rr)unsafe++;

   if(w.strict_restore_pair(1,sA,1,txA,xA,1,sB,2,txB,xB)===1)strictOpens++;
   if(w.try_commit(1,txA)===1||w.try_commit(2,txB)===1)holdEsc++;

   if((rand()&1)===0){
     if(w.resolve_exact(sA,1,txA,xA)===1){resolutions++;aCan++;}
     if(w.try_commit(2,txB)===1)loserEsc++;
   }else{
     if(w.resolve_exact(sB,2,txB,xB)===1){resolutions++;bCan++;}
     if(w.try_commit(1,txA)===1)loserEsc++;
   }

   if(w.strict_restore_pair(1,sB,2,txB,xB,1,sA,1,txA,xA)===1)strictOpens++;
 }
 const seconds=Number(process.hrtime.bigint()-t0)/1e9;
 if(unsafe!==rounds)throw Error(`unsafe=${unsafe}`);
 if(strictOpens!==0)throw Error(`strict opens=${strictOpens}`);
 if(holdEsc!==0)throw Error(`hold escapes=${holdEsc}`);
 if(resolutions!==rounds)throw Error(`resolutions=${resolutions}`);
 if(loserEsc!==0)throw Error(`loser escapes=${loserEsc}`); pass++;

 console.log(`NODE=${process.version}`);
 console.log(`WASM_ENGINE=V8 WebAssembly`);
 console.log(`PASS_ASSERT_GROUPS=${pass}`);
 console.log(`TWO_VALID_RECORD_LOCAL_SELECTION_SPLIT=REPRODUCED`);
 console.log(`STRESS_ROUNDS=${rounds}`);
 console.log(`UNSAFE_DIVERGENT_LOCAL_SELECTIONS=${unsafe}`);
 console.log(`STRICT_CONFLICT_OPENS=${strictOpens}`);
 console.log(`STRICT_COMMITS_DURING_HOLD=${holdEsc}`);
 console.log(`STRICT_EXACT_CANONICAL_RESOLUTIONS=${resolutions}`);
 console.log(`STRICT_LOSER_ESCAPES=${loserEsc}`);
 console.log(`A_CANONICAL=${aCan}`);
 console.log(`B_CANONICAL=${bCan}`);
 console.log(`SECONDS=${seconds.toFixed(6)}`);
 console.log(`ROUNDS_PER_SEC=${Math.round(rounds/seconds)}`);
 console.log(`RESULT=xe / INDIVIDUAL RECORD VALIDITY AS AUTHORITY FAIL`);
 console.log(`RESULT2=0e / CONFLICT HOLD + EXACT CANONICAL RESOLUTION PASS`);
})();
