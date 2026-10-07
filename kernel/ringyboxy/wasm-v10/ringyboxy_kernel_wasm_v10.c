
#include <stdint.h>

static uint32_t committed_child = 0, committed_txid = 0;
static uint32_t open_gate = 0, conflict = 0;
static uint32_t r1_seq=0,r1_child=0,r1_txid=0,r1_crc=0;
static uint32_t r2_seq=0,r2_child=0,r2_txid=0,r2_crc=0;

static uint32_t record_crc(uint32_t marker,uint32_t seq,uint32_t child,uint32_t txid) {
  uint32_t x=0x243F6A88u;
  x ^= marker*0x9E3779B9u; x ^= seq*0x85EBCA6Bu;
  x ^= child*0xC2B2AE35u; x ^= txid*0x27D4EB2Fu;
  x ^= x>>16; x*=0x7FEB352Du; x^=x>>15; x*=0x846CA68Bu; x^=x>>16;
  return x;
}
static uint32_t valid_record(uint32_t m,uint32_t s,uint32_t c,uint32_t t,uint32_t x) {
  return m==1 && s!=0 && (c==1||c==2) && t!=0 && x==record_crc(m,s,c,t);
}
__attribute__((export_name("reset"))) void reset(void) {
  committed_child=committed_txid=open_gate=conflict=0;
  r1_seq=r1_child=r1_txid=r1_crc=0; r2_seq=r2_child=r2_txid=r2_crc=0;
}
__attribute__((export_name("make_crc")))
uint32_t make_crc(uint32_t m,uint32_t s,uint32_t c,uint32_t t){return record_crc(m,s,c,t);}

__attribute__((export_name("unsafe_restore_one")))
uint32_t unsafe_restore_one(uint32_t m,uint32_t s,uint32_t c,uint32_t t,uint32_t x){
  if(!valid_record(m,s,c,t,x)) return 0;
  committed_child=c; committed_txid=t; open_gate=1; conflict=0; return 1;
}

__attribute__((export_name("strict_restore_pair")))
uint32_t strict_restore_pair(
  uint32_t m1,uint32_t s1,uint32_t c1,uint32_t t1,uint32_t x1,
  uint32_t m2,uint32_t s2,uint32_t c2,uint32_t t2,uint32_t x2) {
  reset();
  uint32_t v1=valid_record(m1,s1,c1,t1,x1), v2=valid_record(m2,s2,c2,t2,x2);
  if((m1==1&&!v1)||(m2==1&&!v2)) return 0;
  if(v1&&!v2){committed_child=c1;committed_txid=t1;open_gate=1;return 1;}
  if(!v1&&v2){committed_child=c2;committed_txid=t2;open_gate=1;return 1;}
  if(!v1&&!v2) return 0;
  if(c1==c2 && t1==t2){committed_child=c1;committed_txid=t1;open_gate=1;return 1;}
  r1_seq=s1;r1_child=c1;r1_txid=t1;r1_crc=x1;
  r2_seq=s2;r2_child=c2;r2_txid=t2;r2_crc=x2;
  conflict=1; open_gate=0; return 0;
}
static uint32_t exact_stored(uint32_t s,uint32_t c,uint32_t t,uint32_t x){
  uint32_t a=(s==r1_seq&&c==r1_child&&t==r1_txid&&x==r1_crc);
  uint32_t b=(s==r2_seq&&c==r2_child&&t==r2_txid&&x==r2_crc);
  return a||b;
}
__attribute__((export_name("resolve_exact")))
uint32_t resolve_exact(uint32_t s,uint32_t c,uint32_t t,uint32_t x){
  if(!conflict) return 0;
  if(!valid_record(1,s,c,t,x)) return 0;
  if(!exact_stored(s,c,t,x)) return 0;
  committed_child=c;committed_txid=t;conflict=0;open_gate=1;return 1;
}
__attribute__((export_name("try_commit")))
uint32_t try_commit(uint32_t c,uint32_t t){
  if(!open_gate || (c!=1&&c!=2) || t==0) return 0;
  if(committed_child==c && committed_txid==t) return 1;
  if(committed_child!=0) return 0;
  committed_child=c;committed_txid=t;return 1;
}
__attribute__((export_name("child_state"))) uint32_t child_state(void){return committed_child;}
__attribute__((export_name("txid_state"))) uint32_t txid_state(void){return committed_txid;}
__attribute__((export_name("open_state"))) uint32_t open_state(void){return open_gate;}
__attribute__((export_name("conflict_state"))) uint32_t conflict_state(void){return conflict;}
