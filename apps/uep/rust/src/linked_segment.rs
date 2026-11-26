//! UEP-251R: linked bounded segments; inherited state is never reset. .dlw
use crate::{executable::{Universe,Request},replay_archive::{Archive,Checkpoint},state_hash::{self,Commitment},request_codec};
use sha2::{Digest,Sha256};
pub const LIMIT:usize=360;
pub const BYTE_LIMIT:usize=64*1024*1024;
#[derive(Clone,Debug,PartialEq,Eq)]
pub struct Anchor{pub total:u64,pub ancestry:[u8;32],pub closing:[u8;32]}
#[derive(Clone,Debug,PartialEq,Eq)]
pub struct Segment{parent:Anchor,universe:Universe,entries:Vec<(Vec<u8>,Commitment)>}
fn hash(domain:&[u8],bytes:&[u8])->[u8;32]{let mut h=Sha256::new();h.update(domain);h.update(bytes);h.finalize().into()}
fn root_anchor(c:&Checkpoint)->Anchor{let mut b=c.count.to_be_bytes().to_vec();b.extend_from_slice(&c.archive_digest);b.extend_from_slice(&c.closing);Anchor{total:c.count,ancestry:hash(b"OASIS-UEP-251R-root-v1",&b),closing:c.closing}}
impl Segment{
 pub fn from_root(a:&Archive,expected:&Checkpoint)->Result<Self,&'static str>{
  if a.checkpoint()?!=*expected||expected.count!=LIMIT as u64{return Err("root not sealed or mismatch")}
  Self::start(root_anchor(expected),a.universe())
 }
 fn start(parent:Anchor,u:&Universe)->Result<Self,&'static str>{
  if parent.total!=u.total_observations()||parent.closing!=state_hash::fingerprint(u)?{return Err("parent state mismatch")}
  Ok(Self{parent,universe:u.clone(),entries:vec![]})
 }
 pub fn universe(&self)->&Universe{&self.universe}
 pub fn parent(&self)->&Anchor{&self.parent}
 pub fn append(&self,r:&Request)->Result<Self,&'static str>{
  if self.entries.len()>=LIMIT{return Err("segment full")}
  let bytes=request_codec::encode(r)?;let (u,c)=state_hash::advance(&self.universe,r)?;
  let mut n=self.clone();n.universe=u;n.entries.push((bytes,c));n.encode()?;Ok(n)
 }
 pub fn encode(&self)->Result<Vec<u8>,&'static str>{
  let mut b=b"UEP251R\0".to_vec();b.extend_from_slice(&self.parent.total.to_be_bytes());b.extend_from_slice(&self.parent.ancestry);b.extend_from_slice(&self.parent.closing);b.extend_from_slice(&(self.entries.len() as u64).to_be_bytes());
  for (r,c) in &self.entries{if b.len().checked_add(r.len()).and_then(|v|v.checked_add(136)).ok_or("size")?>BYTE_LIMIT{return Err("segment size")}
   b.extend_from_slice(&(r.len() as u64).to_be_bytes());b.extend_from_slice(r);for v in [&c.opening,&c.request,&c.closing,&c.digest]{b.extend_from_slice(v)}}
  Ok(b)
 }
 pub fn anchor(&self)->Result<Anchor,&'static str>{
  let total=self.parent.total.checked_add(self.entries.len() as u64).ok_or("total overflow")?;
  Ok(Anchor{total,ancestry:hash(b"OASIS-UEP-251R-segment-v1",&self.encode()?),closing:state_hash::fingerprint(&self.universe)?})
 }
 pub fn successor(&self,expected:&Anchor)->Result<Self,&'static str>{
  if self.entries.len()!=LIMIT||self.anchor()?!=*expected{return Err("segment not sealed or mismatch")}
  Self::start(expected.clone(),&self.universe)
 }
}
#[cfg(test)]mod tests{
 use super::*;use crate::{evidence::Ledger,equilibrium::Step,population::Period,bridge::Shares,dividend::Revenue,capacity::Input};
 fn req(funding:u64)->Request{let s=Step{period:Period{enter:vec![],depart:vec![],award:100,funding},restitution:Shares::default(),revenue:Revenue{public_equity:0,licensing:0,automation_royalties:0,infrastructure_return:0},dividend_cap:0,resources:Input{inflow:[100;4],essential:[20;4],decay_bps:0,work_ceiling:17}};Request{present:s.clone(),requested:0,complete:0,accept:0,future:vec![s]}}
 fn root()->Archive{Archive::new(Ledger::default(),[0;32]).unwrap()}
 fn small()->Segment{let a=root();Segment::start(root_anchor(&a.checkpoint().unwrap()),a.universe()).unwrap()}
 #[test]fn reject_partial_root(){let a=root();assert!(Segment::from_root(&a,&a.checkpoint().unwrap()).is_err())}
 #[test]fn reject_wrong_state(){let a=root();let mut c=root_anchor(&a.checkpoint().unwrap());c.closing[0]^=1;assert!(Segment::start(c,a.universe()).is_err())}
 #[test]fn branch_binding(){let s=small();let a=s.append(&req(600)).unwrap();let b=s.append(&req(500)).unwrap();assert_ne!(a.anchor().unwrap(),b.anchor().unwrap());assert_eq!(s.anchor().unwrap().total,0);assert!(a.successor(&a.anchor().unwrap()).is_err())}
 #[test]fn continuation(){let mut a=root();for _ in 0..360{a=a.append(&req(600)).unwrap()}let c=a.checkpoint().unwrap();let s=Segment::from_root(&a,&c).unwrap();let n=s.append(&req(500)).unwrap();assert_eq!(n.anchor().unwrap().total,361);assert_eq!(n.universe().observations().last().unwrap().epoch,367);assert_eq!(n.universe(),&a.universe().advance(&req(500)).unwrap());assert_eq!(a.checkpoint().unwrap(),c)}
 #[test]fn full_segment(){let mut s=small();for _ in 0..360{s=s.append(&req(600)).unwrap()}let c=s.anchor().unwrap();assert!(s.append(&req(600)).is_err());let mut wrong=c.clone();wrong.ancestry[0]^=1;assert!(s.successor(&wrong).is_err());let n=s.successor(&c).unwrap();assert_eq!(n.parent(),&c);assert_eq!(n.universe(),s.universe());}
}

// UEP-252R: opt-in compaction at qualified segment boundaries; legacy behavior retained.
impl Segment{pub fn compact_boundary(&self,expected:&Anchor)->Result<Self,&'static str>{if self.entries.len()!=LIMIT||self.anchor()?!=*expected{return Err("boundary mismatch")}let u=self.universe.compact(expected.closing)?;Self::start(expected.clone(),&u)}}

// UEP-256R: canonical successor decoding against an authenticated-by-caller opening and expected closing anchor.
// No standalone state deserialization, no reset, no implicit trust in archive-supplied digests.
struct SegmentReader<'a>{b:&'a[u8],pos:usize}
impl<'a> SegmentReader<'a>{
 fn take(&mut self,n:usize)->Result<&'a[u8],&'static str>{let end=self.pos.checked_add(n).ok_or("segment offset overflow")?;let s=self.b.get(self.pos..end).ok_or("truncated segment")?;self.pos=end;Ok(s)}
 fn num(&mut self)->Result<u64,&'static str>{Ok(u64::from_be_bytes(self.take(8)?.try_into().map_err(|_|"number")?))}
 fn digest(&mut self)->Result<[u8;32],&'static str>{self.take(32)?.try_into().map_err(|_|"digest")}
 fn anchor(&mut self)->Result<Anchor,&'static str>{Ok(Anchor{total:self.num()?,ancestry:self.digest()?,closing:self.digest()?})}
}
impl Segment{
 pub fn recover(open:&Segment,bytes:&[u8],expected:&Anchor)->Result<Self,&'static str>{
  if !open.entries.is_empty(){return Err("nonempty opening segment")}
  if bytes.len()>BYTE_LIMIT{return Err("segment size")}
  if hash(b"OASIS-UEP-251R-segment-v1",bytes)!=expected.ancestry{return Err("segment digest mismatch")}
  let mut d=SegmentReader{b:bytes,pos:0};
  if d.take(8)?!=b"UEP251R\0"{return Err("segment version")}
  let parent=d.anchor()?;
  if parent!=open.parent{return Err("segment parent mismatch")}
  let count=d.num()?;
  if count>LIMIT as u64||parent.total.checked_add(count)!=Some(expected.total){return Err("segment count")}
  let mut s=Self::start(parent,&open.universe)?;
  for _ in 0..count{
   let len=d.num()?;if len>BYTE_LIMIT as u64{return Err("request length")}
   let raw=d.take(len as usize)?;
   let req=request_codec::decode(raw)?;
   if request_codec::encode(&req)?.as_slice()!=raw{return Err("noncanonical request")}
   let recorded=Commitment{opening:d.digest()?,request:d.digest()?,closing:d.digest()?,digest:d.digest()?};
   let(u,actual)=state_hash::advance(&s.universe,&req)?;
   if !recorded.verify()||recorded!=actual{return Err("segment transition mismatch")}
   s.universe=u;s.entries.push((raw.to_vec(),actual));
  }
  if d.pos!=bytes.len()||s.anchor()?!=*expected{return Err("segment closing or trailing bytes")}
  if s.encode()?.as_slice()!=bytes{return Err("segment canonical mismatch")}
  Ok(s)
 }
}
#[cfg(test)]mod fulcrum_tests{
 use super::*;use crate::{evidence::Ledger,equilibrium::Step,population::Period,bridge::Shares,dividend::Revenue,capacity::Input};
 fn req(f:u64)->Request{let s=Step{period:Period{enter:vec![],depart:vec![],award:100,funding:f},restitution:Shares::default(),revenue:Revenue{public_equity:0,licensing:0,automation_royalties:0,infrastructure_return:0},dividend_cap:0,resources:Input{inflow:[100;4],essential:[20;4],decay_bps:0,work_ceiling:17}};Request{present:s.clone(),requested:0,complete:0,accept:0,future:vec![s]}}
 fn open()->Segment{let a=Archive::new(Ledger::default(),[0;32]).unwrap();Segment::start(root_anchor(&a.checkpoint().unwrap()),a.universe()).unwrap()}
 fn fixture()->(Segment,Segment){let a=open();let b=a.append(&req(500)).unwrap().append(&req(750)).unwrap();(a,b)}
 fn rehash(b:&[u8],c:&Anchor)->Anchor{let mut c=c.clone();c.ancestry=hash(b"OASIS-UEP-251R-segment-v1",b);c}
 #[test]fn roundtrip(){let(a,b)=fixture();let raw=b.encode().unwrap();assert_eq!(Segment::recover(&a,&raw,&b.anchor().unwrap()).unwrap(),b);assert_eq!(Segment::recover(&a,&a.encode().unwrap(),&a.anchor().unwrap()).unwrap(),a);}
 #[test]fn truncation_and_trailing(){let(a,b)=fixture();let mut raw=b.encode().unwrap();let c=b.anchor().unwrap();for i in 0..raw.len(){let p=&raw[..i];assert!(Segment::recover(&a,p,&rehash(p,&c)).is_err())}raw.push(0);assert!(Segment::recover(&a,&raw,&rehash(&raw,&c)).is_err());}
 #[test]fn altered_commitments(){let(a,b)=fixture();let raw=b.encode().unwrap();let c=b.anchor().unwrap();for i in raw.len()-128..raw.len(){let mut x=raw.clone();x[i]^=1;assert!(Segment::recover(&a,&x,&rehash(&x,&c)).is_err());}}
 #[test]fn wrong_parent_and_count(){let(a,b)=fixture();let raw=b.encode().unwrap();let c=b.anchor().unwrap();for i in [0,8,16,48,80]{let mut x=raw.clone();x[i]^=128;assert!(Segment::recover(&a,&x,&rehash(&x,&c)).is_err());}let mut x=raw.clone();x[80..88].copy_from_slice(&361u64.to_be_bytes());assert!(Segment::recover(&a,&x,&rehash(&x,&c)).is_err());let mut x=raw.clone();x[88..96].copy_from_slice(&u64::MAX.to_be_bytes());assert!(Segment::recover(&a,&x,&rehash(&x,&c)).is_err());assert!(Segment::recover(&b,&raw,&c).is_err());}
 #[test]fn compacted_successor(){let mut a=Archive::new(Ledger::default(),[0;32]).unwrap();for _ in 0..360{a=a.append(&req(600)).unwrap()}let mut s=Segment::from_root(&a,&a.checkpoint().unwrap()).unwrap();for _ in 0..359{s=s.append(&req(600)).unwrap()}s=s.append(&req(0)).unwrap();let anchor=s.anchor().unwrap();let o=s.compact_boundary(&anchor).unwrap();let n=o.append(&req(700)).unwrap();let raw=n.encode().unwrap();let restored=Segment::recover(&o,&raw,&n.anchor().unwrap()).unwrap();assert_eq!(restored,n);assert_eq!(restored.universe().total_observations(),721);assert_eq!(restored.universe().observations().len(),1);assert_eq!(restored.universe().population_ledger().outstanding().unwrap(),900);}
}
