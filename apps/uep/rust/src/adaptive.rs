//! UEP-237R: adaptive regenerative recovery; synthetic transitions only. .dlw
use crate::{regeneration::{Regeneration,Frame as Regenerative},evidence::Ledger,equilibrium::Step};
#[derive(Clone,Debug,PartialEq,Eq)]
pub struct Recovery{state:Regeneration,rate:u64,clear:u64}
#[derive(Clone,Debug,PartialEq,Eq)]
pub struct Frame{pub next:Recovery,pub regeneration:Regenerative,pub requested:u64,pub permitted:u64,pub deferred_completion:u64,pub deferred_acceptance:u64,pub blocked:bool}
impl Recovery{
 pub fn new(l:&Ledger,head:[u8;32])->Result<Self,&'static str>{Ok(Self{state:Regeneration::new(l,head)?,rate:50,clear:0})}
 pub fn rate(&self)->u64{self.rate}
 pub fn state(&self)->&Regeneration{&self.state}
 pub fn advance(&self,s:&Step,requested:u64,complete:u64,accept:u64)->Result<Frame,&'static str>{
  let r=self.state.restoration();
  if complete>r.funded()-r.completed()||accept>r.completed()-r.accepted(){return Err("stage ancestry")}
  // Compute neutral transition from opening state. Never commit both branches.
  let neutral=self.state.advance(s,0,0,0)?;
  let blocked=neutral.lifecycle.expenditure.physical.blocked;
  let clear=if blocked{0}else{self.clear.saturating_add(1)};
  let rate=if blocked{0}else if clear>=2{(self.rate+25).min(100)}else{self.rate};
  let permitted=((requested as u128*rate as u128)/100) as u64;
  let f=if blocked{neutral.clone()}else{self.state.advance(s,permitted,complete,accept)?};
  if f.lifecycle.expenditure.economic.universal!=neutral.lifecycle.expenditure.economic.universal||f.activated!=neutral.activated||f.cap_loss!=neutral.cap_loss||f.decay!=neutral.decay{return Err("neutral parity")}
  if blocked&&(f.lifecycle.expenditure.units!=0||f.lifecycle.completed_now!=0||f.lifecycle.accepted_now!=0){return Err("scarcity violation")}
  let next=Self{state:f.next.clone(),rate,clear};
  Ok(Frame{next,regeneration:f,requested,permitted,deferred_completion:if blocked{complete}else{0},deferred_acceptance:if blocked{accept}else{0},blocked})
 }
}
#[cfg(test)]
mod tests{
 use super::*;use crate::{evidence::Event,restitution::Assessment,capacity::Input,dividend::Revenue,population::Period,bridge::Shares};
 fn root()->Recovery{let l=Ledger::default().append(Event::Estimate{id:"e".into(),valuation:10000,assessment:Assessment{target:"synthetic".into(),evidence_refs:vec!["source".into()],human_observation_ref:"h".into(),ai_observation_ref:"a".into(),positive:[999;22],negative:[0;22]}}).unwrap().append(Event::AcceptModel{id:"a".into(),estimate_id:"e".into(),decision_ref:"model".into()}).unwrap();Recovery::new(&l,l.head()).unwrap()}
 fn step()->Step{Step{period:Period{enter:vec![],depart:vec![],award:100,funding:600},restitution:Shares{carbon:100,ai:0},revenue:Revenue{public_equity:0,licensing:0,automation_royalties:0,infrastructure_return:0},dividend_cap:0,resources:Input{inflow:[40;4],essential:[20;4],decay_bps:0,work_ceiling:17}}}
 #[test]fn ramp(){let mut p=step();p.period.funding=500;let mut s=root().advance(&p,17,0,0).unwrap().next;assert_eq!(s.rate(),0);p.period.funding=750;for rate in [0,25,50,75,100]{let f=s.advance(&p,0,0,0).unwrap();assert_eq!(f.next.rate(),rate);s=f.next;}}
 #[test]fn defer_and_recover(){let p=step();let s=root().advance(&p,10,0,0).unwrap().next;let mut q=p.clone();q.period.funding=500;let f=s.advance(&q,17,5,0).unwrap();assert!(f.blocked);assert_eq!(f.deferred_completion,5);assert_eq!(f.next.state().restoration().completed(),0);let g=f.next.advance(&p,0,5,0).unwrap();assert_eq!(g.next.state().restoration().completed(),5);}
 #[test]fn pending_survives_shock(){let p=step();let s=root().advance(&p,10,0,0).unwrap().next.advance(&p,0,5,0).unwrap().next.advance(&p,0,0,5).unwrap().next;let mut q=p.clone();q.period.funding=500;let f=s.advance(&q,17,0,0).unwrap();assert!(f.blocked);assert_eq!(f.regeneration.activated,[10,5,10,5]);assert_eq!(f.regeneration.queued,[0;4]);}
 #[test]fn invalid_ancestry(){let mut p=step();p.period.funding=0;assert!(root().advance(&p,0,1,0).is_err());}
 #[test]fn cycles(){let mut s=root();for t in 0..360{let mut p=step();if t%30<10{p.period.funding=500;p.resources.inflow=[0;4];}let r=s.state().restoration();let f=s.advance(&p,17,r.funded()-r.completed(),r.completed()-r.accepted()).unwrap();assert!(!f.blocked||f.regeneration.lifecycle.expenditure.units==0);assert_eq!(f.regeneration.lifecycle.residual_harm+f.next.state().restoration().accepted(),17);s=f.next;}assert_eq!(s.state().restoration().accepted(),17);}
}

// UEP-242R: explicit canonical state encoding.
impl Recovery{pub(crate) fn state_bytes(&self,b:&mut Vec<u8>){self.state.state_bytes(b);crate::state_hash::num(b,self.rate);crate::state_hash::num(b,self.clear)}}
