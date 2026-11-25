//! UEP-221R: read-only systemic obligation reconciliation. .dlw
use crate::{infrastructure::Infrastructure,bridge::Shares,evidence::{Ledger,Event},restitution::assessed_estimate};
use std::collections::BTreeMap;
#[derive(Clone,Debug,PartialEq,Eq)]
pub struct CaseLifecycle {
 pub estimated:Shares,pub accepted_model:bool,pub reserved:Shares,pub unreserved:Shares,
 pub carbon_spent:u64,pub carbon_reserved_unspent:u64,pub ai_reserved_unspent:u64,
 pub funded_units:u64,pub unfinished_units:u64,pub completed_unaccepted:u64,pub restored_units:u64,
}
#[derive(Clone,Debug,PartialEq,Eq)]
pub struct Report {pub cases:BTreeMap<String,CaseLifecycle>,pub original_harm:u64,pub residual_harm:u64,pub restored_units:u64}
/// Derive lifecycle from actual ledger and infrastructure state, never from caller-declared stage totals.
/// Physical origin is the inherited synthetic genesis of 17 units; no real-world proof.
pub fn reconcile(l:&Ledger,expected:[u8;32],s:&Infrastructure)->Result<Report,&'static str>{
 l.verify_head(expected)?;
 let mut cases=BTreeMap::new();
 for r in l.records(){match &r.event{
  Event::Estimate{id,valuation,assessment}=>{let e=assessed_estimate(*valuation,assessment)?;cases.insert(id.clone(),CaseLifecycle{estimated:Shares{carbon:e.carbon_cents,ai:e.ai_cents},accepted_model:false,reserved:Shares::default(),unreserved:Shares::default(),carbon_spent:0,carbon_reserved_unspent:0,ai_reserved_unspent:0,funded_units:0,unfinished_units:0,completed_unaccepted:0,restored_units:0});}
  Event::AcceptModel{estimate_id,..}=>{cases.get_mut(estimate_id).ok_or("missing estimate")?.accepted_model=true;}
 }}
 let mut total=0u64;
 for (id,c) in &mut cases{
  let p=s.priority().cases().get(id);
  if c.accepted_model!=p.is_some(){return Err("acceptance mismatch")}
  if let Some(p)=p{
   if p.assessed!=c.estimated{return Err("assessment mismatch")}
   c.reserved=p.reserved.clone();
   c.unreserved=Shares{carbon:c.estimated.carbon.checked_sub(c.reserved.carbon).ok_or("carbon reservation")?,ai:c.estimated.ai.checked_sub(c.reserved.ai).ok_or("AI reservation")?};
  }
  if let Some(w)=s.work().get(id){
   if !c.accepted_model||w.spent%2!=0{return Err("work ancestry")}
   c.carbon_spent=w.spent;c.funded_units=w.spent/2;
   c.unfinished_units=c.funded_units.checked_sub(w.completed).ok_or("completion exceeds funded")?;
   c.completed_unaccepted=w.completed.checked_sub(w.accepted).ok_or("acceptance exceeds completion")?;
   c.restored_units=w.accepted;
   total=total.checked_add(w.accepted).ok_or("restoration overflow")?;
  }
  c.carbon_reserved_unspent=c.reserved.carbon.checked_sub(c.carbon_spent).ok_or("unfunded spend")?;
  c.ai_reserved_unspent=c.reserved.ai;
 }
 if s.priority().cases().keys().chain(s.work().keys()).any(|id|!cases.contains_key(id)){return Err("orphan case")}
 if s.harm().checked_add(total)!=Some(17){return Err("harm conservation")}
 Ok(Report{cases,original_harm:17,residual_harm:s.harm(),restored_units:total})
}
#[cfg(test)]
mod tests{
 use super::*;use crate::{priority::{Engine,Priority},population::Period,infrastructure::{Conditions,Request},restitution::Assessment};
 fn fixture()->(Ledger,Infrastructure){
 let l=Ledger::default().append(Event::Estimate{id:"e".into(),valuation:10000,assessment:Assessment{target:"aggregate synthetic".into(),evidence_refs:vec!["source".into()],human_observation_ref:"h".into(),ai_observation_ref:"a".into(),positive:[999;22],negative:[0;22]}}).unwrap().append(Event::AcceptModel{id:"a".into(),estimate_id:"e".into(),decision_ref:"model".into()}).unwrap();
 let m=BTreeMap::from([("e".into(),Priority{origin:1,affected:100,deprivation:500,harm:500,urgency:500,source_ref:"synthetic".into()})]);
 let s=Infrastructure::genesis(Engine::genesis()).with_priority(&l,l.head(),&m).unwrap();(l,s)
 }
 #[test]fn stages(){let(l,s)=fixture();let p=Period{enter:vec![],depart:vec![],award:100,funding:800};let mut c=Conditions{inflow:30,essential:20,other_essentials_met:true,decay_bps:0,maintenance:0,request:Some(Request{case_id:"e".into(),spend_units:5,complete_units:4,accept_units:3})};let f=s.advance(&p,Shares{carbon:100,ai:25},&c).unwrap();let r=reconcile(&l,l.head(),&f.next).unwrap();let e=&r.cases["e"];assert_eq!((e.carbon_spent,e.carbon_reserved_unspent,e.unfinished_units,e.completed_unaccepted,e.restored_units),(10,90,1,1,3));assert_eq!(r.residual_harm,14);c.request=None;let z=s.advance(&p,Shares::default(),&c).unwrap();assert_eq!(f.accounting.universal,z.accounting.universal);}
 #[test]fn wrong_checkpoint(){let(l,s)=fixture();assert!(reconcile(&l,[0;32],&s).is_err());assert!(reconcile(&Ledger::default(),[0;32],&s).is_err());}
 #[test]fn funding_not_restoration(){let(l,s)=fixture();let f=s.advance(&Period{enter:vec![],depart:vec![],award:100,funding:800},Shares{carbon:1640,ai:410},&Conditions{inflow:30,essential:20,other_essentials_met:true,decay_bps:0,maintenance:0,request:None}).unwrap();let r=reconcile(&l,l.head(),&f.next).unwrap();assert_eq!(r.residual_harm,17);assert_eq!(r.cases["e"].carbon_reserved_unspent,1640);}
}
