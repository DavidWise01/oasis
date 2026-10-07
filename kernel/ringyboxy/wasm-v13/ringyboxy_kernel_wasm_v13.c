
#include <stdint.h>

static uint32_t final_child=0,final_txid=0,open_gate=0,hold_flag=0,snapshot_epoch=0;

static uint32_t dig(uint32_t m,uint32_t e,uint32_t c,uint32_t t){
  uint32_t x=0x13C0A5E1u;
  x^=m*0x9E3779B9u; x^=e*0x85EBCA6Bu; x^=c*0xC2B2AE35u; x^=t*0x27D4EB2Fu;
  x^=x>>16; x*=0x7FEB352Du; x^=x>>15; x*=0x846CA68Bu; x^=x>>16;
  return x;
}

__attribute__((export_name("reset"))) void reset(void){
  final_child=final_txid=open_gate=hold_flag=snapshot_epoch=0;
}
__attribute__((export_name("make_digest")))
uint32_t make_digest(uint32_t m,uint32_t e,uint32_t c,uint32_t t){return dig(m,e,c,t);}

__attribute__((export_name("unsafe_restore_child_only")))
uint32_t unsafe_restore_child_only(uint32_t c,uint32_t t){
  if((c!=1&&c!=2)||t==0)return 0;
  final_child=final_txid=0; open_gate=1; hold_flag=0; snapshot_epoch=0; return 1;
}

__attribute__((export_name("strict_restore_child_only")))
uint32_t strict_restore_child_only(uint32_t c,uint32_t t){
  final_child=final_txid=0; open_gate=0; hold_flag=1; snapshot_epoch=0;
  if((c!=1&&c!=2)||t==0)return 0;
  return 0;
}

__attribute__((export_name("strict_restore_snapshot")))
uint32_t strict_restore_snapshot(uint32_t m,uint32_t e,uint32_t c,uint32_t t,uint32_t d){
  final_child=final_txid=0; open_gate=0; hold_flag=1; snapshot_epoch=0;
  if(m!=1||e==0||(c!=1&&c!=2)||t==0)return 0;
  if(d!=dig(m,e,c,t))return 0;
  final_child=c;final_txid=t;snapshot_epoch=e;hold_flag=0;open_gate=1;return 1;
}

__attribute__((export_name("try_commit")))
uint32_t try_commit(uint32_t c,uint32_t t){
  if(!open_gate||(c!=1&&c!=2)||t==0)return 0;
  if(final_child==c&&final_txid==t)return 1;
  if(final_child!=0)return 0;
  final_child=c;final_txid=t;return 1;
}
__attribute__((export_name("child_state"))) uint32_t child_state(void){return final_child;}
__attribute__((export_name("txid_state"))) uint32_t txid_state(void){return final_txid;}
__attribute__((export_name("open_state"))) uint32_t open_state(void){return open_gate;}
__attribute__((export_name("hold_state"))) uint32_t hold_state(void){return hold_flag;}
__attribute__((export_name("epoch_state"))) uint32_t epoch_state(void){return snapshot_epoch;}
