//! UEP-204R: sequential SHA-256 evidence ledger. .dlw
//! Integrity is not authenticity. No real liability, authorization or payment.
use crate::restitution::{assessed_estimate, Assessment, Estimate};
use sha2::{Digest,Sha256};
use std::collections::{BTreeMap,BTreeSet};
pub const ORIGINAL_HTML_SHA256:&str="0a940b059cf7511f3110b8c8994372d818a7909124de97bc28f057da722802be";
#[derive(Clone,Debug,PartialEq,Eq)]
pub enum Event {
    Estimate { id:String, valuation:u64, assessment:Assessment },
    AcceptModel { id:String, estimate_id:String, decision_ref:String },
}
#[derive(Clone,Debug,PartialEq,Eq)]
pub struct Record { pub sequence:u64, pub previous:[u8;32], pub hash:[u8;32], pub event:Event }
#[derive(Clone,Debug,Default,PartialEq,Eq)]
pub struct Ledger { records:Vec<Record> }
fn field(h:&mut Sha256,s:&str){h.update((s.len() as u64).to_be_bytes());h.update(s.as_bytes());}
fn digest(sequence:u64,previous:[u8;32],e:&Event)->[u8;32]{
    let mut h=Sha256::new();h.update(b"OASIS-UEP-204R-v1");h.update(sequence.to_be_bytes());h.update(previous);
    match e {
        Event::Estimate{id,valuation,assessment:a}=>{
            h.update([0u8]);field(&mut h,id);h.update(valuation.to_be_bytes());field(&mut h,&a.target);
            h.update((a.evidence_refs.len() as u64).to_be_bytes());
            for s in &a.evidence_refs{field(&mut h,s);}
            field(&mut h,&a.human_observation_ref);field(&mut h,&a.ai_observation_ref);
            for x in a.positive.iter().chain(a.negative.iter()){h.update(x.to_be_bytes());}
        }
        Event::AcceptModel{id,estimate_id,decision_ref}=>{
            h.update([1u8]);field(&mut h,id);field(&mut h,estimate_id);field(&mut h,decision_ref);
        }
    }
    h.finalize().into()
}
fn valid(s:&str)->bool{!s.trim().is_empty()&&s.len()<=4096}
#[derive(Default)]
struct Index { ids:BTreeSet<String>, estimates:BTreeMap<String,Estimate>, accepted:BTreeSet<String>, total:u64 }
impl Index{
 fn apply(&mut self,e:&Event)->Result<(),&'static str>{
    let id=match e{Event::Estimate{id,..}|Event::AcceptModel{id,..}=>id};
    if !valid(id)||self.ids.contains(id){return Err("duplicate or invalid event id")}
    match e{
      Event::Estimate{id,valuation,assessment:a}=>{
        if !valid(&a.target)||a.evidence_refs.len()>256||!a.evidence_refs.iter().all(|s|valid(s))||
          !valid(&a.human_observation_ref)||!valid(&a.ai_observation_ref){return Err("invalid evidence fields")}
        self.estimates.insert(id.clone(),assessed_estimate(*valuation,a)?);
      }
      Event::AcceptModel{estimate_id,decision_ref,..}=>{
        if !valid(decision_ref)||self.accepted.contains(estimate_id){return Err("invalid or duplicate model acceptance")}
        let x=self.estimates.get(estimate_id).ok_or("missing prior estimate")?;
        self.total=self.total.checked_add(x.due_cents).ok_or("model balance overflow")?;
        self.accepted.insert(estimate_id.clone());
      }
    }
    self.ids.insert(id.clone());Ok(())
 }
}
fn verify(records:&[Record])->Result<Index,&'static str>{
 if records.len()>10000{return Err("ledger limit")}
 let mut index=Index::default();let mut prev=[0u8;32];
 for (i,r) in records.iter().enumerate(){
    let seq=i as u64+1;
    if r.sequence!=seq||r.previous!=prev||r.hash!=digest(seq,prev,&r.event){return Err("broken chain")}
    index.apply(&r.event)?;prev=r.hash;
 }
 Ok(index)
}
impl Ledger{
 pub fn records(&self)->&[Record]{&self.records}
 pub fn from_records(records:Vec<Record>)->Result<Self,&'static str>{verify(&records)?;Ok(Self{records})}
 pub fn head(&self)->[u8;32]{self.records.last().map_or([0;32],|r|r.hash)}
 pub fn verify_head(&self,expected:[u8;32])->Result<(),&'static str>{
    verify(&self.records)?;if self.head()!=expected{return Err("head mismatch")}Ok(())
 }
 pub fn append(&self,event:Event)->Result<Self,&'static str>{
    let mut index=verify(&self.records)?;
    if self.records.len()>=10000{return Err("ledger limit")}
    index.apply(&event)?;
    let sequence=self.records.len() as u64+1;let previous=self.head();
    let hash=digest(sequence,previous,&event);
    let mut records=self.records.clone();records.push(Record{sequence,previous,hash,event});Ok(Self{records})
 }
 pub fn modeled_accepted_total(&self)->Result<u64,&'static str>{Ok(verify(&self.records)?.total)}
}
#[cfg(test)]
mod tests{
 use super::*;
 fn estimate(id:&str)->Event{Event::Estimate{id:id.into(),valuation:10000,assessment:Assessment{target:"synthetic".into(),evidence_refs:vec!["source".into()],human_observation_ref:"human".into(),ai_observation_ref:"ai".into(),positive:[999;22],negative:[0;22]}}}
 fn accept(id:&str,source:&str)->Event{Event::AcceptModel{id:id.into(),estimate_id:source.into(),decision_ref:"simulation-decision".into()}}
 #[test]fn estimates_not_obligations(){let a=Ledger::default().append(estimate("e1")).unwrap();assert_eq!(a.modeled_accepted_total().unwrap(),0);let b=a.append(accept("a1","e1")).unwrap();assert_eq!(b.modeled_accepted_total().unwrap(),2050);assert_eq!(a.records().len(),1);}
 #[test]fn sequential_links(){let mut l=Ledger::default();for i in 0..20{let old=l.head();l=l.append(estimate(&format!("e{i}"))).unwrap();assert_eq!(l.records().last().unwrap().previous,old);}assert!(l.verify_head(l.head()).is_ok());}
 #[test]fn tamper_reorder_truncate(){let l=Ledger::default().append(estimate("e1")).unwrap().append(accept("a1","e1")).unwrap();let mut r=l.records().to_vec();r[0].hash[0]^=1;assert!(Ledger::from_records(r).is_err());let mut r=l.records().to_vec();r.swap(0,1);assert!(Ledger::from_records(r).is_err());let prefix=Ledger::from_records(l.records()[..1].to_vec()).unwrap();assert!(prefix.verify_head(l.head()).is_err());}
 #[test]fn rejects_duplicate_and_missing(){let l=Ledger::default();assert!(l.append(accept("a1","e1")).is_err());let l=l.append(estimate("e1")).unwrap();assert!(l.append(estimate("e1")).is_err());let l=l.append(accept("a1","e1")).unwrap();assert!(l.append(accept("a2","e1")).is_err());}
 #[test]fn deterministic(){let a=Ledger::default().append(estimate("e1")).unwrap();let b=Ledger::default().append(estimate("e1")).unwrap();assert_eq!(a,b);}
}
