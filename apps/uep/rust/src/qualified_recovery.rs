//! UEP-288R: bounded qualified delta replay, legacy byte-compatible. .dlw
use crate::{authenticated_state::Root,qualified_delta::Qualified,executable::{Universe,Request},request_codec};
use sha2::{Sha256,Digest};
pub const LIMIT:usize=360;
pub const BYTE_LIMIT:usize=64*1024*1024;
use crate::authenticated_recovery::decode_commitment;
#[derive(Clone,Debug,PartialEq,Eq)]
pub struct Anchor{pub total:u64,pub digest:[u8;32],pub closing:Root}
#[derive(Clone,Debug,PartialEq,Eq)]
pub struct Tape{opening:Root,start:u64,projection:Qualified,entries:Vec<(Vec<u8>,Root)>}
fn hash(b:&[u8])->[u8;32]{let mut h=Sha256::new();h.update(b"OASIS-UEP-277R-tape-v1");h.update(b);h.finalize().into()}
impl Tape{
 pub fn start(p:&Qualified,c:&Root)->Result<Self,&'static str>{
  if p.root()!=c||!c.verify(){return Err("opening root")}if !p.universe().observations().is_empty(){return Err("opening not compacted")}
  Ok(Self{opening:c.clone(),start:p.universe().total_observations(),projection:p.clone(),entries:vec![]})
 }
 pub fn projection(&self)->&Qualified{&self.projection}
 pub fn universe(&self)->&Universe{self.projection.universe()}
 pub fn append(&self,r:&Request)->Result<Self,&'static str>{
  if self.entries.len()>=LIMIT{return Err("tape full")}
  let c=self.entries.last().map_or(&self.opening,|e|&e.1);
  let(p,_,_)=self.projection.advance(r,c)?;let next=p.root().clone();
  let mut n={let _profile=crate::verification_profile::span(9);self.clone()};n.projection=p;n.entries.push((request_codec::encode(r)?,next));n.encode()?;Ok(n)
 }
 pub fn encode(&self)->Result<Vec<u8>,&'static str>{
  let mut b=b"UEP277R\0".to_vec();b.extend_from_slice(&self.start.to_be_bytes());b.extend_from_slice(&self.opening.encode());b.extend_from_slice(&(self.entries.len() as u64).to_be_bytes());
  for(r,c)in &self.entries{if b.len().checked_add(r.len()).and_then(|n|n.checked_add(176)).ok_or("size")?>BYTE_LIMIT{return Err("tape size")}b.extend_from_slice(&(r.len() as u64).to_be_bytes());b.extend_from_slice(r);b.extend_from_slice(&c.encode());}Ok(b)
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
