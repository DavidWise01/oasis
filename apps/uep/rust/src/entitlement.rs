//! UEP-225R: unified entitlement protection, modeled reservations only. .dlw
use crate::{bridge::Shares,dividend::{Economy,Revenue,Frame as EconomicFrame},capacity::{Capacity,Input,Frame as CapacityFrame},population::{Period,settle},evidence::Ledger};
#[derive(Clone,Debug,PartialEq,Eq)]
pub struct Protected{economy:Economy,capacity:Capacity}
#[derive(Clone,Debug,PartialEq,Eq)]
pub struct Frame{pub next:Protected,pub economic:EconomicFrame,pub physical:CapacityFrame}
impl Protected{
 pub fn new(economy:Economy)->Self{Self{economy,capacity:Capacity::genesis()}}
 pub fn economy(&self)->&Economy{&self.economy}
 pub fn sync(&self,l:&Ledger,head:[u8;32])->Result<Self,&'static str>{let mut n=self.clone();n.economy=n.economy.sync(l,head)?;Ok(n)}
 pub fn advance(&self,p:&Period,funds:Shares,revenue:&Revenue,cap:u64,input:&Input)->Result<Frame,&'static str>{
  let baseline=settle(self.economy.bridge().population(),p)?;
  let economic=self.economy.advance(p,funds,revenue,cap)?;
  if economic.universal!=baseline{return Err("universal offset")}
  let physical=self.capacity.advance(input,&baseline)?;
  if (baseline.current_funded<baseline.current_due||physical.unmet.iter().any(|&v|v>0))&&physical.work!=0{return Err("essential protection")}
  if baseline.awards.iter().any(|a|a.due!=p.award||a.funded>a.due){return Err("individual entitlement")}
  let next=Self{economy:economic.next.clone(),capacity:physical.next.clone()};
  Ok(Frame{next,economic,physical})
 }
}
#[cfg(test)]
mod tests{
 use super::*;use crate::{bridge::Bridge,evidence::Event,restitution::Assessment};
 fn root()->Protected{let l=Ledger::default().append(Event::Estimate{id:"e".into(),valuation:10000,assessment:Assessment{target:"synthetic".into(),evidence_refs:vec!["source".into()],human_observation_ref:"human".into(),ai_observation_ref:"ai".into(),positive:[999;22],negative:[0;22]}}).unwrap().append(Event::AcceptModel{id:"a".into(),estimate_id:"e".into(),decision_ref:"model".into()}).unwrap();Protected::new(Economy::new(Bridge::genesis())).sync(&l,l.head()).unwrap()}
 fn rev(n:u64)->Revenue{Revenue{public_equity:n,licensing:0,automation_royalties:0,infrastructure_return:0}}
 fn input(d:u64)->Input{Input{inflow:[20;4],essential:[d;4],decay_bps:2000,work_ceiling:17}}
 #[test]fn independent_dividend(){let s=root();let p=Period{enter:vec![],depart:vec![],award:100,funding:500};let f=s.advance(&p,Shares{carbon:1640,ai:410},&rev(1000),100,&input(20)).unwrap();assert_eq!(f.economic.universal.current_due,600);assert_eq!(f.economic.universal.current_funded,500);assert_eq!(f.economic.dividend_total,600);assert_eq!(f.physical.work,0);}
 #[test]fn scarcity_not_offset(){let s=root();let p=Period{enter:vec![],depart:vec![],award:100,funding:600};let f=s.advance(&p,Shares::default(),&rev(0),100,&input(100)).unwrap();assert!(f.physical.blocked);assert_eq!(f.economic.universal.current_funded,600);}
 #[test]fn turnover_grid(){for revenue in [0,300,1000]{for funding in [0,500,600]{for demand in [10,40,90]{let mut a=root();let mut b=root();for i in 0..360{let p=Period{depart:if i%30==0{a.economy().bridge().population().active.iter().cloned().collect()}else{vec![]},enter:if i%30==0{(0..6).map(|j|format!("g{i}_{j}")).collect()}else{vec![]},award:100,funding};let f=a.advance(&p,Shares{carbon:100,ai:25},&rev(revenue),100,&input(demand)).unwrap();let z=b.advance(&p,Shares::default(),&rev(0),100,&input(demand)).unwrap();assert_eq!(f.economic.universal,z.economic.universal);assert_eq!(f.physical,z.physical);assert_eq!(f.economic.universal.current_due,600);a=f.next;b=z.next;}}}}}
}
