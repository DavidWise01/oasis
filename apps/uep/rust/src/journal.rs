//! UEP-217R: bounded canonical ledger snapshots and exclusive native export. .dlw
use crate::{evidence::{Event,Ledger,Record},restitution::Assessment};
const MAGIC:&[u8]=b"UEP217\0";
const MAX:usize=64*1024*1024;
#[derive(Clone,Debug,PartialEq,Eq)]
pub struct Checkpoint{pub count:u64,pub head:[u8;32]}
impl Checkpoint{pub fn of(l:&Ledger)->Self{Self{count:l.records().len() as u64,head:l.head()}}}
fn put(b:&mut Vec<u8>,s:&str){b.extend_from_slice(&(s.len() as u32).to_be_bytes());b.extend_from_slice(s.as_bytes());}
pub fn encode(l:&Ledger)->Result<Vec<u8>,&'static str>{
 l.verify_head(l.head())?;let mut b=MAGIC.to_vec();b.extend_from_slice(&(l.records().len() as u64).to_be_bytes());
 for r in l.records(){
  b.extend_from_slice(&r.sequence.to_be_bytes());b.extend_from_slice(&r.previous);b.extend_from_slice(&r.hash);
  match &r.event{
   Event::Estimate{id,valuation,assessment:a}=>{b.push(0);put(&mut b,id);b.extend_from_slice(&valuation.to_be_bytes());put(&mut b,&a.target);b.extend_from_slice(&(a.evidence_refs.len() as u32).to_be_bytes());for s in &a.evidence_refs{put(&mut b,s)}put(&mut b,&a.human_observation_ref);put(&mut b,&a.ai_observation_ref);for x in a.positive.iter().chain(a.negative.iter()){b.extend_from_slice(&x.to_be_bytes())}}
   Event::AcceptModel{id,estimate_id,decision_ref}=>{b.push(1);put(&mut b,id);put(&mut b,estimate_id);put(&mut b,decision_ref)}
  }
  if b.len()>MAX{return Err("snapshot size limit")}
 }Ok(b)
}
struct Reader<'a>{bytes:&'a[u8],at:usize}
impl<'a> Reader<'a>{
 fn take<const N:usize>(&mut self)->Result<[u8;N],&'static str>{let end=self.at.checked_add(N).ok_or("overflow")?;let x=self.bytes.get(self.at..end).ok_or("truncated")?;self.at=end;x.try_into().map_err(|_|"length")}
 fn u64(&mut self)->Result<u64,&'static str>{Ok(u64::from_be_bytes(self.take()?))}
 fn u32(&mut self)->Result<u32,&'static str>{Ok(u32::from_be_bytes(self.take()?))}
 fn string(&mut self)->Result<String,&'static str>{let n=self.u32()? as usize;if n>4096{return Err("string limit")}let end=self.at.checked_add(n).ok_or("overflow")?;let x=self.bytes.get(self.at..end).ok_or("truncated string")?;self.at=end;Ok(std::str::from_utf8(x).map_err(|_|"invalid utf8")?.to_owned())}
}
pub fn decode(bytes:&[u8],expected:&Checkpoint)->Result<Ledger,&'static str>{
 if bytes.len()>MAX||!bytes.starts_with(MAGIC){return Err("invalid snapshot")}
 let mut r=Reader{bytes,at:MAGIC.len()};let count=r.u64()?;if count>10000||count!=expected.count{return Err("count mismatch")}
 let mut records=Vec::with_capacity(count as usize);
 for _ in 0..count{
  let sequence=r.u64()?;let previous=r.take()?;let hash=r.take()?;
  let event=match r.take::<1>()?[0]{
   0=>{let id=r.string()?;let valuation=r.u64()?;let target=r.string()?;let n=r.u32()?;if n>256{return Err("reference limit")}let mut evidence_refs=Vec::new();for _ in 0..n{evidence_refs.push(r.string()?)}let human_observation_ref=r.string()?;let ai_observation_ref=r.string()?;let mut positive=[0u16;22];let mut negative=[0u16;22];for x in positive.iter_mut().chain(negative.iter_mut()){*x=u16::from_be_bytes(r.take()?)}Event::Estimate{id,valuation,assessment:Assessment{target,evidence_refs,human_observation_ref,ai_observation_ref,positive,negative}}}
   1=>Event::AcceptModel{id:r.string()?,estimate_id:r.string()?,decision_ref:r.string()?},
   _=>return Err("unknown event")
  };records.push(Record{sequence,previous,hash,event});
 }
 if r.at!=bytes.len(){return Err("trailing bytes")}
 let l=Ledger::from_records(records)?;l.verify_head(expected.head)?;Ok(l)
}
/// New immutable snapshot path only. Interrupted writes may leave an invalid
/// file; readers reject it. No claim of atomic visibility or directory fsync.
#[cfg(not(target_arch="wasm32"))]
pub fn export_new(path:&std::path::Path,l:&Ledger)->Result<Checkpoint,Box<dyn std::error::Error>>{
 use std::io::Write;
 let bytes=encode(l)?;let mut f=std::fs::OpenOptions::new().write(true).create_new(true).open(path)?;
 f.write_all(&bytes)?;f.sync_all()?;Ok(Checkpoint::of(l))
}
#[cfg(not(target_arch="wasm32"))]
pub fn recover(path:&std::path::Path,expected:&Checkpoint)->Result<Ledger,Box<dyn std::error::Error>>{
 use std::io::Read;
 let mut b=Vec::new();std::fs::File::open(path)?.take((MAX+1) as u64).read_to_end(&mut b)?;Ok(decode(&b,expected)?)
}
#[cfg(test)]
mod tests{
 use super::*;
 fn fixture()->Ledger{Ledger::default().append(Event::Estimate{id:"e".into(),valuation:10000,assessment:Assessment{target:"Gap 🌀".into(),evidence_refs:vec!["source".into()],human_observation_ref:"human".into(),ai_observation_ref:"ai".into(),positive:std::array::from_fn(|i|i as u16*40),negative:std::array::from_fn(|i|999-i as u16*40)}}).unwrap().append(Event::AcceptModel{id:"a".into(),estimate_id:"e".into(),decision_ref:"synthetic".into()}).unwrap()}
 #[test]fn roundtrip(){let l=fixture();let b=encode(&l).unwrap();assert_eq!(decode(&b,&Checkpoint::of(&l)).unwrap(),l);assert_eq!(encode(&decode(&b,&Checkpoint::of(&l)).unwrap()).unwrap(),b);}
 #[test]fn every_truncation(){let l=fixture();let b=encode(&l).unwrap();for i in 0..b.len(){assert!(decode(&b[..i],&Checkpoint::of(&l)).is_err());}}
 #[test]fn every_single_bit(){let l=fixture();let b=encode(&l).unwrap();for i in 0..b.len(){let mut x=b.clone();x[i]^=1;assert!(decode(&x,&Checkpoint::of(&l)).is_err());}}
 #[test]fn rollback_and_suffix(){let l=fixture();let prefix=Ledger::from_records(l.records()[..1].to_vec()).unwrap();assert!(decode(&encode(&prefix).unwrap(),&Checkpoint::of(&l)).is_err());let mut b=encode(&l).unwrap();b.push(0);assert!(decode(&b,&Checkpoint::of(&l)).is_err());}
 #[test]fn empty(){let l=Ledger::default();assert_eq!(decode(&encode(&l).unwrap(),&Checkpoint::of(&l)).unwrap(),l);}
}
