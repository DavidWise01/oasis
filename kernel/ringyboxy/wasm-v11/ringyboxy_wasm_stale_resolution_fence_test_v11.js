
const fs=require('fs');
const bytes=fs.readFileSync('/mnt/data/ringyboxy_kernel_v11.wasm');

function rng(seed){
  let x=seed>>>0;
  return()=>{x^=x<<13;x>>>=0;x^=x>>>17;x>>>=0;x^=x<<5;x>>>=0;return x>>>0;};
}

(async()=>{
  const mod=await WebAssembly.instantiate(bytes,{});
  const w=mod.instance.exports;
  let pass=0;

  const A={s:101,c:1,t:0xA001},B={s:102,c:2,t:0xB002};
  A.x=w.make_crc(1,A.s,A.c,A.t)>>>0;
  B.x=w.make_crc(1,B.s,B.c,B.t)>>>0;

  // 1. Unsafe: prepare A under fence N, roll to N+1, stale resolution still installs.
  w.reset();
  w.install_fence(10,0xAAA00010);
  if(w.load_conflict_pair(A.s,A.c,A.t,A.x,B.s,B.c,B.t,B.x)!==1)throw Error('conflict load failed');
  if(w.prepare_resolution(A.s,A.c,A.t,A.x)!==1)throw Error('prepare A failed');
  w.install_fence(11,0xBBB00011);
  if(w.unsafe_install_resolution()!==1||w.child_state()!==1)
    throw Error('unsafe stale-resolution exploit not reproduced');
  pass++;

  // 2. Strict: epoch rollover blocks stale prepared resolution and stays HOLD.
  w.reset();
  w.install_fence(20,0xAAA00020);
  w.load_conflict_pair(A.s,A.c,A.t,A.x,B.s,B.c,B.t,B.x);
  w.prepare_resolution(A.s,A.c,A.t,A.x);
  w.install_fence(21,0xBBB00021);

  if(w.strict_install_resolution()!==0)throw Error('stale epoch resolution installed');
  if(w.open_state()!==0||w.conflict_state()!==1||w.prepared_state()!==0)
    throw Error('stale epoch did not remain held');
  if(w.try_commit(1,A.t)!==0||w.try_commit(2,B.t)!==0)
    throw Error('commit escaped stale-resolution hold');
  pass++;

  // 3. Same epoch, changed digest also invalidates prepared resolution.
  w.reset();
  w.install_fence(30,0x11112222);
  w.load_conflict_pair(A.s,A.c,A.t,A.x,B.s,B.c,B.t,B.x);
  w.prepare_resolution(B.s,B.c,B.t,B.x);
  w.install_fence(30,0x33334444);

  if(w.strict_install_resolution()!==0)
    throw Error('same-epoch stale digest resolution installed');
  if(w.open_state()!==0||w.conflict_state()!==1)
    throw Error('digest rollover did not hold');
  pass++;

  // 4. Reissue resolution under current fence succeeds.
  if(w.prepare_resolution(B.s,B.c,B.t,B.x)!==1)
    throw Error('fresh B resolution prepare failed');
  if(w.strict_install_resolution()!==1||w.child_state()!==2||w.open_state()!==1)
    throw Error('fresh B resolution install failed');
  if(w.try_commit(1,A.t)!==0||w.try_commit(2,B.t)!==1)
    throw Error('post-resolution state wrong');
  pass++;

  // 5. Exact record binding: a fabricated winner not in stored conflict cannot prepare.
  w.reset();
  w.install_fence(40,0x44440040);
  w.load_conflict_pair(A.s,A.c,A.t,A.x,B.s,B.c,B.t,B.x);
  const fakeS=999,fakeC=1,fakeT=0xFA11;
  const fakeX=w.make_crc(1,fakeS,fakeC,fakeT)>>>0;
  if(w.prepare_resolution(fakeS,fakeC,fakeT,fakeX)!==0)
    throw Error('fabricated resolution prepared');
  pass++;

  const rounds=900000,rand=rng(0x11FECE55);
  let unsafeStaleInstalls=0,strictStaleInstalls=0,strictHoldEscapes=0;
  let strictFreshInstalls=0,strictLoserEscapes=0;
  let epochRollovers=0,digestRollovers=0,aFinal=0,bFinal=0;

  const t0=process.hrtime.bigint();

  for(let i=0;i<rounds;i++){
    const sA=1000+i*2,sB=sA+1;
    const tA=(rand()|1)>>>0;
    let tB=(rand()|1)>>>0;
    if(tB===tA)tB=((tB^0x10101)>>>0)||3;
    const xA=w.make_crc(1,sA,1,tA)>>>0;
    const xB=w.make_crc(1,sB,2,tB)>>>0;

    const baseEpoch=100+(rand()%1000000);
    const baseDigest=(0xA5000000^rand())>>>0;
    const mode=rand()&1;
    const nextEpoch=mode===0?baseEpoch+1:baseEpoch;
    const nextDigest=(baseDigest^(mode===0?0x01010101:0x00010001))>>>0;
    if(mode===0)epochRollovers++;else digestRollovers++;

    const chooseA=(rand()&1)===0;
    const ws=chooseA?sA:sB,wc=chooseA?1:2,wt=chooseA?tA:tB,wx=chooseA?xA:xB;
    const loserC=chooseA?2:1,loserT=chooseA?tB:tA;

    // Unsafe stale install.
    w.reset();
    w.install_fence(baseEpoch,baseDigest);
    w.load_conflict_pair(sA,1,tA,xA,sB,2,tB,xB);
    if(w.prepare_resolution(ws,wc,wt,wx)!==1)throw Error('unsafe prepare failed');
    w.install_fence(nextEpoch,nextDigest);
    if(w.unsafe_install_resolution()===1)unsafeStaleInstalls++;

    // Strict stale install must fail and remain held.
    w.reset();
    w.install_fence(baseEpoch,baseDigest);
    w.load_conflict_pair(sA,1,tA,xA,sB,2,tB,xB);
    if(w.prepare_resolution(ws,wc,wt,wx)!==1)throw Error('strict prepare failed');
    w.install_fence(nextEpoch,nextDigest);

    if(w.strict_install_resolution()===1)strictStaleInstalls++;
    if(w.try_commit(wc,wt)===1||w.try_commit(loserC,loserT)===1)strictHoldEscapes++;

    // Reissued exact resolution under current fence must install.
    if(w.prepare_resolution(ws,wc,wt,wx)!==1)throw Error('fresh prepare failed');
    if(w.strict_install_resolution()===1){
      strictFreshInstalls++;
      if(wc===1)aFinal++;else bFinal++;
    }
    if(w.try_commit(loserC,loserT)===1)strictLoserEscapes++;
  }

  const seconds=Number(process.hrtime.bigint()-t0)/1e9;

  if(unsafeStaleInstalls!==rounds)throw Error(`unsafe stale=${unsafeStaleInstalls}`);
  if(strictStaleInstalls!==0)throw Error(`strict stale=${strictStaleInstalls}`);
  if(strictHoldEscapes!==0)throw Error(`hold escapes=${strictHoldEscapes}`);
  if(strictFreshInstalls!==rounds)throw Error(`fresh installs=${strictFreshInstalls}`);
  if(strictLoserEscapes!==0)throw Error(`loser escapes=${strictLoserEscapes}`);

  pass++;

  console.log(`NODE=${process.version}`);
  console.log(`WASM_ENGINE=V8 WebAssembly`);
  console.log(`PASS_ASSERT_GROUPS=${pass}`);
  console.log(`STALE_CONFLICT_RESOLUTION_FENCE=REPRODUCED`);
  console.log(`STRESS_ROUNDS=${rounds}`);
  console.log(`EPOCH_ROLLOVERS=${epochRollovers}`);
  console.log(`DIGEST_ONLY_ROLLOVERS=${digestRollovers}`);
  console.log(`UNSAFE_STALE_RESOLUTION_INSTALLS=${unsafeStaleInstalls}`);
  console.log(`STRICT_STALE_RESOLUTION_INSTALLS=${strictStaleInstalls}`);
  console.log(`STRICT_COMMITS_DURING_HOLD=${strictHoldEscapes}`);
  console.log(`STRICT_FRESH_RESOLUTION_INSTALLS=${strictFreshInstalls}`);
  console.log(`STRICT_LOSER_ESCAPES=${strictLoserEscapes}`);
  console.log(`A_FINAL=${aFinal}`);
  console.log(`B_FINAL=${bFinal}`);
  console.log(`SECONDS=${seconds.toFixed(6)}`);
  console.log(`ROUNDS_PER_SEC=${Math.round(rounds/seconds)}`);
  console.log(`RESULT=xe / TIMELESS CONFLICT-RESOLUTION AUTHORITY FAIL`);
  console.log(`RESULT2=0e / EXACT RESOLUTION + CURRENT FENCE INSTALL PASS`);
})();
