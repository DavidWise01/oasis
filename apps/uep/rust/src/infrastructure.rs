//! UEP-207R: modeled infrastructure conversion, never actual disbursement. .dlw
use crate::priority::{Engine,Frame as PriorityFrame};
use crate::population::Period;
use crate::bridge::Shares;
use std::collections::BTreeMap;
#[derive(Clone,Debug,Default,PartialEq,Eq)]
pub struct Work { pub spent:u64,pub completed:u64,pub accepted:u64 }
#[derive(Clone,Debug,PartialEq,Eq)]
pub struct Infrastructure {
    priority:Engine, stock:u64, gain:u64,pending:u64,harm:u64,
    work:BTreeMap<String,Work>,
}
#[derive(Clone,Debug,PartialEq,Eq)]
pub struct Request {pub case_id:String,pub spend_units:u64,pub complete_units:u64,pub accept_units:u64}
#[derive(Clone,Debug,PartialEq,Eq)]
pub struct Conditions {pub inflow:u64,pub essential:u64,pub other_essentials_met:bool,pub decay_bps:u64,pub maintenance:u64,pub request:Option<Request>}
#[derive(Clone,Debug,PartialEq,Eq)]
pub struct Frame {pub next:Infrastructure,pub accounting:PriorityFrame,pub delivered:u64,pub blocked:bool,pub maintenance:u64}
const COST:u64=2;const RESERVE:u64=10;const CAP:u64=100;const GAIN_CAP:u64=30;
impl Infrastructure {
 pub fn genesis(priority:Engine)->Self{Self{priority,stock:90,gain:15,pending:0,harm:17,work:BTreeMap::new()}}
 pub fn priority(&self)->&Engine{&self.priority}
 pub fn stock(&self)->u64{self.stock}
 pub fn gain(&self)->u64{self.gain}
 pub fn harm(&self)->u64{self.harm}
 pub fn work(&self)->&BTreeMap<String,Work>{&self.work}
 pub fn with_priority(&self,ledger:&crate::evidence::Ledger,head:[u8;32],metadata:&BTreeMap<String,crate::priority::Priority>)->Result<Self,&'static str>{
   let mut n=self.clone();n.priority=self.priority.sync(ledger,head,metadata)?;Ok(n)
 }
 pub fn advance(&self,p:&Period,funding:Shares,c:&Conditions)->Result<Frame,&'static str>{
   if c.inflow>1_000_000||c.essential>1_000_000||c.decay_bps>10000||c.maintenance>30{return Err("invalid conditions")}
   let accounting=self.priority.advance(p,funding)?;
   let mut n=self.clone();n.priority=accounting.next.clone();
   n.gain=(n.gain+n.pending).min(GAIN_CAP);n.pending=0;
   n.stock=(n.stock+c.inflow+n.gain).min(CAP);
   let delivered=c.essential.min(n.stock.saturating_sub(5));n.stock-=delivered;
   let decay=(n.gain*c.decay_bps+9999)/10000;
   let blocked=delivered<c.essential||!c.other_essentials_met||n.stock<RESERVE||accounting.universal.current_funded<accounting.universal.current_due;
   let maintenance=if blocked{0}else{c.maintenance.min(decay).min(n.stock.saturating_sub(RESERVE))};
   // Maintenance consumes water only; financial and labor costs are not modeled.
   n.stock-=maintenance;n.gain-=decay-maintenance;
   if let Some(r)=&c.request{
      if [r.spend_units,r.complete_units,r.accept_units].iter().any(|&x|x>1_000_000){return Err("invalid work request")}
      let case=n.priority.cases().get(&r.case_id).ok_or("unknown case")?;
      let w=n.work.entry(r.case_id.clone()).or_default();
      let spend=r.spend_units.checked_mul(COST).ok_or("cost overflow")?;
      let water=r.spend_units.checked_mul(2).ok_or("water overflow")?;
      if r.spend_units>0&&(blocked||water>n.stock.saturating_sub(RESERVE)){return Err("physical protection")}
      w.spent=w.spent.checked_add(spend).ok_or("spend overflow")?;
      if w.spent>case.reserved.carbon{return Err("unfunded work")}
      w.completed=w.completed.checked_add(r.complete_units).ok_or("completion overflow")?;
      if w.completed>w.spent/COST{return Err("unfunded completion")}
      w.accepted=w.accepted.checked_add(r.accept_units).ok_or("acceptance overflow")?;
      if w.accepted>w.completed||r.accept_units>n.harm{return Err("unsupported acceptance")}
      n.stock-=water;n.harm-=r.accept_units;n.pending=r.accept_units.min(GAIN_CAP);
   }
   Ok(Frame{next:n,accounting,delivered,blocked,maintenance})
 }
}
#[cfg(test)]
mod tests{
 use super::*;use crate::evidence::{Ledger,Event};use crate::restitution::Assessment;use crate::priority::Priority;
 fn root()->Infrastructure{
  let l=Ledger::default().append(Event::Estimate{id:"case".into(),valuation:10000,assessment:Assessment{target:"synthetic".into(),evidence_refs:vec!["source".into()],human_observation_ref:"human".into(),ai_observation_ref:"ai".into(),positive:[999;22],negative:[0;22]}}).unwrap().append(Event::AcceptModel{id:"accept".into(),estimate_id:"case".into(),decision_ref:"model".into()}).unwrap();
  let mut m=BTreeMap::new();m.insert("case".into(),Priority{origin:1,affected:100,deprivation:500,harm:500,urgency:500,source_ref:"synthetic".into()});
  Infrastructure::genesis(Engine::genesis()).with_priority(&l,l.head(),&m).unwrap()
 }
 fn p(funding:u64)->Period{Period{enter:vec![],depart:vec![],award:100,funding}}
 fn c()->Conditions{Conditions{inflow:30,essential:20,other_essentials_met:true,decay_bps:2000,maintenance:0,request:None}}
 fn f()->Shares{Shares{carbon:100,ai:25}}
 #[test]fn distinct_stages(){let s=root();let mut a=c();a.request=Some(Request{case_id:"case".into(),spend_units:5,complete_units:0,accept_units:0});let r=s.advance(&p(800),f(),&a).unwrap();assert_eq!(r.next.harm(),17);assert_eq!(r.next.work()["case"].spent,10);a.request=Some(Request{case_id:"case".into(),spend_units:0,complete_units:5,accept_units:3});let t=r.next.advance(&p(800),f(),&a).unwrap();assert_eq!(t.next.harm(),14);assert_eq!(t.next.work()["case"].accepted,3);assert_eq!(t.next.pending,3);let z=t.next.advance(&p(800),f(),&c()).unwrap();assert_eq!(z.next.pending,0);assert_eq!(s.harm(),17);}
 #[test]fn scarcity_and_unfunded_rejected(){let s=root();let mut a=c();a.request=Some(Request{case_id:"case".into(),spend_units:5,complete_units:0,accept_units:0});assert!(s.advance(&p(500),f(),&a).is_err());assert!(s.advance(&p(800),Shares::default(),&a).is_err());a.other_essentials_met=false;assert!(s.advance(&p(800),f(),&a).is_err());}
 #[test]fn no_completion_without_spend(){let mut a=c();a.request=Some(Request{case_id:"case".into(),spend_units:0,complete_units:1,accept_units:1});assert!(root().advance(&p(800),f(),&a).is_err());}
 #[test]fn maintenance_non_offset(){let s=root();let mut a=c();a.maintenance=3;let r=s.advance(&p(800),f(),&a).unwrap();let b=s.advance(&p(800),f(),&c()).unwrap();assert_eq!(r.accounting.universal,b.accounting.universal);assert_eq!(r.next.gain(),b.next.gain()+3);assert_eq!(r.next.stock()+3,b.next.stock());}
 #[test]fn bounded_grid(){for inflow in [0,20,40]{for essential in [10,30,90]{for funds in [0,500,800]{let mut s=root();for _ in 0..360{let mut a=c();a.inflow=inflow;a.essential=essential;a.maintenance=3;let r=s.advance(&p(funds),f(),&a).unwrap();assert!(r.next.stock()<=100&&r.next.gain()<=30);assert!(!r.blocked||r.maintenance==0);assert_eq!(r.next.harm(),17);s=r.next;}}}}}
}
