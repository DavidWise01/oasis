//! UEP-229R: coordinated economic universe; one logical funding stream, two reconciled views. .dlw
use crate::{bridge::{Bridge,Shares},dividend::Economy,entitlement::Protected,generation::Generation,infrastructure::{Infrastructure,Conditions},priority::{Engine,Priority},evidence::Ledger,equilibrium::Step,arrears,lifecycle::Report};
use std::collections::BTreeMap;
#[derive(Clone,Debug,PartialEq,Eq)]
pub struct Universe{economic:Protected,generation:Generation,ledger:Ledger,head:[u8;32]}
#[derive(Clone,Debug,PartialEq,Eq)]
pub struct Frame{pub next:Universe,pub lifecycle:Report,pub economics:crate::entitlement::Frame,pub receipts:Vec<arrears::Receipt>}
impl Universe{
 pub fn new(ledger:Ledger,head:[u8;32],metadata:&BTreeMap<String,Priority>)->Result<Self,&'static str>{
  ledger.verify_head(head)?;
  let economic=Protected::new(Economy::new(Bridge::genesis())).sync(&ledger,head)?;
  let infrastructure=Infrastructure::genesis(Engine::genesis()).with_priority(&ledger,head,metadata)?;
  Ok(Self{economic,generation:Generation::new(infrastructure),ledger,head})
 }
 pub fn advance(&self,s:&Step)->Result<Frame,&'static str>{
  let audit=arrears::advance(self.economic.economy().bridge().population(),&s.period)?;
  let e=self.economic.advance(&s.period,s.restitution.clone(),&s.revenue,s.dividend_cap,&s.resources)?;
  // No physical work is committed: four-resource execution is not yet implemented.
  let c=Conditions{inflow:s.resources.inflow[0],essential:s.resources.essential[0],other_essentials_met:!e.physical.blocked,decay_bps:s.resources.decay_bps,maintenance:0,request:None};
  let g=self.generation.advance(&self.ledger,self.head,&s.period,s.restitution.clone(),&c)?;
  if g.universal!=e.economic.universal||audit.settlement!=g.universal{return Err("universal parity")}
  let mut assessed=Shares::default();let mut reserved=Shares::default();
  for x in g.closing.cases.values().filter(|x|x.accepted_model){
   assessed.carbon=assessed.carbon.checked_add(x.estimated.carbon).ok_or("carbon total")?;
   assessed.ai=assessed.ai.checked_add(x.estimated.ai).ok_or("AI total")?;
   reserved.carbon=reserved.carbon.checked_add(x.reserved.carbon).ok_or("carbon reservation")?;
   reserved.ai=reserved.ai.checked_add(x.reserved.ai).ok_or("AI reservation")?;
  }
  let b=e.next.economy().bridge();
  if &assessed!=b.assessed()||&reserved!=b.funded(){return Err("funding view parity")}
  if g.closing.residual_harm!=e.physical.next.harm()||g.closing.restored_units!=0{return Err("physical view parity")}
  let next=Self{economic:e.next.clone(),generation:g.next,ledger:self.ledger.clone(),head:self.head};
  Ok(Frame{next,lifecycle:g.closing,economics:e,receipts:audit.receipts})
 }
}
#[cfg(test)]
mod tests{
 use super::*;use crate::{evidence::Event,restitution::Assessment,capacity::Input,dividend::Revenue,population::Period};
 fn root()->Universe{
 let l=Ledger::default().append(Event::Estimate{id:"e".into(),valuation:10000,assessment:Assessment{target:"synthetic aggregate".into(),evidence_refs:vec!["source".into()],human_observation_ref:"human".into(),ai_observation_ref:"ai".into(),positive:[999;22],negative:[0;22]}}).unwrap().append(Event::AcceptModel{id:"a".into(),estimate_id:"e".into(),decision_ref:"model".into()}).unwrap();
 let m=BTreeMap::from([("e".into(),Priority{origin:1,affected:100,deprivation:500,harm:500,urgency:500,source_ref:"synthetic".into()})]);let h=l.head();Universe::new(l,h,&m).unwrap()
 }
 fn step(funding:u64)->Step{Step{period:Period{enter:vec![],depart:vec![],award:100,funding},restitution:Shares{carbon:100,ai:25},revenue:Revenue{public_equity:1000,licensing:0,automation_royalties:0,infrastructure_return:0},dividend_cap:100,resources:Input{inflow:[20;4],essential:[20;4],decay_bps:2000,work_ceiling:17}}}
 #[test]fn integrated(){let s=root();let f=s.advance(&step(500)).unwrap();assert_eq!(f.lifecycle.cases["e"].reserved,Shares{carbon:100,ai:25});assert_eq!(f.economics.economic.universal.current_funded,500);assert_eq!(f.economics.physical.work,0);assert_eq!(f.lifecycle.residual_harm,17);}
 #[test]fn recovery_receipt(){let s=root().advance(&step(500)).unwrap().next;let f=s.advance(&step(750)).unwrap();assert_eq!(f.receipts.iter().map(|r|r.reserved).sum::<u64>(),100);assert_eq!(f.economics.economic.universal.closing.outstanding().unwrap(),400);}
 #[test]fn replay(){let s=root();let p=step(600);assert_eq!(s.advance(&p).unwrap(),s.advance(&p).unwrap());}
 #[test]fn grid(){for funding in [0,500,750]{for demand in [10,40,90]{for revenue in [0,300,1000]{let mut s=root();for _ in 0..360{let mut p=step(funding);p.resources.essential=[demand;4];p.revenue.public_equity=revenue;let f=s.advance(&p).unwrap();assert_eq!(f.lifecycle.residual_harm,17);assert_eq!(f.economics.economic.universal.current_due,600);s=f.next;}}}}}
}
