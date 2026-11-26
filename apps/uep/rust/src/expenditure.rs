//! UEP-234R: synthetic expenditure, not completion or acceptance. .dlw
use crate::{capacity::{Capacity,Frame as Physical,COST},dividend::{Economy,Frame as Economic},bridge::Bridge,evidence::Ledger,equilibrium::Step,population::settle};
#[derive(Clone,Debug,PartialEq,Eq)]
pub struct Execution{economy:Economy,capacity:Capacity,spent_cents:u64,funded_units:u64}
#[derive(Clone,Debug,PartialEq,Eq)]
pub struct Frame{pub next:Execution,pub economic:Economic,pub physical:Physical,pub resources_spent:[u64;4],pub units:u64,pub carbon_spent:u64}
impl Execution{
 pub fn new(l:&Ledger,head:[u8;32])->Result<Self,&'static str>{Ok(Self{economy:Economy::new(Bridge::genesis()).sync(l,head)?,capacity:Capacity::genesis(),spent_cents:0,funded_units:0})}
 pub fn spent_cents(&self)->u64{self.spent_cents}
 pub fn funded_units(&self)->u64{self.funded_units}
 pub fn advance(&self,s:&Step,requested:u64)->Result<Frame,&'static str>{
  let baseline=settle(self.economy.bridge().population(),&s.period)?;
  let e=self.economy.advance(&s.period,s.restitution.clone(),&s.revenue,s.dividend_cap)?;
  if e.universal!=baseline{return Err("universal offset")}
  let budget=e.next.bridge().funded().carbon.checked_sub(self.spent_cents).ok_or("carbon overspend")?;
  let remaining=self.capacity.harm().checked_sub(self.funded_units).ok_or("work ceiling")?;
  let (p,resources,units)=self.capacity.spend_candidate(&s.resources,&baseline,requested,budget,remaining)?;
  let carbon=units.checked_mul(2).ok_or("carbon cost")?;
  let spent_cents=self.spent_cents.checked_add(carbon).ok_or("spent overflow")?;
  let funded_units=self.funded_units.checked_add(units).ok_or("units overflow")?;
  if spent_cents>e.next.bridge().funded().carbon||funded_units>self.capacity.harm()||p.next.harm()!=self.capacity.harm()||p.blocked&&units!=0{return Err("expenditure gate")}
  for k in 0..4{if resources[k]!=units*COST[k]{return Err("cost parity")}}
  let next=Self{economy:e.next.clone(),capacity:p.next.clone(),spent_cents,funded_units};
  Ok(Frame{next,economic:e,physical:p,resources_spent:resources,units,carbon_spent:carbon})
 }
}
#[cfg(test)]
mod tests{
 use super::*;use crate::{evidence::Event,restitution::Assessment,capacity::Input,dividend::Revenue,population::Period,bridge::Shares};
 fn root()->Execution{let l=Ledger::default().append(Event::Estimate{id:"e".into(),valuation:10000,assessment:Assessment{target:"synthetic".into(),evidence_refs:vec!["source".into()],human_observation_ref:"h".into(),ai_observation_ref:"a".into(),positive:[999;22],negative:[0;22]}}).unwrap().append(Event::AcceptModel{id:"a".into(),estimate_id:"e".into(),decision_ref:"model".into()}).unwrap();Execution::new(&l,l.head()).unwrap()}
 fn step()->Step{Step{period:Period{enter:vec![],depart:vec![],award:100,funding:600},restitution:Shares{carbon:10,ai:100},revenue:Revenue{public_equity:1000,licensing:0,automation_royalties:0,infrastructure_return:0},dividend_cap:100,resources:Input{inflow:[20;4],essential:[20;4],decay_bps:2000,work_ceiling:17}}}
 #[test]fn spend(){let s=root();let f=s.advance(&step(),17).unwrap();assert_eq!(f.units,5);assert_eq!(f.resources_spent,[10,5,15,10]);assert_eq!(f.physical.next.stock(),[70,75,55,70]);assert_eq!(f.physical.next.harm(),17);assert_eq!(f.carbon_spent,10);}
 #[test]fn blocked(){let mut p=step();p.period.funding=500;assert_eq!(root().advance(&p,17).unwrap().units,0);}
 #[test]fn independent_funds(){let mut p=step();p.restitution.carbon=0;assert_eq!(root().advance(&p,17).unwrap().units,0);}
 #[test]fn no_repeat_spend(){let mut s=root();for _ in 0..360{s=s.advance(&step(),17).unwrap().next;}assert_eq!(s.funded_units(),17);assert_eq!(s.spent_cents(),34);}
 #[test]fn grid(){for funding in [0,500,750]{for demand in [10,40,90]{for carbon in [0,2,100]{let mut s=root();for _ in 0..360{let mut p=step();p.period.funding=funding;p.resources.essential=[demand;4];p.restitution.carbon=carbon;let f=s.advance(&p,17).unwrap();assert_eq!(f.physical.next.harm(),17);if f.units>0{assert!(f.physical.next.stock().iter().all(|&v|v>=10));}s=f.next;}}}}}
}

// UEP-236R: internal lifecycle handoff, not external authorization.
impl Execution{
 pub(crate) fn queue_yield(&mut self,units:u64)->Result<(),&'static str>{self.capacity.queue_yield(units)}
 pub(crate) fn pending_yield(&self)->[u64;4]{self.capacity.pending_yield()}
}

// UEP-242R: explicit canonical state encoding.
impl Execution{pub(crate) fn state_bytes(&self,b:&mut Vec<u8>){self.economy.state_bytes(b);self.capacity.state_bytes(b);crate::state_hash::num(b,self.spent_cents);crate::state_hash::num(b,self.funded_units)}}
