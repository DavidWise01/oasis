//! UEP-227R: finite-horizon equilibrium diagnostics, not a proof of sustainability. .dlw
use crate::{entitlement::Protected,bridge::Shares,dividend::Revenue,capacity::Input,population::Period,arrears};
#[derive(Clone,Debug,PartialEq,Eq)]
pub struct Step{pub period:Period,pub restitution:Shares,pub revenue:Revenue,pub dividend_cap:u64,pub resources:Input}
#[derive(Clone,Debug,PartialEq,Eq)]
pub struct Observation{pub epoch:u64,pub arrears:u64,pub unattributed:u64,pub unreserved:Shares,pub public_reserve:u64,pub stock:[u64;4],pub gain:[u64;4],pub harm:u64,pub current_shortfall:u64,pub unmet:[u64;4],pub historical_reserved:u64,pub candidate:u64}
#[derive(Clone,Debug,PartialEq,Eq)]
pub struct Report{pub next:Protected,pub observations:Vec<Observation>,pub protected_tail:usize,pub stationary_tail:usize,pub unresolved:bool}
fn same(a:&Observation,b:&Observation)->bool{a.arrears==b.arrears&&a.unreserved==b.unreserved&&a.public_reserve==b.public_reserve&&a.stock==b.stock&&a.gain==b.gain&&a.harm==b.harm&&a.candidate==b.candidate}
pub fn run(start:&Protected,steps:&[Step])->Result<Report,&'static str>{
 if steps.is_empty()||steps.len()>360{return Err("horizon")}
 let mut state=start.clone();let mut observations:Vec<Observation>=Vec::new();let mut protected_tail=0;let mut stationary_tail=0;
 for s in steps{
  let audit=arrears::advance(state.economy().bridge().population(),&s.period)?;
  let f=state.advance(&s.period,s.restitution.clone(),&s.revenue,s.dividend_cap,&s.resources)?;
  if audit.settlement!=f.economic.universal{return Err("arrears parity")}
  let u=&f.economic.universal;
  let o=Observation{epoch:u.closing.epoch,arrears:u.closing.outstanding()?,unattributed:u.closing.unattributed,unreserved:f.next.economy().bridge().outstanding(),public_reserve:f.next.economy().reserve(),stock:f.physical.next.stock(),gain:f.physical.next.gain(),harm:f.physical.next.harm(),current_shortfall:u.current_due-u.current_funded,unmet:f.physical.unmet,historical_reserved:audit.total_reserved,candidate:f.physical.work};
  if !f.physical.blocked{protected_tail+=1;stationary_tail=if observations.last().map_or(false,|p|same(p,&o))&&protected_tail>1{stationary_tail+1}else{1};}else{protected_tail=0;stationary_tail=0;}
  observations.push(o);state=f.next;
 }
 let last=observations.last().ok_or("empty")?;
 let unresolved=last.arrears>0||last.unreserved.carbon>0||last.unreserved.ai>0||last.harm>0;
 Ok(Report{next:state,observations,protected_tail,stationary_tail,unresolved})
}
#[cfg(test)]
mod tests{
 use super::*;use crate::{bridge::Bridge,dividend::Economy};
 fn root()->Protected{Protected::new(Economy::new(Bridge::genesis()))}
 fn step(funding:u64)->Step{Step{period:Period{enter:vec![],depart:vec![],award:100,funding},restitution:Shares::default(),revenue:Revenue{public_equity:0,licensing:0,automation_royalties:0,infrastructure_return:0},dividend_cap:100,resources:Input{inflow:[20;4],essential:[20;4],decay_bps:2000,work_ceiling:17}}}
 #[test]fn stationary_not_resolved(){let r=run(&root(),&vec![step(600);360]).unwrap();assert!(r.stationary_tail>300);assert!(r.unresolved);assert_eq!(r.observations.last().unwrap().arrears,400);}
 #[test]fn scarcity_not_equilibrium(){let r=run(&root(),&vec![step(500);360]).unwrap();assert_eq!(r.stationary_tail,0);assert_eq!(r.observations.last().unwrap().arrears,36400);}
 #[test]fn deterministic_prefix(){let s=root();let steps=vec![step(600);24];let a=run(&s,&steps).unwrap();let b=run(&s,&steps[..12]).unwrap();assert_eq!(a.observations[..12],b.observations[..]);assert_eq!(a,run(&s,&steps).unwrap());}
 #[test]fn invalid_horizon(){assert!(run(&root(),&[]).is_err());assert!(run(&root(),&vec![step(600);361]).is_err());}
}
