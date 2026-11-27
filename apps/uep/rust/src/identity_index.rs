//! UEP-263R: derived append-only historical identity commitment. .dlw
use crate::{population::{Population,Period},identity_continuity};
use std::collections::BTreeSet;
use sha2::{Digest,Sha256};
#[derive(Clone,Debug,PartialEq,Eq)]
pub struct IdentityIndex{known:BTreeSet<String>,active:BTreeSet<String>,epoch:u64,head:[u8;32],count:u64}
fn valid(id:&str)->bool{!id.is_empty()&&id.len()<=30&&id.bytes().all(|b|b.is_ascii_alphanumeric()||b==b'_'||b==b'-')}
fn fold(head:[u8;32],count:u64,id:&str)->[u8;32]{let mut h=Sha256::new();h.update(b"OASIS-UEP-263R-identity-v1");h.update(head);h.update(count.to_be_bytes());h.update((id.len() as u64).to_be_bytes());h.update(id.as_bytes());h.finalize().into()}
impl IdentityIndex{
 /// Bootstrap a sorted membership snapshot; this does not reconstruct pre-bootstrap entry order.
 pub fn build(p:&Population)->Result<Self,&'static str>{
  if p.known.len()>10000||!p.active.is_subset(&p.known)||!p.known.iter().all(|id|valid(id)){return Err("invalid identity snapshot")}
  let mut n=Self{known:BTreeSet::new(),active:p.active.clone(),epoch:p.epoch,head:[0;32],count:0};
  for id in &p.known{n.insert(id)?;}Ok(n)
 }
 fn insert(&mut self,id:&str)->Result<(),&'static str>{if !valid(id)||self.known.len()>=10000||!self.known.insert(id.into()){return Err("identity reuse or capacity")}self.count=self.count.checked_add(1).ok_or("count")?;self.head=fold(self.head,self.count,id);Ok(())}
 pub fn known(&self,id:&str)->bool{self.known.contains(id)}
 pub fn active(&self,id:&str)->bool{self.active.contains(id)}
 pub fn count(&self)->u64{self.count}
 pub fn head(&self)->[u8;32]{self.head}
 pub fn verify_membership(&self,p:&Population)->Result<(),&'static str>{if self.epoch!=p.epoch||self.known!=p.known||self.active!=p.active||self.count!=p.known.len() as u64{return Err("identity membership mismatch")}Ok(())}
 /// Full-scan qualification remains enabled; the history head changes only on new identities.
 pub fn advance(&self,opening:&Population,closing:&Population,r:&Period)->Result<Self,&'static str>{
  self.verify_membership(opening)?;let d=identity_continuity::verify(opening,closing,r)?;
  let mut n={let _profile=crate::verification_profile::span(8);self.clone()};for id in d.departed{n.active.remove(&id);}for id in d.entered{n.insert(&id)?;n.active.insert(id);}
  n.epoch=closing.epoch;n.verify_membership(closing)?;Ok(n)
 }
}
#[cfg(test)]mod tests{
 use super::*;use crate::population::settle;
 fn req()->Period{Period{enter:vec![],depart:vec![],award:100,funding:600}}
 #[test]fn unchanged_without_entry(){let p=Population::phase_ix();let i=IdentityIndex::build(&p).unwrap();let q=settle(&p,&req()).unwrap().closing;let n=i.advance(&p,&q,&req()).unwrap();assert_eq!(n.head(),i.head());assert_eq!(n.count(),7);}
 #[test]fn churn360(){let mut p=Population::phase_ix();let mut i=IdentityIndex::build(&p).unwrap();let mut current="A_1".to_string();for t in 0..360{let mut r=req();let next=format!("G_{t}");r.depart=vec![std::mem::replace(&mut current,next.clone())];r.enter=vec![next];let q=settle(&p,&r).unwrap().closing;let n=i.advance(&p,&q,&r).unwrap();assert_ne!(n.head(),i.head());i=n;p=q;}assert_eq!(i.count(),367);assert!(i.known("A_1"));assert!(!i.active("A_1"));assert!(i.active("G_359"));assert_eq!(i.active.len(),6);}
 #[test]fn reuse_and_erasure(){let p=Population::phase_ix();let i=IdentityIndex::build(&p).unwrap();let mut r=req();r.enter=vec!["A_0".into()];assert!(i.advance(&p,&p,&r).is_err());let mut q=settle(&p,&req()).unwrap().closing;q.known.remove("A_0");assert!(i.advance(&p,&q,&req()).is_err());}
 #[test]fn batch_order_canonical(){let p=Population::phase_ix();let i=IdentityIndex::build(&p).unwrap();let mut r=req();r.enter=vec!["Z".into(),"E".into()];let q=settle(&p,&r).unwrap().closing;let n=i.advance(&p,&q,&r).unwrap();r.enter.reverse();let q=settle(&p,&r).unwrap().closing;assert_eq!(n,i.advance(&p,&q,&r).unwrap());}
 #[test]fn stale_and_debt_substitution(){let p=Population::phase_ix();let i=IdentityIndex::build(&p).unwrap();let mut r=req();r.funding=0;let q=settle(&p,&r).unwrap().closing;let n=i.advance(&p,&q,&r).unwrap();assert!(i.verify_membership(&q).is_err());let mut r=req();r.enter=vec!["G".into()];r.depart=vec!["A_1".into()];let mut z=settle(&q,&r).unwrap().closing;z.lots[0].id="G".into();assert!(n.advance(&q,&z,&r).is_err());}
}

// UEP-266R: commit actual membership as well as incremental historical head.
impl IdentityIndex{pub(crate) fn commitment_bytes(&self)->Vec<u8>{let _profile=crate::verification_profile::span(5);let mut b=b"UEP266I\0".to_vec();b.extend_from_slice(&self.epoch.to_be_bytes());b.extend_from_slice(&self.count.to_be_bytes());b.extend_from_slice(&self.head);for set in [&self.known,&self.active]{b.extend_from_slice(&(set.len() as u64).to_be_bytes());for id in set{b.extend_from_slice(&(id.len() as u64).to_be_bytes());b.extend_from_slice(id.as_bytes())}}b}}
