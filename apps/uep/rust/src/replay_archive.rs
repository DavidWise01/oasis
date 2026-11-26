//! UEP-243R: bounded immutable replay snapshots. Synthetic only. .dlw
use crate::{evidence::Ledger,executable::{Universe,Request},journal,request_codec,state_hash::{self,Commitment}};
use sha2::{Digest,Sha256};
const MAGIC:&[u8;8]=b"UEP243R\0";
pub const MAX_BYTES:usize=64*1024*1024;
pub const MAX_STEPS:usize=360;
#[derive(Clone,Debug,PartialEq,Eq)]
pub struct Archive{ledger:Ledger,universe:Universe,entries:Vec<(Vec<u8>,Commitment)>}
#[derive(Clone,Debug,PartialEq,Eq)]
pub struct Checkpoint{pub count:u64,pub archive_digest:[u8;32],pub closing:[u8;32]}
fn digest(b:&[u8])->[u8;32]{let mut h=Sha256::new();h.update(b"OASIS-UEP-243R-archive-v1");h.update(b);h.finalize().into()}
fn num(b:&mut Vec<u8>,x:u64){b.extend_from_slice(&x.to_be_bytes())}
fn block(b:&mut Vec<u8>,x:&[u8])->Result<(),&'static str>{if b.len().checked_add(8).and_then(|v|v.checked_add(x.len())).ok_or("size overflow")?>MAX_BYTES{return Err("archive size")}num(b,x.len() as u64);b.extend_from_slice(x);Ok(())}
impl Archive{
 pub fn new(ledger:Ledger,head:[u8;32])->Result<Self,&'static str>{let universe=Universe::new(ledger.clone(),head)?;Ok(Self{ledger,universe,entries:vec![]})}
 pub fn universe(&self)->&Universe{&self.universe}
 pub fn append(&self,r:&Request)->Result<Self,&'static str>{
  if self.entries.len()>=MAX_STEPS{return Err("archive steps")}
  let bytes=request_codec::encode(r)?;let (universe,c)=state_hash::advance(&self.universe,r)?;
  let mut n=self.clone();n.universe=universe;n.entries.push((bytes,c));n.encode()?;Ok(n)
 }
 pub fn encode(&self)->Result<Vec<u8>,&'static str>{
  let mut b=MAGIC.to_vec();num(&mut b,self.ledger.records().len() as u64);b.extend_from_slice(&self.ledger.head());block(&mut b,&journal::encode(&self.ledger)?)?;num(&mut b,self.entries.len() as u64);
  for (r,c) in &self.entries{block(&mut b,r)?;if b.len()>MAX_BYTES-128{return Err("archive size")}for x in [&c.opening,&c.request,&c.closing,&c.digest]{b.extend_from_slice(x)}}
  if b.len()>MAX_BYTES{return Err("archive size")}Ok(b)
 }
 pub fn checkpoint(&self)->Result<Checkpoint,&'static str>{Ok(Checkpoint{count:self.entries.len() as u64,archive_digest:digest(&self.encode()?),closing:state_hash::fingerprint(&self.universe)?})}
}
struct Reader<'a>{b:&'a[u8],p:usize}
impl<'a> Reader<'a>{
 fn take(&mut self,n:usize)->Result<&'a[u8],&'static str>{let end=self.p.checked_add(n).ok_or("length overflow")?;let x=self.b.get(self.p..end).ok_or("truncated archive")?;self.p=end;Ok(x)}
 fn n(&mut self)->Result<u64,&'static str>{Ok(u64::from_be_bytes(self.take(8)?.try_into().map_err(|_|"number")?))}
 fn hash(&mut self)->Result<[u8;32],&'static str>{self.take(32)?.try_into().map_err(|_|"hash")}
 fn block(&mut self)->Result<&'a[u8],&'static str>{let n=self.n()?;if n>MAX_BYTES as u64{return Err("block size")}self.take(n as usize)}
}
pub fn decode(b:&[u8],expected:&Checkpoint)->Result<Archive,&'static str>{
 if b.len()>MAX_BYTES||digest(b)!=expected.archive_digest{return Err("archive fingerprint")}
 let mut d=Reader{b,p:0};if d.take(8)?!=MAGIC{return Err("version")}
 let count=d.n()?;let head=d.hash()?;let ledger=journal::decode(d.block()?,&journal::Checkpoint{count,head})?;
 let n=d.n()?;if n>MAX_STEPS as u64||n!=expected.count{return Err("archive count")}
 let mut a=Archive::new(ledger,head)?;
 for _ in 0..n{let bytes=d.block()?;let r=request_codec::decode(bytes)?;if request_codec::encode(&r)?!=bytes{return Err("noncanonical request")}
  let c=Commitment{opening:d.hash()?,request:d.hash()?,closing:d.hash()?,digest:d.hash()?};
  let (u,actual)=state_hash::advance(&a.universe,&r)?;if c!=actual||!c.verify(){return Err("replay mismatch")}
  a.universe=u;a.entries.push((bytes.to_vec(),c));
 }
 if d.p!=b.len()||state_hash::fingerprint(&a.universe)?!=expected.closing{return Err("closing or trailing bytes")}
 Ok(a)
}
#[cfg(not(target_arch="wasm32"))]
pub fn export_new(path:&std::path::Path,a:&Archive)->Result<Checkpoint,Box<dyn std::error::Error>>{use std::io::Write;let b=a.encode()?;let c=a.checkpoint()?;let mut f=std::fs::OpenOptions::new().write(true).create_new(true).open(path)?;f.write_all(&b)?;f.sync_all()?;Ok(c)}
#[cfg(not(target_arch="wasm32"))]
pub fn recover(path:&std::path::Path,c:&Checkpoint)->Result<Archive,Box<dyn std::error::Error>>{use std::io::Read;let mut b=Vec::new();std::fs::File::open(path)?.take((MAX_BYTES+1) as u64).read_to_end(&mut b)?;Ok(decode(&b,c)?)}
#[cfg(test)]
mod tests{
 use super::*;use crate::{equilibrium::Step,population::Period,bridge::Shares,dividend::Revenue,capacity::Input};
 fn root()->Archive{Archive::new(Ledger::default(),[0;32]).unwrap()}
 fn req()->Request{let s=Step{period:Period{enter:vec![],depart:vec![],award:100,funding:600},restitution:Shares::default(),revenue:Revenue{public_equity:0,licensing:0,automation_royalties:0,infrastructure_return:0},dividend_cap:0,resources:Input{inflow:[100;4],essential:[20;4],decay_bps:0,work_ceiling:17}};Request{present:s.clone(),requested:0,complete:0,accept:0,future:vec![s]}}
 #[test]fn roundtrip(){let mut a=root();for _ in 0..12{a=a.append(&req()).unwrap()}let b=a.encode().unwrap();assert_eq!(decode(&b,&a.checkpoint().unwrap()).unwrap(),a);}
 #[test]fn truncation(){let a=root().append(&req()).unwrap();let b=a.encode().unwrap();let c=a.checkpoint().unwrap();for i in 0..b.len(){assert!(decode(&b[..i],&c).is_err());}}
 #[test]fn altered_commitment(){let a=root().append(&req()).unwrap();let mut b=a.encode().unwrap();let mut c=a.checkpoint().unwrap();let n=b.len();b[n-1]^=1;c.archive_digest=digest(&b);assert!(decode(&b,&c).is_err());}
 #[test]fn rollback(){let a=root();let b=a.append(&req()).unwrap();assert!(decode(&a.encode().unwrap(),&b.checkpoint().unwrap()).is_err());}
 #[test]fn trailing(){let a=root().append(&req()).unwrap();let mut b=a.encode().unwrap();b.push(0);let mut c=a.checkpoint().unwrap();c.archive_digest=digest(&b);assert!(decode(&b,&c).is_err());}
 #[test]fn nonempty_ledger(){use crate::{evidence::Event,restitution::Assessment};let l=Ledger::default().append(Event::Estimate{id:"e".into(),valuation:10000,assessment:Assessment{target:"synthetic".into(),evidence_refs:vec!["source".into()],human_observation_ref:"h".into(),ai_observation_ref:"a".into(),positive:[999;22],negative:[0;22]}}).unwrap();let a=Archive::new(l.clone(),l.head()).unwrap().append(&req()).unwrap();assert_eq!(decode(&a.encode().unwrap(),&a.checkpoint().unwrap()).unwrap(),a);}
}

// UEP-244R: exact immutable ancestry comparison.
impl Archive{pub fn extends(&self,prior:&Self)->bool{self.ledger==prior.ledger&&self.entries.starts_with(&prior.entries)}}
