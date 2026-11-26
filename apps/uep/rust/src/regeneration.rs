//! UEP-236R: delayed productive yield with explicit cap loss and decay. .dlw
use crate::{restoration::{Restoration,Frame as Lifecycle},evidence::Ledger,equilibrium::Step,capacity::YIELD};
#[derive(Clone,Debug,PartialEq,Eq)]
pub struct Regeneration{state:Restoration,gain:[u64;4]}
#[derive(Clone,Debug,PartialEq,Eq)]
pub struct Frame{pub next:Regeneration,pub lifecycle:Lifecycle,pub activated:[u64;4],pub cap_loss:[u64;4],pub decay:[u64;4],pub queued:[u64;4]}
impl Regeneration{
 pub fn new(l:&Ledger,head:[u8;32])->Result<Self,&'static str>{Ok(Self{state:Restoration::new(l,head)?,gain:[15,0,0,0]})}
 pub fn restoration(&self)->&Restoration{&self.state}
 pub fn advance(&self,s:&Step,requested:u64,complete:u64,accept:u64)->Result<Frame,&'static str>{
  let pending=self.state.pending_yield();
  let f=self.state.advance_regenerative(s,requested,complete,accept)?;
  let mut activated=[0;4];let mut cap_loss=[0;4];let mut decay=[0;4];
  let gain=f.expenditure.physical.next.gain();
  let queued=f.next.pending_yield();
  for k in 0..4{
   let raw=self.gain[k].checked_add(pending[k]).ok_or("gain overflow")?;
   let capped=raw.min(30);
   activated[k]=capped.checked_sub(self.gain[k]).ok_or("activation")?;
   cap_loss[k]=raw-capped;
   decay[k]=(capped*s.resources.decay_bps+9999)/10000;
   if gain[k]!=capped-decay[k]||queued[k]!=f.accepted_now*YIELD[k]||activated[k]+cap_loss[k]!=pending[k]{return Err("yield parity")}
  }
  let next=Self{state:f.next.clone(),gain};
  Ok(Frame{next,lifecycle:f,activated,cap_loss,decay,queued})
 }
}
#[cfg(test)]
mod tests{
 use super::*;use crate::{evidence::Event,restitution::Assessment,capacity::Input,dividend::Revenue,population::Period,bridge::Shares};
 fn root()->Regeneration{let l=Ledger::default().append(Event::Estimate{id:"e".into(),valuation:10000,assessment:Assessment{target:"synthetic".into(),evidence_refs:vec!["source".into()],human_observation_ref:"h".into(),ai_observation_ref:"a".into(),positive:[999;22],negative:[0;22]}}).unwrap().append(Event::AcceptModel{id:"a".into(),estimate_id:"e".into(),decision_ref:"model".into()}).unwrap();Regeneration::new(&l,l.head()).unwrap()}
 fn step()->Step{Step{period:Period{enter:vec![],depart:vec![],award:100,funding:600},restitution:Shares{carbon:100,ai:0},revenue:Revenue{public_equity:0,licensing:0,automation_royalties:0,infrastructure_return:0},dividend_cap:0,resources:Input{inflow:[40;4],essential:[20;4],decay_bps:0,work_ceiling:17}}}
 fn accepted(n:u64)->Frame{let p=step();root().advance(&p,n,0,0).unwrap().next.advance(&p,0,n,0).unwrap().next.advance(&p,0,0,n).unwrap()}
 #[test]fn delayed(){let f=accepted(5);assert_eq!(f.queued,[10,5,10,5]);assert_eq!(f.activated,[0;4]);assert_eq!(f.lifecycle.expenditure.physical.next.gain(),[15,0,0,0]);let g=f.next.advance(&step(),0,0,0).unwrap();assert_eq!(g.activated,[10,5,10,5]);assert_eq!(g.queued,[0;4]);}
 #[test]fn cap(){let f=accepted(17).next.advance(&step(),0,0,0).unwrap();assert_eq!(f.cap_loss,[19,0,4,0]);assert_eq!(f.lifecycle.expenditure.physical.next.gain(),[30,17,30,17]);}
 #[test]fn decay(){let mut p=step();p.resources.decay_bps=2000;let f=accepted(5).next.advance(&p,0,0,0).unwrap();assert_eq!(f.decay,[5,1,2,1]);assert_eq!(f.lifecycle.expenditure.physical.next.gain(),[20,4,8,4]);}
 #[test]fn no_replay_credit(){let p=step();let f=accepted(5).next.advance(&p,0,0,0).unwrap();let g=f.next.advance(&p,0,0,0).unwrap();assert_eq!(g.activated,[0;4]);assert_eq!(g.queued,[0;4]);assert!(g.next.advance(&p,0,0,5).is_err());}
 #[test]fn long_horizon(){let mut s=root();let mut p=step();p.resources.decay_bps=1000;for _ in 0..360{let r=s.restoration();let f=s.advance(&p,17,r.funded()-r.completed(),r.completed()-r.accepted()).unwrap();assert!(f.lifecycle.expenditure.physical.next.gain().iter().all(|&x|x<=30));assert_eq!(f.lifecycle.residual_harm+f.next.restoration().accepted(),17);s=f.next;}assert_eq!(s.restoration().accepted(),17);}
}
