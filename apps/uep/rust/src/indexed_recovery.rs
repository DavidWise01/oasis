//! UEP-267R: bounded ordered projection replay packets. .dlw
use crate::{working_projection::{Projection,ProjectionCommitment},executable::{Universe,Request},request_codec};
use sha2::{Sha256,Digest};
pub const LIMIT:usize=360;
pub const BYTE_LIMIT:usize=64*1024*1024;
pub fn decode_commitment(b:&[u8])->Result<ProjectionCommitment,&'static str>{
 if b.len()!=168||&b[..8]!=b"UEP266R\0"{return Err("commitment format")}
 let a=|i:usize|-> [u8;32]{b[i..i+32].try_into().unwrap()};
 let c=ProjectionCommitment{authority:a(8),balances:a(40),identities:a(72),chronology:a(104),digest:a(136)};
 if !c.verify()||c.encode()!=b{return Err("commitment digest")}Ok(c)
}
#[derive(Clone,Debug,PartialEq,Eq)]
pub struct Anchor{pub total:u64,pub digest:[u8;32],pub closing:ProjectionCommitment}
#[derive(Clone,Debug,PartialEq,Eq)]
pub struct Tape{opening:ProjectionCommitment,start:u64,projection:Projection,universe:Universe,entries:Vec<(Vec<u8>,ProjectionCommitment)>}
fn hash(b:&[u8])->[u8;32]{let mut h=Sha256::new();h.update(b"OASIS-UEP-267R-tape-v1");h.update(b);h.finalize().into()}
impl Tape{
 pub fn start(p:&Projection,u:&Universe,c:&ProjectionCommitment)->Result<Self,&'static str>{
  p.verify_commitment(u,c)?;if !u.observations().is_empty(){return Err("opening not compacted")}
  Ok(Self{opening:c.clone(),start:u.total_observations(),projection:p.clone(),universe:u.clone(),entries:vec![]})
 }
 pub fn projection(&self)->&Projection{&self.projection}
 pub fn universe(&self)->&Universe{&self.universe}
 pub fn append(&self,r:&Request)->Result<Self,&'static str>{
  if self.entries.len()>=LIMIT{return Err("tape full")}
  let c=self.entries.last().map_or(&self.opening,|e|&e.1);
  let(p,u,_,_,next)=self.projection.advance_committed(&self.universe,r,c)?;
  let mut n={let _profile=crate::verification_profile::span(9);self.clone()};n.projection=p;n.universe=u;n.entries.push((request_codec::encode(r)?,next));n.encode()?;Ok(n)
 }
 pub fn encode(&self)->Result<Vec<u8>,&'static str>{
  let mut b=b"UEP267R\0".to_vec();b.extend_from_slice(&self.start.to_be_bytes());b.extend_from_slice(&self.opening.encode());b.extend_from_slice(&(self.entries.len() as u64).to_be_bytes());
  for(r,c)in &self.entries{if b.len().checked_add(r.len()).and_then(|n|n.checked_add(176)).ok_or("size")?>BYTE_LIMIT{return Err("tape size")}b.extend_from_slice(&(r.len() as u64).to_be_bytes());b.extend_from_slice(r);b.extend_from_slice(&c.encode());}Ok(b)
 }
 pub fn anchor(&self)->Result<Anchor,&'static str>{Ok(Anchor{total:self.start.checked_add(self.entries.len() as u64).ok_or("total")?,digest:hash(&self.encode()?),closing:self.projection.commitment(&self.universe)?})}
 pub fn successor(&self,a:&Anchor)->Result<Self,&'static str>{if self.entries.len()!=LIMIT||self.anchor()?!=*a{return Err("boundary")}let u=self.projection.compact(&self.universe)?;Self::start(&self.projection,&u,&a.closing)}
}
struct Reader<'a>{b:&'a[u8],i:usize}
impl<'a>Reader<'a>{fn take(&mut self,n:usize)->Result<&'a[u8],&'static str>{let end=self.i.checked_add(n).ok_or("length")?;let v=self.b.get(self.i..end).ok_or("truncated")?;self.i=end;Ok(v)}fn num(&mut self)->Result<u64,&'static str>{Ok(u64::from_be_bytes(self.take(8)?.try_into().unwrap()))}}
pub fn recover(p:&Projection,u:&Universe,opening:&ProjectionCommitment,b:&[u8],expected:&Anchor)->Result<Tape,&'static str>{
 if b.len()>BYTE_LIMIT||hash(b)!=expected.digest{return Err("tape digest or size")}
 let mut d=Reader{b,i:0};if d.take(8)?!=b"UEP267R\0"||d.num()?!=u.total_observations()||decode_commitment(d.take(168)?)?!=*opening{return Err("opening mismatch")}
 let count=d.num()?;if count>LIMIT as u64||u.total_observations().checked_add(count)!=Some(expected.total){return Err("count")}
 let mut n=Tape::start(p,u,opening)?;
 for _ in 0..count{let len=d.num()?;if len>BYTE_LIMIT as u64{return Err("request size")}let raw=d.take(len as usize)?;let r=request_codec::decode(raw)?;if request_codec::encode(&r)?!=raw{return Err("noncanonical request")}let c=decode_commitment(d.take(168)?)?;n=n.append(&r)?;if n.entries.last().map(|x|&x.1)!=Some(&c){return Err("transition mismatch")}}
 if d.i!=b.len()||n.anchor()?!=*expected||n.encode()?!=b{return Err("terminal mismatch")}Ok(n)
}
#[cfg(not(target_arch="wasm32"))]
pub fn recover_file(p:&Projection,u:&Universe,opening:&ProjectionCommitment,path:&std::path::Path,expected:&Anchor)->Result<Tape,&'static str>{use std::io::Read;let mut b=Vec::new();std::fs::File::open(path).map_err(|_|"open")?.take((BYTE_LIMIT+1) as u64).read_to_end(&mut b).map_err(|_|"read")?;recover(p,u,opening,&b,expected)}
#[cfg(test)]mod tests{
 use super::*;use crate::{evidence::Ledger,state_hash,equilibrium::Step,population::Period,bridge::Shares,dividend::Revenue,capacity::Input};
 fn root()->Tape{let u=Universe::new(Ledger::default(),[0;32]).unwrap();let p=Projection::build(&u,state_hash::fingerprint(&u).unwrap()).unwrap();Tape::start(&p,&u,&p.commitment(&u).unwrap()).unwrap()}
 fn req(f:u64)->Request{let s=Step{period:Period{enter:vec![],depart:vec![],award:100,funding:f},restitution:Shares::default(),revenue:Revenue{public_equity:0,licensing:0,automation_royalties:0,infrastructure_return:0},dividend_cap:0,resources:Input{inflow:[100;4],essential:[20;4],decay_bps:0,work_ceiling:17}};Request{present:s.clone(),requested:0,complete:0,accept:0,future:vec![s]}}
 fn fixture()->(Tape,Tape){let a=root();let b=a.append(&req(0)).unwrap().append(&req(1200)).unwrap();(a,b)}
 #[test]fn packet(){let a=root();let b=a.opening.encode();assert_eq!(decode_commitment(&b).unwrap(),a.opening);for i in 0..b.len(){let mut x=b.clone();x[i]^=1;assert!(decode_commitment(&x).is_err())}assert!(decode_commitment(&b[..167]).is_err());}
 #[test]fn replay_history(){let(a,b)=fixture();let n=recover(&a.projection,&a.universe,&a.opening,&b.encode().unwrap(),&b.anchor().unwrap()).unwrap();assert_eq!(n,b);let reset=Projection::build(&n.universe,state_hash::fingerprint(&n.universe).unwrap()).unwrap();assert!(reset.verify_commitment(&n.universe,&n.anchor().unwrap().closing).is_err());}
 #[test]fn rehashed_tamper(){let(a,b)=fixture();let raw=b.encode().unwrap();for i in [0,8,16,184,192,200,raw.len()-1]{let mut x=raw.clone();x[i]^=1;let mut c=b.anchor().unwrap();c.digest=hash(&x);assert!(recover(&a.projection,&a.universe,&a.opening,&x,&c).is_err())}let mut x=raw.clone();x.push(0);let mut c=b.anchor().unwrap();c.digest=hash(&x);assert!(recover(&a.projection,&a.universe,&a.opening,&x,&c).is_err());}
 #[test]fn boundary(){let a=root();let mut b=a.clone();for _ in 0..360{b=b.append(&req(600)).unwrap()}let c=b.anchor().unwrap();let n=b.successor(&c).unwrap();assert_eq!(n.universe.total_observations(),360);assert!(n.universe.observations().is_empty());assert_eq!(n.opening,c.closing);assert!(b.append(&req(600)).is_err());let z=n.append(&req(500)).unwrap();assert_eq!(recover(&n.projection,&n.universe,&n.opening,&z.encode().unwrap(),&z.anchor().unwrap()).unwrap(),z);}
 #[test]fn wrong_terminal(){let(a,b)=fixture();let mut c=b.anchor().unwrap();c.total+=1;assert!(recover(&a.projection,&a.universe,&a.opening,&b.encode().unwrap(),&c).is_err());assert!(a.successor(&a.anchor().unwrap()).is_err());}
}
