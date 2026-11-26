//! UEP-235R: aggregate funded/completed/accepted work ledger. Synthetic only. .dlw
use crate::{expenditure::{Execution,Frame as Expenditure},evidence::Ledger,equilibrium::Step};
#[derive(Clone,Debug,PartialEq,Eq)]
pub struct Restoration{execution:Execution,completed:u64,accepted:u64}
#[derive(Clone,Debug,PartialEq,Eq)]
pub struct Frame{pub next:Restoration,pub expenditure:Expenditure,pub completed_now:u64,pub accepted_now:u64,pub unfinished:u64,pub awaiting_acceptance:u64,pub residual_harm:u64}
impl Restoration{
 pub fn new(l:&Ledger,head:[u8;32])->Result<Self,&'static str>{Ok(Self{execution:Execution::new(l,head)?,completed:0,accepted:0})}
 pub fn funded(&self)->u64{self.execution.funded_units()}
 pub fn completed(&self)->u64{self.completed}
 pub fn accepted(&self)->u64{self.accepted}
 /// Completion can consume only opening funded work; acceptance only opening completed work.
 /// No evidence authenticity or individual case attribution is implied.
 pub fn advance(&self,s:&Step,requested:u64,complete:u64,accept:u64)->Result<Frame,&'static str>{
  if complete>self.funded().checked_sub(self.completed).ok_or("completion ancestry")?{return Err("unfunded completion")}
  if accept>self.completed.checked_sub(self.accepted).ok_or("acceptance ancestry")?{return Err("uncompleted acceptance")}
  let e=self.execution.advance(s,requested)?;
  if e.physical.blocked&&(complete>0||accept>0){return Err("protection hold")}
  let completed=self.completed.checked_add(complete).ok_or("completion overflow")?;
  let accepted=self.accepted.checked_add(accept).ok_or("acceptance overflow")?;
  let funded=e.next.funded_units();
  let unfinished=funded.checked_sub(completed).ok_or("funded balance")?;
  let awaiting_acceptance=completed.checked_sub(accepted).ok_or("completion balance")?;
  // Capacity still owns the frozen original harm; this is the derived lifecycle residual.
  let residual_harm=e.physical.next.harm().checked_sub(accepted).ok_or("harm balance")?;
  let next=Self{execution:e.next.clone(),completed,accepted};
  Ok(Frame{next,expenditure:e,completed_now:complete,accepted_now:accept,unfinished,awaiting_acceptance,residual_harm})
 }
}
#[cfg(test)]
mod tests{
 use super::*;use crate::{evidence::Event,restitution::Assessment,capacity::Input,dividend::Revenue,population::Period,bridge::Shares};
 fn root()->Restoration{let l=Ledger::default().append(Event::Estimate{id:"e".into(),valuation:10000,assessment:Assessment{target:"synthetic".into(),evidence_refs:vec!["source".into()],human_observation_ref:"h".into(),ai_observation_ref:"a".into(),positive:[999;22],negative:[0;22]}}).unwrap().append(Event::AcceptModel{id:"a".into(),estimate_id:"e".into(),decision_ref:"model".into()}).unwrap();Restoration::new(&l,l.head()).unwrap()}
 fn step()->Step{Step{period:Period{enter:vec![],depart:vec![],award:100,funding:600},restitution:Shares{carbon:10,ai:100},revenue:Revenue{public_equity:0,licensing:0,automation_royalties:0,infrastructure_return:0},dividend_cap:0,resources:Input{inflow:[40;4],essential:[20;4],decay_bps:2000,work_ceiling:17}}}
 #[test]fn ordered_stages(){let p=step();let f=root().advance(&p,5,0,0).unwrap();assert_eq!((f.unfinished,f.residual_harm),(5,17));let f=f.next.advance(&p,0,5,0).unwrap();assert_eq!((f.awaiting_acceptance,f.residual_harm),(5,17));let f=f.next.advance(&p,0,0,5).unwrap();assert_eq!((f.awaiting_acceptance,f.residual_harm),(0,12));}
 #[test]fn no_same_epoch_credit(){assert!(root().advance(&step(),5,5,0).is_err());let f=root().advance(&step(),5,0,0).unwrap();assert!(f.next.advance(&step(),0,5,5).is_err());}
 #[test]fn no_duplicate_acceptance(){let p=step();let s=root().advance(&p,1,0,0).unwrap().next.advance(&p,0,1,0).unwrap().next.advance(&p,0,0,1).unwrap().next;assert!(s.advance(&p,0,0,1).is_err());}
 #[test]fn scarcity_hold(){let s=root().advance(&step(),5,0,0).unwrap().next;let mut p=step();p.period.funding=500;assert!(s.advance(&p,0,1,0).is_err());assert_eq!(s.advance(&p,5,0,0).unwrap().expenditure.units,0);}
 #[test]fn long_horizon(){let mut s=root();let p=step();for _ in 0..360{let f=s.advance(&p,17,s.funded()-s.completed(),s.completed()-s.accepted()).unwrap();assert_eq!(f.residual_harm+f.next.accepted(),17);assert!(f.next.accepted()<=f.next.completed()&&f.next.completed()<=f.next.funded());s=f.next;}assert_eq!((s.funded(),s.completed(),s.accepted()),(17,17,17));}
}

// UEP-236R: acceptance queues yield in closing state only.
impl Restoration{
 pub(crate) fn advance_regenerative(&self,s:&Step,requested:u64,complete:u64,accept:u64)->Result<Frame,&'static str>{
  let mut f=self.advance(s,requested,complete,accept)?;
  f.next.execution.queue_yield(f.accepted_now)?;
  Ok(f)
 }
 pub(crate) fn pending_yield(&self)->[u64;4]{self.execution.pending_yield()}
}

// UEP-242R: explicit canonical state encoding.
impl Restoration{pub(crate) fn state_bytes(&self,b:&mut Vec<u8>){self.execution.state_bytes(b);crate::state_hash::num(b,self.completed);crate::state_hash::num(b,self.accepted)}}
