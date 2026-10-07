
#include <stdint.h>

/*
  v11: conflict resolution must itself be fence-bound.

  State:
    canonical fence = {epoch, digest}
    conflict = two distinct valid records for one parent
    prepared resolution = exact stored winner + fence under which authority chose it

  Unsafe install:
    applies prepared resolution even if canonical fence has rolled.

  Strict install:
    requires prepared resolution fence == current canonical fence
    at the instant of installation.

  This models the authority/fencing invariant; it is not a full consensus protocol.
*/

static uint32_t canonical_epoch = 0;
static uint32_t canonical_digest = 0;

static uint32_t open_gate = 0;
static uint32_t conflict = 0;
static uint32_t committed_child = 0;
static uint32_t committed_txid = 0;

static uint32_t r1_seq=0,r1_child=0,r1_txid=0,r1_crc=0;
static uint32_t r2_seq=0,r2_child=0,r2_txid=0,r2_crc=0;

static uint32_t prep_flag=0;
static uint32_t prep_seq=0,prep_child=0,prep_txid=0,prep_crc=0;
static uint32_t prep_epoch=0,prep_digest=0;

static uint32_t record_crc(uint32_t marker,uint32_t seq,uint32_t child,uint32_t txid) {
  uint32_t x=0xA5A5F00Du;
  x ^= marker*0x9E3779B9u;
  x ^= seq*0x85EBCA6Bu;
  x ^= child*0xC2B2AE35u;
  x ^= txid*0x27D4EB2Fu;
  x ^= x>>16; x*=0x7FEB352Du; x^=x>>15; x*=0x846CA68Bu; x^=x>>16;
  return x;
}

static uint32_t valid_record(uint32_t m,uint32_t s,uint32_t c,uint32_t t,uint32_t x) {
  return m==1 && s!=0 && (c==1||c==2) && t!=0 && x==record_crc(m,s,c,t);
}

static uint32_t exact_stored(uint32_t s,uint32_t c,uint32_t t,uint32_t x) {
  uint32_t a=(s==r1_seq&&c==r1_child&&t==r1_txid&&x==r1_crc);
  uint32_t b=(s==r2_seq&&c==r2_child&&t==r2_txid&&x==r2_crc);
  return a||b;
}

__attribute__((export_name("reset")))
void reset(void) {
  canonical_epoch=canonical_digest=0;
  open_gate=conflict=0;
  committed_child=committed_txid=0;
  r1_seq=r1_child=r1_txid=r1_crc=0;
  r2_seq=r2_child=r2_txid=r2_crc=0;
  prep_flag=prep_seq=prep_child=prep_txid=prep_crc=prep_epoch=prep_digest=0;
}

__attribute__((export_name("make_crc")))
uint32_t make_crc(uint32_t m,uint32_t s,uint32_t c,uint32_t t) {
  return record_crc(m,s,c,t);
}

__attribute__((export_name("install_fence")))
uint32_t install_fence(uint32_t epoch,uint32_t digest) {
  if (epoch < canonical_epoch) return 0;
  canonical_epoch=epoch;
  canonical_digest=digest;
  return 1;
}

__attribute__((export_name("load_conflict_pair")))
uint32_t load_conflict_pair(
  uint32_t s1,uint32_t c1,uint32_t t1,uint32_t x1,
  uint32_t s2,uint32_t c2,uint32_t t2,uint32_t x2) {

  if(!valid_record(1,s1,c1,t1,x1)) return 0;
  if(!valid_record(1,s2,c2,t2,x2)) return 0;
  if(c1==c2 && t1==t2) return 0; /* duplicate, not conflict */

  r1_seq=s1;r1_child=c1;r1_txid=t1;r1_crc=x1;
  r2_seq=s2;r2_child=c2;r2_txid=t2;r2_crc=x2;

  conflict=1;
  open_gate=0;
  committed_child=0;
  committed_txid=0;
  prep_flag=0;
  return 1;
}

/*
  Authority prepares an exact resolution under the current canonical fence.
*/
__attribute__((export_name("prepare_resolution")))
uint32_t prepare_resolution(uint32_t s,uint32_t c,uint32_t t,uint32_t x) {
  if(!conflict) return 0;
  if(!valid_record(1,s,c,t,x)) return 0;
  if(!exact_stored(s,c,t,x)) return 0;

  prep_seq=s;prep_child=c;prep_txid=t;prep_crc=x;
  prep_epoch=canonical_epoch;
  prep_digest=canonical_digest;
  prep_flag=1;
  return 1;
}

static uint32_t apply_resolution(void) {
  if(!prep_flag) return 0;
  committed_child=prep_child;
  committed_txid=prep_txid;
  conflict=0;
  open_gate=1;
  prep_flag=0;
  return 1;
}

__attribute__((export_name("unsafe_install_resolution")))
uint32_t unsafe_install_resolution(void) {
  return apply_resolution();
}

__attribute__((export_name("strict_install_resolution")))
uint32_t strict_install_resolution(void) {
  if(!prep_flag) return 0;

  if(prep_epoch!=canonical_epoch || prep_digest!=canonical_digest) {
    prep_flag=0; /* stale authority object is consumed/rejected */
    return 0;
  }

  return apply_resolution();
}

__attribute__((export_name("try_commit")))
uint32_t try_commit(uint32_t c,uint32_t t) {
  if(!open_gate) return 0;
  if(c!=1&&c!=2) return 0;
  if(t==0) return 0;
  if(committed_child==c && committed_txid==t) return 1;
  if(committed_child!=0) return 0;
  committed_child=c;committed_txid=t;return 1;
}

__attribute__((export_name("open_state"))) uint32_t open_state(void){return open_gate;}
__attribute__((export_name("conflict_state"))) uint32_t conflict_state(void){return conflict;}
__attribute__((export_name("prepared_state"))) uint32_t prepared_state(void){return prep_flag;}
__attribute__((export_name("child_state"))) uint32_t child_state(void){return committed_child;}
__attribute__((export_name("txid_state"))) uint32_t txid_state(void){return committed_txid;}
