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
  if parent.total!=u.observations().len() as u64||parent.closing!=state_hash::fingerprint(u)?{return Err("parent state mismatch")}
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
