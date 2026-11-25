//! UEP-222R: collective obligations across population turnover. .dlw
use crate::{bridge::Shares,evidence::Ledger,infrastructure::{Infrastructure,Conditions},population::{Period,Population,settle,Settlement},lifecycle::{reconcile,Report}};
#[derive(Clone,Debug,PartialEq,Eq)]
pub struct Generation{system:Infrastructure,universal:Population,epoch:u64}
#[derive(Clone,Debug,PartialEq,Eq)]
pub struct Frame{pub next:Generation,pub opening:Report,pub closing:Report,pub universal:Settlement}
impl Generation{
 pub fn new(system:Infrastructure)->Self{Self{system,universal:Population::phase_ix(),epoch:6}}
 pub fn advance(&self,l:&Ledger,head:[u8;32],p:&Period,funds:Shares,c:&Conditions)->Result<Frame,&'static str>{
  let opening=reconcile(l,head,&self.system)?;
  let baseline=settle(&self.universal,p)?;
  let f=self.system.advance(p,funds,c)?;
  if f.accounting.universal!=baseline{return Err("universal offset")}
  let closing=reconcile(l,head,&f.next)?;
  if closing.original_harm!=opening.original_harm||closing.restored_units<opening.restored_units{return Err("historical harm rewrite")}
  for (id,a) in &opening.cases{
   let b=closing.cases.get(id).ok_or("lost obligation")?;
   if a.estimated!=b.estimated||a.accepted_model!=b.accepted_model||b.reserved.carbon<a.reserved.carbon||b.reserved.ai<a.reserved.ai||b.carbon_spent<a.carbon_spent||b.restored_units<a.restored_units{return Err("historical obligation rewrite")}
  }
  let next=Self{system:f.next,universal:baseline.closing.clone(),epoch:self.epoch.checked_add(1).ok_or("epoch overflow")?};
  Ok(Frame{next,opening,closing,universal:baseline})
 }
 pub fn population(&self)->&Population{&self.universal}
 pub fn epoch(&self)->u64{self.epoch}
}
#[cfg(test)]
mod tests{
 use super::*;use crate::{priority::Engine};
 fn root()->Generation{Generation::new(Infrastructure::genesis(Engine::genesis()))}
 fn conditions()->Conditions{Conditions{inflow:30,essential:20,other_essentials_met:true,decay_bps:0,maintenance:0,request:None}}
 #[test]fn complete_turnover(){let l=Ledger::default();let s=root();let p=Period{depart:s.population().active.iter().cloned().collect(),enter:(0..6).map(|i|format!("new_{i}")).collect(),award:100,funding:600};let f=s.advance(&l,l.head(),&p,Shares::default(),&conditions()).unwrap();assert_eq!(f.closing.residual_harm,17);assert_eq!(f.universal.current_due,600);assert!(f.universal.awards.iter().all(|a|a.due==100&&a.funded==100));assert_eq!(f.next.population().unattributed,400);}
 #[test]fn empty_generation(){let l=Ledger::default();let s=root();let p=Period{depart:s.population().active.iter().cloned().collect(),enter:vec![],award:100,funding:0};let f=s.advance(&l,l.head(),&p,Shares::default(),&conditions()).unwrap();assert_eq!(f.closing.residual_harm,17);assert_eq!(f.universal.current_due,0);}
 #[test]fn repeated_turnover(){let l=Ledger::default();for funding in [0,300,600]{let mut s=root();for i in 0..360{let p=Period{depart:s.population().active.iter().cloned().collect(),enter:(0..6).map(|j|format!("g{i}_{j}")).collect(),award:100,funding};let f=s.advance(&l,l.head(),&p,Shares::default(),&conditions()).unwrap();assert_eq!(f.closing.residual_harm,17);assert_eq!(f.universal.current_due,600);assert_eq!(f.universal.current_funded,funding);s=f.next;}}}
}
