
const fs=require('fs');
const bytes=fs.readFileSync('/mnt/data/ringyboxy_kernel_v13.wasm');
const u=x=>x>>>0;
function rng(seed){let x=seed>>>0;return()=>{x^=x<<13;x>>>=0;x^=x>>>17;x>>>=0;x^=x<<5;x>>>=0;return x>>>0;};}

(async()=>{
 const mod=await WebAssembly.instantiate(bytes,{}); const w=mod.instance.exports; let pass=0;
 const E=77,A=1,txA=0xA13A13A1>>>0,dA=u(w.make_digest(1,E,A,txA));

 w.reset();
 if(w.unsafe_restore_child_only(A,txA)!==1)throw Error('unsafe child-only restore');
 if(w.try_commit(2,0xB13B13B1)!==1||w.child_state()!==2)throw Error('exploit not reproduced');
 pass++;

 w.reset();
 if(w.strict_restore_child_only(A,txA)!==0)throw Error('strict child-only opened');
 if(w.open_state()!==0||w.hold_state()!==1)throw Error('strict child-only not HOLD');
 if(w.try_commit(2,0xB13B13B1)!==0)throw Error('sibling escaped HOLD');
 pass++;

 w.reset();
 if(w.strict_restore_snapshot(1,E,A,txA,dA)!==1)throw Error('valid snapshot rejected');
 if(w.child_state()!==A||u(w.txid_state())!==txA||w.epoch_state()!==E)throw Error('restore wrong');
 if(w.try_commit(2,0xB13B13B1)!==0)throw Error('sibling rewrote finality');
 if(w.try_commit(A,txA)!==1)throw Error('exact replay failed');
 pass++;

 w.reset();
 const dm=u(w.make_digest(0,E,A,txA));
 if(w.strict_restore_snapshot(0,E,A,txA,dm)!==0)throw Error('markerless accepted');
 if(w.open_state()!==0||w.hold_state()!==1)throw Error('markerless not HOLD');
 pass++;

 w.reset();
 if(w.strict_restore_snapshot(1,E,A,txA,(dA^0x10001)>>>0)!==0)throw Error('corrupt digest accepted');
 if(w.open_state()!==0||w.hold_state()!==1)throw Error('corrupt not HOLD');
 pass++;

 w.reset();
 if(w.strict_restore_snapshot(1,E,2,0xB13B13B1,dA)!==0)throw Error('mismatched replacement accepted');
 pass++;

 const rounds=1000000,rand=rng(0x13C0A511);
 let unsafe=0,strictChildOpen=0,strictChildEsc=0,valid=0,validSibling=0,corruptOpen=0,a=0,b=0;
 const t0=process.hrtime.bigint();

 for(let i=0;i<rounds;i++){
   const winner=(rand()&1)?1:2,sibling=winner===1?2:1;
   if(winner===1)a++;else b++;
   const tx=(rand()|1)>>>0,sibTx=(rand()|1)>>>0,epoch=1+(rand()%1000000);
   const good=u(w.make_digest(1,epoch,winner,tx));

   w.reset();w.unsafe_restore_child_only(winner,tx);
   if(w.try_commit(sibling,sibTx)===1)unsafe++;

   w.reset();
   if(w.strict_restore_child_only(winner,tx)===1)strictChildOpen++;
   if(w.try_commit(sibling,sibTx)===1)strictChildEsc++;

   w.reset();
   if(w.strict_restore_snapshot(1,epoch,winner,tx,good)===1)valid++;
   if(w.try_commit(sibling,sibTx)===1)validSibling++;

   w.reset();
   const mode=rand()%3;
   let m=1,c=winner,t=tx,d=good;
   if(mode===0)m=0; else if(mode===1)c=sibling; else d=(good^0x01000001)>>>0;
   if(w.strict_restore_snapshot(m,epoch,c,t,d)===1)corruptOpen++;
 }
 const sec=Number(process.hrtime.bigint()-t0)/1e9;
 if(unsafe!==rounds)throw Error(`unsafe=${unsafe}`);
 if(strictChildOpen!==0)throw Error(`child opens=${strictChildOpen}`);
 if(strictChildEsc!==0)throw Error(`child esc=${strictChildEsc}`);
 if(valid!==rounds)throw Error(`valid=${valid}`);
 if(validSibling!==0)throw Error(`valid sibling=${validSibling}`);
 if(corruptOpen!==0)throw Error(`corrupt opens=${corruptOpen}`);
 pass++;

 console.log(`NODE=${process.version}`);
 console.log(`WASM_ENGINE=V8 WebAssembly`);
 console.log(`PASS_ASSERT_GROUPS=${pass}`);
 console.log(`COMPACTION_FINALITY_LOSS=REPRODUCED`);
 console.log(`STRESS_ROUNDS=${rounds}`);
 console.log(`UNSAFE_REOPEN_FORKS=${unsafe}`);
 console.log(`STRICT_CHILD_ONLY_OPENS=${strictChildOpen}`);
 console.log(`STRICT_CHILD_ONLY_SIBLING_ESCAPES=${strictChildEsc}`);
 console.log(`STRICT_VALID_SNAPSHOT_RESTORES=${valid}`);
 console.log(`STRICT_VALID_SNAPSHOT_SIBLING_ESCAPES=${validSibling}`);
 console.log(`STRICT_CORRUPT_SNAPSHOT_OPENS=${corruptOpen}`);
 console.log(`A_FINAL=${a}`);
 console.log(`B_FINAL=${b}`);
 console.log(`SECONDS=${sec.toFixed(6)}`);
 console.log(`ROUNDS_PER_SEC=${Math.round(rounds/sec)}`);
 console.log(`RESULT=xe / COMPACTION-DROPPED FINALITY MARKER FAIL`);
 console.log(`RESULT2=0e / FINALITY-CARRYING SNAPSHOT + HOLD-ON-LOSS PASS`);
})();
