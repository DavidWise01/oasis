//! UEP-253R: cross-archive obligation audit; reservations are not payments. .dlw
use crate::{executable::Request,linked_segment::{Anchor,Segment},arrears::{self,Receipt},population::Population,state_hash};
#[derive(Clone,Debug,PartialEq,Eq)]
pub struct Audit{pub opening:u64,pub due:u64,pub current_funded:u64,pub historical_reserved:u64,pub closing:u64,pub receipts:Vec<Receipt>}
pub fn boundary(s:&Segment,expected:&Anchor)->Result<Segment,&'static str>{
 let n=s.compact_boundary(expected)?;
 if n.universe().population_ledger()!=s.universe().population_ledger()||state_hash::encode(n.universe())?!=state_hash::encode(s.universe())?{return Err("boundary obligation mismatch")}Ok(n)
}
pub fn append(s:&Segment,r:&Request)->Result<(Segment,Audit),&'static str>{
 let p=s.universe().population_ledger();let opening=p.outstanding()?;
 let a=arrears::advance(p,&r.present.period)?;let n=s.append(r)?;
 let q=n.universe().population_ledger();let o=n.universe().observations().last().ok_or("missing observation")?;
 let closing=q.outstanding()?;
 if q!=&a.settlement.closing||o.due!=a.settlement.current_due||o.funded!=a.settlement.current_funded||o.historical_reserved!=a.total_reserved||o.arrears!=closing||q.unattributed!=p.unattributed{return Err("integrated obligation parity")}
 if u128::from(opening)+u128::from(o.due)!=u128::from(closing)+u128::from(o.funded)+u128::from(a.total_reserved){return Err("conservation")}
 if o.funded!=o.due.min(r.present.period.funding){return Err("current priority")}
 let audit=Audit{opening,due:o.due,current_funded:o.funded,historical_reserved:a.total_reserved,closing,receipts:a.receipts};
 Ok((n,audit))
}
pub fn attributable(p:&Population,id:&str)->Result<u64,&'static str>{p.lots.iter().filter(|l|l.id==id).try_fold(0u64,|a,l|a.checked_add(l.amount).ok_or("amount overflow"))}
#[cfg(test)]mod tests{
 use super::*;use crate::{evidence::Ledger,replay_archive::Archive,equilibrium::Step,population::Period,bridge::Shares,dividend::Revenue,capacity::Input};
 fn req(funding:u64)->Request{let s=Step{period:Period{enter:vec![],depart:vec![],award:100,funding},restitution:Shares::default(),revenue:Revenue{public_equity:0,licensing:0,automation_royalties:0,infrastructure_return:0},dividend_cap:0,resources:Input{inflow:[100;4],essential:[20;4],decay_bps:0,work_ceiling:17}};Request{present:s.clone(),requested:0,complete:0,accept:0,future:vec![s]}}
 fn root()->Segment{let mut a=Archive::new(Ledger::default(),[0;32]).unwrap();for _ in 0..360{a=a.append(&req(600)).unwrap()}Segment::from_root(&a,&a.checkpoint().unwrap()).unwrap()}
 #[test]fn rollover_obligations(){let mut s=root();for _ in 0..359{s=s.append(&req(600)).unwrap()}s=s.append(&req(0)).unwrap();let anchor=s.anchor().unwrap();let bytes=s.encode().unwrap();let n=boundary(&s,&anchor).unwrap();assert_eq!(n.universe().total_observations(),720);assert!(n.universe().observations().is_empty());assert_eq!(n.universe().population_ledger().outstanding().unwrap(),1000);assert_eq!(s.encode().unwrap(),bytes);let mut r=req(700);r.present.period.depart=vec!["A_1".into()];r.present.period.enter=vec!["G_1".into()];let(n,a)=append(&n,&r).unwrap();assert_eq!((a.due,a.current_funded,a.historical_reserved,a.closing),(600,600,100,900));assert_eq!(a.receipts[0].beneficiary,"A_1");assert!(a.receipts[0].departed);assert_eq!(a.receipts[0].origin,726);assert_eq!(attributable(n.universe().population_ledger(),"A_1").unwrap(),0);}
 #[test]fn shortage_priority(){let s=root().append(&req(0)).unwrap();let(_,a)=append(&s,&req(500)).unwrap();assert_eq!((a.opening,a.current_funded,a.historical_reserved,a.closing),(1000,500,0,1100));}
 #[test]fn departed_carry(){let s=root().append(&req(0)).unwrap();let mut r=req(600);r.present.period.depart=vec!["A_1".into()];r.present.period.enter=vec!["G_1".into()];let(n,_)=append(&s,&r).unwrap();assert_eq!(attributable(n.universe().population_ledger(),"A_1").unwrap(),100);let(_,a)=append(&n,&req(650)).unwrap();assert_eq!(a.receipts[0].remainder,50);assert!(a.receipts[0].departed);}
 #[test]fn unattributed_hold(){let s=root().append(&req(0)).unwrap();let(n,a)=append(&s,&req(2000)).unwrap();assert_eq!((a.historical_reserved,a.closing),(600,400));assert_eq!(n.universe().population_ledger().unattributed,400);}
 #[test]fn partial_boundary_rejected(){let s=root();assert!(boundary(&s,&s.anchor().unwrap()).is_err());}
}
