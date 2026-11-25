//! UEP-228R: deterministic shock and recovery diagnostics. .dlw
use crate::{equilibrium::{run,Step,Report},entitlement::Protected};
#[derive(Clone,Debug,PartialEq,Eq)]
pub struct Stress{pub report:Report,pub blocked:usize,pub longest_block:usize,pub recovered_episodes:usize,pub open_episode:bool,pub peak_arrears:u64}
pub fn evaluate(start:&Protected,steps:&[Step])->Result<Stress,&'static str>{
 let report=run(start,steps)?;let mut blocked=0;let mut longest_block=0;let mut streak=0;let mut recovered_episodes=0;let mut peak_arrears=start.economy().bridge().population().outstanding()?;
 for o in &report.observations{
  let hold=o.current_shortfall>0||o.unmet.iter().any(|&x|x>0)||o.stock.iter().any(|&x|x<10);
  if hold{if o.candidate!=0{return Err("unsafe candidate")}blocked+=1;streak+=1;longest_block=longest_block.max(streak);}
  else if streak>0{recovered_episodes+=1;streak=0;}
  peak_arrears=peak_arrears.max(o.arrears);
 }
 Ok(Stress{report,blocked,longest_block,recovered_episodes,open_episode:streak>0,peak_arrears})
}
/// 12 deterministic 30-period cycles. Replace one person at each cycle boundary.
/// Shock duration, inflow and funding are explicit synthetic parameters.
pub fn schedule(start:&Protected,duration:usize,inflow:u64,funding:u64)->Result<Vec<Step>,&'static str>{
 use crate::{bridge::Shares,dividend::Revenue,capacity::Input,population::Period};
 if duration>30||inflow>40||funding>750{return Err("shock bounds")}
 let mut active=start.economy().bridge().population().active.clone();
 let mut known=start.economy().bridge().population().known.clone();
 let mut steps=Vec::new();
 for t in 0..360{let shock=t%30<duration;let mut depart=Vec::new();let mut enter=Vec::new();
 if t%30==0{if let Some(id)=active.iter().next().cloned(){active.remove(&id);depart.push(id);let id=format!("stress_{}_{}",start.economy().bridge().population().epoch,t);if !known.insert(id.clone()){return Err("identity collision")}active.insert(id.clone());enter.push(id);}}
 let count=active.len() as u64;let full=count.checked_mul(100).ok_or("award overflow")?;
 steps.push(Step{period:Period{enter,depart,award:100,funding:if shock{funding.min(full)}else{full.checked_add(150).ok_or("funding overflow")?}},restitution:Shares{carbon:100,ai:25},revenue:Revenue{public_equity:if shock{0}else{600},licensing:0,automation_royalties:0,infrastructure_return:0},dividend_cap:100,resources:Input{inflow:[if shock{inflow}else{40};4],essential:[20;4],decay_bps:2000,work_ceiling:17}});
 }Ok(steps)
}
#[cfg(test)]
mod tests{
 use super::*;use crate::{bridge::Bridge,dividend::Economy};
 fn root()->Protected{Protected::new(Economy::new(Bridge::genesis()))}
 #[test]fn shock_recovery(){let s=root();let r=evaluate(&s,&schedule(&s,10,0,500).unwrap()).unwrap();assert!(r.blocked>=120);assert_eq!(r.recovered_episodes,12);assert!(!r.open_episode);assert_eq!(r.report.observations.last().unwrap().unattributed,400);}
 #[test]fn permanent_shock(){let s=root();let r=evaluate(&s,&schedule(&s,30,0,0).unwrap()).unwrap();assert_eq!(r.blocked,360);assert_eq!(r.longest_block,360);assert!(r.open_episode);}
 #[test]fn deterministic(){let s=root();let p=schedule(&s,5,10,500).unwrap();assert_eq!(evaluate(&s,&p).unwrap(),evaluate(&s,&p).unwrap());assert_eq!(p.iter().map(|x|x.period.enter.len()).sum::<usize>(),12);}
 #[test]fn bounds(){assert!(schedule(&root(),31,0,0).is_err());}
}
