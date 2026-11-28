//! UEP-288R: bounded qualified delta replay, legacy byte-compatible. .dlw
use crate::{authenticated_state::Root,qualified_delta::Qualified,executable::{Universe,Request},request_codec};
use sha2::{Sha256,Digest};
use std::sync::Arc;
type Entry=Arc<(Vec<u8>,Root)>;
pub const LIMIT:usize=360;
pub const BYTE_LIMIT:usize=64*1024*1024;
use crate::authenticated_recovery::decode_commitment;
#[derive(Clone,Debug,PartialEq,Eq)]
pub struct Anchor{pub total:u64,pub digest:[u8;32],pub closing:Root}
#[derive(Clone,Debug,PartialEq,Eq)]
pub struct Tape{opening:Root,start:u64,projection:Qualified,entries:Vec<Entry>}
fn hash(b:&[u8])->[u8;32]{let mut h=Sha256::new();h.update(b"OASIS-UEP-277R-tape-v1");h.update(b);h.finalize().into()}
impl Tape{
 pub fn start(p:&Qualified,c:&Root)->Result<Self,&'static str>{
  if p.root()!=c||!c.verify(){return Err("opening root")}if !p.universe().observations().is_empty(){return Err("opening not compacted")}
  Ok(Self{opening:c.clone(),start:p.universe().total_observations(),projection:p.clone(),entries:vec![]})
 }
 pub fn projection(&self)->&Qualified{&self.projection}
 pub fn universe(&self)->&Universe{self.projection.universe()}
 pub fn append(&self,r:&Request)->Result<Self,&'static str>{let _span=crate::verification_profile::span(30);
  if self.entries.len()>=LIMIT{return Err("tape full")}
  let c=self.entries.last().map_or(&self.opening,|e|&e.1);
  let(p,_,_)=self.projection.advance(r,c)?;let next=p.root().clone();
  let mut n={let _profile=crate::verification_profile::span(9);Self{opening:self.opening.clone(),start:self.start,projection:p,entries:self.entries.clone()}};let raw={let _span=crate::verification_profile::span(29);request_codec::encode(r)?};n.entries.push(Arc::new((raw,next)));n.encode()?;Ok(n)
 }
 pub fn encode(&self)->Result<Vec<u8>,&'static str>{let _span=crate::verification_profile::span(28);
  let mut b=b"UEP277R\0".to_vec();b.extend_from_slice(&self.start.to_be_bytes());b.extend_from_slice(&self.opening.encode());b.extend_from_slice(&(self.entries.len() as u64).to_be_bytes());
  for entry in &self.entries{let(r,c)=entry.as_ref();if b.len().checked_add(r.len()).and_then(|n|n.checked_add(176)).ok_or("size")?>BYTE_LIMIT{return Err("tape size")}b.extend_from_slice(&(r.len() as u64).to_be_bytes());b.extend_from_slice(r);b.extend_from_slice(&c.encode());}Ok(b)
 }
 pub fn anchor(&self)->Result<Anchor,&'static str>{Ok(Anchor{total:self.start.checked_add(self.entries.len() as u64).ok_or("total")?,digest:hash(&self.encode()?),closing:self.projection.root().clone()})}
 pub fn successor(&self,a:&Anchor)->Result<Self,&'static str>{if self.entries.len()!=LIMIT||self.anchor()?!=*a{return Err("boundary")}let p=self.projection.compact(&a.closing)?;Self::start(&p,&a.closing)}
}
struct Reader<'a>{b:&'a[u8],i:usize}
impl<'a>Reader<'a>{fn take(&mut self,n:usize)->Result<&'a[u8],&'static str>{let end=self.i.checked_add(n).ok_or("length")?;let v=self.b.get(self.i..end).ok_or("truncated")?;self.i=end;Ok(v)}fn num(&mut self)->Result<u64,&'static str>{Ok(u64::from_be_bytes(self.take(8)?.try_into().unwrap()))}}
pub fn recover(p:&Qualified,opening:&Root,b:&[u8],expected:&Anchor)->Result<Tape,&'static str>{
 if b.len()>BYTE_LIMIT||hash(b)!=expected.digest{return Err("tape digest or size")}
 let mut d=Reader{b,i:0};if d.take(8)?!=b"UEP277R\0"||d.num()?!=p.universe().total_observations()||decode_commitment(d.take(168)?)?!=*opening{return Err("opening mismatch")}
 let count=d.num()?;if count>LIMIT as u64||p.universe().total_observations().checked_add(count)!=Some(expected.total){return Err("count")}
 let mut n=Tape::start(p,opening)?;
 for _ in 0..count{let len=d.num()?;if len>BYTE_LIMIT as u64{return Err("request size")}let raw=d.take(len as usize)?;let r=request_codec::decode(raw)?;if request_codec::encode(&r)?!=raw{return Err("noncanonical request")}let c=decode_commitment(d.take(168)?)?;n=n.append(&r)?;if n.entries.last().map(|x|&x.1)!=Some(&c){return Err("transition mismatch")}}
 if d.i!=b.len()||n.anchor()?!=*expected||n.encode()?!=b{return Err("terminal mismatch")}Ok(n)
}
#[cfg(not(target_arch="wasm32"))]
pub fn recover_file(p:&Qualified,opening:&Root,path:&std::path::Path,expected:&Anchor)->Result<Tape,&'static str>{use std::io::Read;let mut b=Vec::new();std::fs::File::open(path).map_err(|_|"open")?.take((BYTE_LIMIT+1) as u64).read_to_end(&mut b).map_err(|_|"read")?;recover(p,opening,&b,expected)}

#[cfg(test)]mod sharing294_tests{
 use super::*;use crate::{authenticated_state::State,evidence::Ledger,state_hash,equilibrium::Step,population::Period,bridge::Shares,dividend::Revenue,capacity::Input};
 fn opening()->Tape{let u=Universe::new(Ledger::default(),[0;32]).unwrap();let s=State::build(&u,state_hash::fingerprint(&u).unwrap()).unwrap();let q=Qualified::import(&s,&u,&s.root()).unwrap();Tape::start(&q,q.root()).unwrap()}
 fn req(f:u64)->Request{let s=Step{period:Period{enter:vec![],depart:vec![],award:100,funding:f},restitution:Shares::default(),revenue:Revenue{public_equity:0,licensing:0,automation_royalties:0,infrastructure_return:0},dividend_cap:0,resources:Input{inflow:[100;4],essential:[20;4],decay_bps:0,work_ceiling:17}};Request{present:s.clone(),requested:0,complete:0,accept:0,future:vec![s]}}
 #[test]fn shared_prefix(){let a=opening().append(&req(500)).unwrap();let raw=a.encode().unwrap();let b=a.append(&req(750)).unwrap();assert!(Arc::ptr_eq(&a.entries[0],&b.entries[0]));assert_eq!(a.encode().unwrap(),raw);assert_eq!(a.entries.len(),1);assert_eq!(b.entries.len(),2);}
 #[test]fn fork_isolation(){let a=opening().append(&req(500)).unwrap();let b=a.append(&req(600)).unwrap();let c=a.append(&req(750)).unwrap();assert!(Arc::ptr_eq(&b.entries[0],&c.entries[0]));assert!(!Arc::ptr_eq(&b.entries[1],&c.entries[1]));assert_ne!(b.anchor().unwrap(),c.anchor().unwrap());drop(a);assert_eq!(b.entries[0],c.entries[0]);}
 #[test]fn recovery(){let a=opening();let mut b=a.clone();for i in 0..30{b=b.append(&req(if i%2==0{500}else{750})).unwrap();}let raw=b.encode().unwrap();let anchor=b.anchor().unwrap();let c=recover(a.projection(),a.projection().root(),&raw,&anchor).unwrap();assert_eq!(b,c);assert_eq!(c.encode().unwrap(),raw);assert!(!Arc::ptr_eq(&b.entries[0],&c.entries[0]));}
 #[test]fn bounded_history(){let a=opening();let mut b=a.clone();for _ in 0..LIMIT{b=b.append(&req(600)).unwrap();}assert!(b.append(&req(600)).is_err());let c=b.successor(&b.anchor().unwrap()).unwrap();assert!(c.entries.is_empty());assert_eq!(c.start,360);assert_eq!(b.entries.len(),360);}
}
