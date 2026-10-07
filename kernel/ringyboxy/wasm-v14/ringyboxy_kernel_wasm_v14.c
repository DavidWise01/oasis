
#include <stdint.h>

/*
  v14: two individually valid compacted snapshots both claim the same latest slot.

  Snapshot identity:
    FINAL marker
    epoch
    prev_digest   -- exact prior canonical snapshot digest
    child
    txid
    digest        -- checksum of the whole snapshot identity

  Unsafe policy:
    accept any individually valid "latest" snapshot locally.

  Strict policy:
    latest is not max(epoch) and not "first valid".
    A candidate must extend the exact trusted prior digest at expected_epoch.
    Two distinct valid children of the same prior snapshot => CONFLICT/HOLD.
    Reopen only after an exact canonical digest names one stored candidate.

  Model only; not a complete distributed consensus protocol.
*/

static uint32_t open_gate=0, conflict=0;
static uint32_t final_child=0, final_txid=0, final_digest=0;

static uint32_t a_epoch=0,a_prev=0,a_child=0,a_txid=0,a_digest=0;
static uint32_t b_epoch=0,b_prev=0,b_child=0,b_txid=0,b_digest=0;

static uint32_t snap_digest(uint32_t marker,uint32_t epoch,uint32_t prev,
                            uint32_t child,uint32_t txid){
  uint32_t x=0x14A11CE5u;
  x^=marker*0x9E3779B9u; x^=epoch*0x85EBCA6Bu;
  x^=prev*0xC2B2AE35u; x^=child*0x27D4EB2Fu; x^=txid*0x165667B1u;
  x^=x>>16; x*=0x7FEB352Du; x^=x>>15; x*=0x846CA68Bu; x^=x>>16;
  return x;
}
static uint32_t self_valid(uint32_t marker,uint32_t epoch,uint32_t prev,
                           uint32_t child,uint32_t txid,uint32_t digest){
  return marker==1 && epoch!=0 && prev!=0 && (child==1||child==2) && txid!=0 &&
         digest==snap_digest(marker,epoch,prev,child,txid);
}
static uint32_t extends(uint32_t expected_epoch,uint32_t trusted_prev,
                        uint32_t marker,uint32_t epoch,uint32_t prev,
                        uint32_t child,uint32_t txid,uint32_t digest){
  return self_valid(marker,epoch,prev,child,txid,digest) &&
         epoch==expected_epoch && prev==trusted_prev;
}

__attribute__((export_name("reset"))) void reset(void){
  open_gate=conflict=0; final_child=final_txid=final_digest=0;
  a_epoch=a_prev=a_child=a_txid=a_digest=0;
  b_epoch=b_prev=b_child=b_txid=b_digest=0;
}
__attribute__((export_name("make_digest")))
uint32_t make_digest(uint32_t m,uint32_t e,uint32_t p,uint32_t c,uint32_t t){
  return snap_digest(m,e,p,c,t);
}

/* Broken local policy: self-validity alone is authority. */
__attribute__((export_name("unsafe_restore_one")))
uint32_t unsafe_restore_one(uint32_t m,uint32_t e,uint32_t p,
                            uint32_t c,uint32_t t,uint32_t d){
  if(!self_valid(m,e,p,c,t,d)) return 0;
  open_gate=1; conflict=0; final_child=c; final_txid=t; final_digest=d; return 1;
}

/*
  Strict recovery of two candidate snapshots for the exact next canonical slot.
  Returns 1 only if one unambiguous semantic identity is recoverable.
*/
__attribute__((export_name("strict_restore_pair")))
uint32_t strict_restore_pair(
  uint32_t expected_epoch,uint32_t trusted_prev,
  uint32_t m1,uint32_t e1,uint32_t p1,uint32_t c1,uint32_t t1,uint32_t d1,
  uint32_t m2,uint32_t e2,uint32_t p2,uint32_t c2,uint32_t t2,uint32_t d2){

  reset();

  uint32_t v1=extends(expected_epoch,trusted_prev,m1,e1,p1,c1,t1,d1);
  uint32_t v2=extends(expected_epoch,trusted_prev,m2,e2,p2,c2,t2,d2);

  /* Claimed FINAL snapshot that fails exact lineage validation => HOLD. */
  if((m1==1&&!v1)||(m2==1&&!v2)) return 0;

  if(v1&&!v2){open_gate=1;final_child=c1;final_txid=t1;final_digest=d1;return 1;}
  if(!v1&&v2){open_gate=1;final_child=c2;final_txid=t2;final_digest=d2;return 1;}
  if(!v1&&!v2) return 0;

  /* Exact semantic duplicate. */
  if(d1==d2 && c1==c2 && t1==t2){
    open_gate=1;final_child=c1;final_txid=t1;final_digest=d1;return 1;
  }

  /* Two distinct valid children of same trusted prior => fork/HOLD. */
  a_epoch=e1;a_prev=p1;a_child=c1;a_txid=t1;a_digest=d1;
  b_epoch=e2;b_prev=p2;b_child=c2;b_txid=t2;b_digest=d2;
  conflict=1; open_gate=0; return 0;
}

__attribute__((export_name("resolve_exact_digest")))
uint32_t resolve_exact_digest(uint32_t digest){
  if(!conflict) return 0;
  if(digest==a_digest){
    final_child=a_child;final_txid=a_txid;final_digest=a_digest;
  } else if(digest==b_digest){
    final_child=b_child;final_txid=b_txid;final_digest=b_digest;
  } else return 0;
  conflict=0;open_gate=1;return 1;
}

__attribute__((export_name("try_replay")))
uint32_t try_replay(uint32_t child,uint32_t txid,uint32_t digest){
  if(!open_gate) return 0;
  return child==final_child && txid==final_txid && digest==final_digest;
}

__attribute__((export_name("open_state"))) uint32_t open_state(void){return open_gate;}
__attribute__((export_name("conflict_state"))) uint32_t conflict_state(void){return conflict;}
__attribute__((export_name("child_state"))) uint32_t child_state(void){return final_child;}
__attribute__((export_name("txid_state"))) uint32_t txid_state(void){return final_txid;}
__attribute__((export_name("digest_state"))) uint32_t digest_state(void){return final_digest;}
