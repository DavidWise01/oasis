
const fs=require('fs');
const bytes=fs.readFileSync('/mnt/data/ringyboxy_kernel_v14.wasm');
const u=x=>x>>>0;
function rng(seed){let x=seed>>>0;return()=>{x^=x<<13;x>>>=0;x^=x>>>17;x>>>=0;x^=x<<5;x>>>=0;return x>>>0;};}

(async()=>{
 const mod=await WebAssembly.instantiate(bytes,{}),w=mod.instance.exports; let pass=0;
 const prev=0x0BADBEEF>>>0,epoch=100;
 const A={m:1,e:epoch,p:prev,c:1,t:0xA14001},B={m:1,e:epoch,p:prev,c:2,t:0xB14002};
 A.d=u(w.make_digest(A.m,A.e,A.p,A.c,A.t));B.d=u(w.make_digest(B.m,B.e,B.p,B.c,B.t));

 // 1. Unsafe local self-validity splits.
 w.reset(); if(w.unsafe_restore_one(A.m,A.e,A.p,A.c,A.t,A.d)!==1)throw Error('unsafe A'); const l=w.child_state();
 w.reset(); if(w.unsafe_restore_one(B.m,B.e,B.p,B.c,B.t,B.d)!==1)throw Error('unsafe B'); const r=w.child_state();
 if(l===r)throw Error('unsafe latest split missing'); pass++;

 // 2. Strict same-lineage, same-epoch distinct snapshots => HOLD.
 if(w.strict_restore_pair(epoch,prev,
   A.m,A.e,A.p,A.c,A.t,A.d,
   B.m,B.e,B.p,B.c,B.t,B.d)!==0)throw Error('strict pair opened');
 if(w.open_state()!==0||w.conflict_state()!==1)throw Error('strict pair not HOLD');
 if(w.try_replay(A.c,A.t,A.d)!==0||w.try_replay(B.c,B.t,B.d)!==0)throw Error('replay escaped HOLD');
 pass++;

 // 3. Input order cannot select a winner.
 if(w.strict_restore_pair(epoch,prev,
   B.m,B.e,B.p,B.c,B.t,B.d,
   A.m,A.e,A.p,A.c,A.t,A.d)!==0)throw Error('reverse pair opened');
 if(w.open_state()!==0||w.conflict_state()!==1)throw Error('reverse pair not HOLD'); pass++;

 // 4. Exact canonical digest resolves; loser cannot replay.
 if(w.resolve_exact_digest(A.d)!==1)throw Error('resolve A failed');
 if(w.child_state()!==1||u(w.txid_state())!==u(A.t)||u(w.digest_state())!==A.d)throw Error('A state wrong');
 if(w.try_replay(A.c,A.t,A.d)!==1||w.try_replay(B.c,B.t,B.d)!==0)throw Error('post resolve replay wrong');
 pass++;

 // 5. Higher epoch alone does not win if it does not occupy expected next slot.
 const H={m:1,e:epoch+1,p:prev,c:2,t:0xB14111};
 H.d=u(w.make_digest(H.m,H.e,H.p,H.c,H.t));
 if(w.strict_restore_pair(epoch,prev,
   H.m,H.e,H.p,H.c,H.t,H.d,
   0,0,0,0,0,0)!==0)throw Error('skipped higher epoch accepted');
 if(w.open_state()!==0)throw Error('higher-epoch gap opened'); pass++;

 // 6. Wrong previous digest blocks even with valid checksum.
 const W={m:1,e:epoch,p:0xC0FFEE01>>>0,c:1,t:0xA14222};
 W.d=u(w.make_digest(W.m,W.e,W.p,W.c,W.t));
 if(w.strict_restore_pair(epoch,prev,
   W.m,W.e,W.p,W.c,W.t,W.d,
   0,0,0,0,0,0)!==0)throw Error('wrong lineage accepted');
 pass++;

 // 7. Exact semantic duplicate is idempotent.
 const D1={m:1,e:epoch,p:prev,c:2,t:0xD00D};
 D1.d=u(w.make_digest(D1.m,D1.e,D1.p,D1.c,D1.t));
 if(w.strict_restore_pair(epoch,prev,
   D1.m,D1.e,D1.p,D1.c,D1.t,D1.d,
   D1.m,D1.e,D1.p,D1.c,D1.t,D1.d)!==1)throw Error('duplicate failed');
 if(w.conflict_state()!==0||w.child_state()!==2)throw Error('duplicate state wrong');
 pass++;

 const rounds=1000000,rand=rng(0x14A11CE5);
 let unsafeSplits=0,strictConflictOpens=0,strictHoldEscapes=0,strictResolutions=0,strictLoserReplays=0;
 let higherEpochAccepted=0,wrongPrevAccepted=0,aCan=0,bCan=0;
 const t0=process.hrtime.bigint();

 for(let i=0;i<rounds;i++){
   const p=(rand()|1)>>>0,e=1+(rand()%1000000);
   const tA=(rand()|1)>>>0; let tB=(rand()|1)>>>0;
   if(tB===tA)tB=((tB^0x10001)>>>0)||3;
   const dA=u(w.make_digest(1,e,p,1,tA)),dB=u(w.make_digest(1,e,p,2,tB));

   w.reset();w.unsafe_restore_one(1,e,p,1,tA,dA);const ll=w.child_state();
   w.reset();w.unsafe_restore_one(1,e,p,2,tB,dB);const rr=w.child_state();
   if(ll!==rr)unsafeSplits++;

   if(w.strict_restore_pair(e,p,
      1,e,p,1,tA,dA,
      1,e,p,2,tB,dB)===1)strictConflictOpens++;
   if(w.try_replay(1,tA,dA)===1||w.try_replay(2,tB,dB)===1)strictHoldEscapes++;

   const chooseA=(rand()&1)===0;
   if(w.resolve_exact_digest(chooseA?dA:dB)===1){
      strictResolutions++; if(chooseA)aCan++;else bCan++;
   }
   if(w.try_replay(chooseA?2:1,chooseA?tB:tA,chooseA?dB:dA)===1)strictLoserReplays++;

   const highD=u(w.make_digest(1,e+1,p,1,tA));
   if(w.strict_restore_pair(e,p,1,e+1,p,1,tA,highD,0,0,0,0,0,0)===1)higherEpochAccepted++;

   const badPrev=(p^0x01010101)>>>0;
   const badD=u(w.make_digest(1,e,badPrev,1,tA));
   if(w.strict_restore_pair(e,p,1,e,badPrev,1,tA,badD,0,0,0,0,0,0)===1)wrongPrevAccepted++;
 }
 const sec=Number(process.hrtime.bigint()-t0)/1e9;
 if(unsafeSplits!==rounds)throw Error(`unsafe splits=${unsafeSplits}`);
 if(strictConflictOpens!==0)throw Error(`conflict opens=${strictConflictOpens}`);
 if(strictHoldEscapes!==0)throw Error(`hold escapes=${strictHoldEscapes}`);
 if(strictResolutions!==rounds)throw Error(`resolutions=${strictResolutions}`);
 if(strictLoserReplays!==0)throw Error(`loser replays=${strictLoserReplays}`);
 if(higherEpochAccepted!==0)throw Error(`higher epoch accepted=${higherEpochAccepted}`);
 if(wrongPrevAccepted!==0)throw Error(`wrong prev accepted=${wrongPrevAccepted}`);
 pass++;

 console.log(`NODE=${process.version}`);
 console.log(`WASM_ENGINE=V8 WebAssembly`);
 console.log(`PASS_ASSERT_GROUPS=${pass}`);
 console.log(`DUAL_VALID_LATEST_SNAPSHOT_SPLIT=REPRODUCED`);
 console.log(`STRESS_ROUNDS=${rounds}`);
 console.log(`UNSAFE_DIVERGENT_LATEST_SELECTIONS=${unsafeSplits}`);
 console.log(`STRICT_CONFLICT_OPENS=${strictConflictOpens}`);
 console.log(`STRICT_COMMITS_DURING_HOLD=${strictHoldEscapes}`);
 console.log(`STRICT_EXACT_DIGEST_RESOLUTIONS=${strictResolutions}`);
 console.log(`STRICT_LOSER_REPLAYS=${strictLoserReplays}`);
 console.log(`STRICT_HIGHER_EPOCH_WITHOUT_NEXT_SLOT_ACCEPTS=${higherEpochAccepted}`);
 console.log(`STRICT_WRONG_PREV_DIGEST_ACCEPTS=${wrongPrevAccepted}`);
 console.log(`A_CANONICAL=${aCan}`);
 console.log(`B_CANONICAL=${bCan}`);
 console.log(`SECONDS=${sec.toFixed(6)}`);
 console.log(`ROUNDS_PER_SEC=${Math.round(rounds/sec)}`);
 console.log(`RESULT=xe / SELF-VALID SNAPSHOT AS LATEST AUTHORITY FAIL`);
 console.log(`RESULT2=0e / EXACT-LINEAGE NEXT-SLOT + CONFLICT HOLD PASS`);
})();
