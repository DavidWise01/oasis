
#include <stdint.h>

static uint32_t canonical_epoch = 0, canonical_digest = 0;
static uint32_t r1_seq=0,r1_child=0,r1_txid=0,r1_crc=0;
static uint32_t r2_seq=0,r2_child=0,r2_txid=0,r2_crc=0;
static uint32_t resolved_flag=0,resolved_child=0,resolved_txid=0;

static uint32_t record_crc(uint32_t m,uint32_t s,uint32_t c,uint32_t t){
  uint32_t x=0x51EDB00Bu;
  x^=m*0x9E3779B9u; x^=s*0x85EBCA6Bu;
  x^=c*0xC2B2AE35u; x^=t*0x27D4EB2Fu;
  x^=x>>16; x*=0x7FEB352Du; x^=x>>15; x*=0x846CA68Bu; x^=x>>16;
  return x;
}
static uint32_t valid_record(uint32_t m,uint32_t s,uint32_t c,uint32_t t,uint32_t x){
  return m==1 && s!=0 && (c==1||c==2) && t!=0 && x==record_crc(m,s,c,t);
}
static uint32_t exact_stored(uint32_t s,uint32_t c,uint32_t t,uint32_t x){
  return (s==r1_seq&&c==r1_child&&t==r1_txid&&x==r1_crc) ||
         (s==r2_seq&&c==r2_child&&t==r2_txid&&x==r2_crc);
}
__attribute__((export_name("reset"))) void reset(void){
  canonical_epoch=canonical_digest=0;
  r1_seq=r1_child=r1_txid=r1_crc=0;
  r2_seq=r2_child=r2_txid=r2_crc=0;
  resolved_flag=resolved_child=resolved_txid=0;
}
__attribute__((export_name("make_crc")))
uint32_t make_crc(uint32_t m,uint32_t s,uint32_t c,uint32_t t){return record_crc(m,s,c,t);}
__attribute__((export_name("install_fence")))
uint32_t install_fence(uint32_t e,uint32_t d){
  if(e<canonical_epoch)return 0;
  canonical_epoch=e; canonical_digest=d; return 1;
}
__attribute__((export_name("load_conflict_pair")))
uint32_t load_conflict_pair(uint32_t s1,uint32_t c1,uint32_t t1,uint32_t x1,
                            uint32_t s2,uint32_t c2,uint32_t t2,uint32_t x2){
  if(!valid_record(1,s1,c1,t1,x1) || !valid_record(1,s2,c2,t2,x2)) return 0;
  if(c1==c2 && t1==t2) return 0;
  r1_seq=s1;r1_child=c1;r1_txid=t1;r1_crc=x1;
  r2_seq=s2;r2_child=c2;r2_txid=t2;r2_crc=x2;
  return 1;
}
__attribute__((export_name("unsafe_install_packet")))
uint32_t unsafe_install_packet(uint32_t s,uint32_t c,uint32_t t,uint32_t x,
                               uint32_t pe,uint32_t pd){
  if(pe!=canonical_epoch||pd!=canonical_digest) return 0;
  if(!valid_record(1,s,c,t,x)||!exact_stored(s,c,t,x)) return 0;
  resolved_flag=1; resolved_child=c; resolved_txid=t; return 1;
}
__attribute__((export_name("strict_install_packet")))
uint32_t strict_install_packet(uint32_t s,uint32_t c,uint32_t t,uint32_t x,
                               uint32_t pe,uint32_t pd){
  if(pe!=canonical_epoch||pd!=canonical_digest) return 0;
  if(!valid_record(1,s,c,t,x)||!exact_stored(s,c,t,x)) return 0;
  if(!resolved_flag){
    resolved_flag=1; resolved_child=c; resolved_txid=t; return 1;
  }
  if(resolved_child==c && resolved_txid==t) return 1;
  return 0;
}
__attribute__((export_name("resolved_state"))) uint32_t resolved_state(void){return resolved_flag;}
__attribute__((export_name("child_state"))) uint32_t child_state(void){return resolved_child;}
__attribute__((export_name("txid_state"))) uint32_t txid_state(void){return resolved_txid;}
