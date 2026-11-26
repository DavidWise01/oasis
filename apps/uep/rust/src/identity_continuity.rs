//! UEP-254R: identity continuity audit across immutable segment transitions. .dlw
use crate::{population::{Population,Period},executable::Request,linked_segment::{Anchor,Segment},cross_arrears::{self,Audit}};
use std::collections::BTreeSet;
#[derive(Clone,Debug,PartialEq,Eq)]
pub struct IdentityDelta{pub entered:BTreeSet<String>,pub departed:BTreeSet<String>,pub retained:BTreeSet<String>}
pub fn verify(open:&Population,close:&Population,p:&Period)->Result<IdentityDelta,&'static str>{
 let entered:BTreeSet<_>=p.enter.iter().cloned().collect();let departed:BTreeSet<_>=p.depart.iter().cloned().collect();
 if entered.len()!=p.enter.len()||departed.len()!=p.depart.len()||!entered.is_disjoint(&open.known)||!departed.is_subset(&open.active){return Err("identity transition")}
 let retained:BTreeSet<_>=open.active.difference(&departed).cloned().collect();
 let active:BTreeSet<_>=retained.union(&entered).cloned().collect();
 let known:BTreeSet<_>=open.known.union(&entered).cloned().collect();
 if close.active!=active||close.known!=known||Some(close.epoch)!=open.epoch.checked_add(1)||close.unattributed!=open.unattributed{return Err("identity continuity")}
 if close.lots.iter().any(|l|!known.contains(&l.id)||l.origin>close.epoch||l.amount==0||(entered.contains(&l.id)&&l.origin<close.epoch)){return Err("beneficiary ancestry")}
 Ok(IdentityDelta{entered,departed,retained})
}
pub fn append(s:&Segment,r:&Request)->Result<(Segment,Audit,IdentityDelta),&'static str>{
 let(n,a)=cross_arrears::append(s,r)?;
 let d=verify(s.universe().population_ledger(),n.universe().population_ledger(),&r.present.period)?;
 Ok((n,a,d))
}
pub fn boundary(s:&Segment,c:&Anchor)->Result<Segment,&'static str>{cross_arrears::boundary(s,c)}
#[cfg(test)]mod tests{
 use super::*;use crate::{population::settle,evidence::Ledger,replay_archive::Archive,equilibrium::Step,bridge::Shares,dividend::Revenue,capacity::Input};
 fn req(f:u64)->Request{let s=Step{period:Period{enter:vec![],depart:vec![],award:100,funding:f},restitution:Shares::default(),revenue:Revenue{public_equity:0,licensing:0,automation_royalties:0,infrastructure_return:0},dividend_cap:0,resources:Input{inflow:[100;4],essential:[20;4],decay_bps:0,work_ceiling:17}};Request{present:s.clone(),requested:0,complete:0,accept:0,future:vec![s]}}
 #[test]fn replacement(){let a=Population::phase_ix();let mut p=req(0).present.period;p.enter=vec!["G_1".into()];p.depart=vec!["A_1".into()];let b=settle(&a,&p).unwrap().closing;let d=verify(&a,&b,&p).unwrap();assert_eq!(d.retained.len(),5);assert!(b.known.contains("A_1"));assert!(!b.active.contains("A_1"));}
 #[test]fn erased_identity(){let a=Population::phase_ix();let p=req(600).present.period;let mut b=settle(&a,&p).unwrap().closing;b.known.remove("A_0");assert!(verify(&a,&b,&p).is_err());}
 #[test]fn reassigned_debt(){let a=settle(&Population::phase_ix(),&req(0).present.period).unwrap().closing;let mut p=req(600).present.period;p.enter=vec!["G_1".into()];p.depart=vec!["A_1".into()];let mut b=settle(&a,&p).unwrap().closing;b.lots[0].id="G_1".into();assert!(verify(&a,&b,&p).is_err());}
 #[test]fn duplicate_reentry(){let a=Population::phase_ix();let mut p=req(600).present.period;p.enter=vec!["A_0".into()];assert!(verify(&a,&a,&p).is_err());p.enter=vec!["G_1".into(),"G_1".into()];assert!(verify(&a,&a,&p).is_err());}
 #[test]fn actual_rollover(){let mut a=Archive::new(Ledger::default(),[0;32]).unwrap();for _ in 0..360{a=a.append(&req(600)).unwrap()}let mut s=Segment::from_root(&a,&a.checkpoint().unwrap()).unwrap();let mut r=req(0);r.present.period.depart=vec!["A_1".into()];r.present.period.enter=vec!["G_1".into()];s=append(&s,&r).unwrap().0;for _ in 1..360{s=s.append(&req(600)).unwrap()}let c=s.anchor().unwrap();let n=boundary(&s,&c).unwrap();let mut reuse=req(600);reuse.present.period.enter=vec!["A_1".into()];reuse.present.period.depart=vec!["G_1".into()];assert!(append(&n,&reuse).is_err());let mut r=req(600);r.present.period.enter=vec!["G_2".into()];r.present.period.depart=vec!["G_1".into()];let(n,_,d)=append(&n,&r).unwrap();assert_eq!(n.universe().total_observations(),721);assert_eq!(d.retained.len(),5);let p=n.universe().population_ledger();assert!(p.known.contains("A_1")&&p.known.contains("G_1")&&p.active.contains("G_2"));assert_eq!(cross_arrears::attributable(p,"G_1").unwrap(),100);}
}
