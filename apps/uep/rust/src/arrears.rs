//! UEP-226R: chronological historical funding receipts; not proof of payment. .dlw
use crate::population::{Population,Period,Settlement,Lot,settle};
use std::collections::BTreeMap;
#[derive(Clone,Debug,PartialEq,Eq)]
pub struct Receipt{pub origin:u64,pub beneficiary:String,pub opening_index:usize,pub reserved:u64,pub remainder:u64,pub departed:bool}
#[derive(Clone,Debug,PartialEq,Eq)]
pub struct Audit{pub settlement:Settlement,pub receipts:Vec<Receipt>,pub total_reserved:u64}
pub fn advance(s:&Population,p:&Period)->Result<Audit,&'static str>{
 let settlement=settle(s,p)?;
 let mut left=p.funding.checked_sub(settlement.current_funded).ok_or("funding")?;
 let mut receipts=Vec::new();let mut closing=Vec::new();let mut by_id=BTreeMap::<String,u64>::new();let mut total=0u64;
 for (index,lot) in s.lots.iter().enumerate(){
  let reserved=left.min(lot.amount);left-=reserved;let remainder=lot.amount-reserved;
  if reserved>0{receipts.push(Receipt{origin:lot.origin,beneficiary:lot.id.clone(),opening_index:index,reserved,remainder,departed:!settlement.closing.active.contains(&lot.id)});let entry=by_id.entry(lot.id.clone()).or_default();*entry=entry.checked_add(reserved).ok_or("receipt overflow")?;total=total.checked_add(reserved).ok_or("total overflow")?;}
  if remainder>0{closing.push(Lot{origin:lot.origin,id:lot.id.clone(),amount:remainder});}
 }
 for a in &settlement.awards{if a.funded<a.due{closing.push(Lot{origin:settlement.closing.epoch,id:a.id.clone(),amount:a.due-a.funded});}}
 if closing!=settlement.closing.lots||by_id!=settlement.historical_reserved||left!=settlement.unallocated||s.unattributed!=settlement.closing.unattributed{return Err("retirement parity")}
 Ok(Audit{settlement,receipts,total_reserved:total})
}
#[cfg(test)]
mod tests{
 use super::*;
 fn period(funding:u64)->Period{Period{enter:vec![],depart:vec![],award:100,funding}}
 #[test]fn chronological_partial(){let a=settle(&Population::phase_ix(),&period(0)).unwrap();let b=settle(&a.closing,&period(0)).unwrap();let r=advance(&b.closing,&period(750)).unwrap();assert_eq!(r.total_reserved,150);assert_eq!(r.receipts.len(),2);assert_eq!(r.receipts[0].origin,7);assert_eq!(r.receipts[1].remainder,50);assert_eq!(r.settlement.closing.unattributed,400);}
 #[test]fn departed_identity(){let a=settle(&Population::phase_ix(),&period(0)).unwrap();let mut p=period(700);p.depart=vec!["A_1".into()];p.enter=vec!["E_0".into()];let r=advance(&a.closing,&p).unwrap();assert_eq!(r.receipts[0].beneficiary,"A_1");assert!(r.receipts[0].departed);assert_eq!(r.receipts[0].reserved,100);}
 #[test]fn current_priority(){let a=settle(&Population::phase_ix(),&period(0)).unwrap();let r=advance(&a.closing,&period(500)).unwrap();assert!(r.receipts.is_empty());assert_eq!(r.settlement.current_funded,500);assert_eq!(r.settlement.closing.outstanding().unwrap(),1100);}
 #[test]fn grid(){for first in [0,300,600]{for second in [0,300,600,750,1200]{let a=settle(&Population::phase_ix(),&period(first)).unwrap();let r=advance(&a.closing,&period(second)).unwrap();assert_eq!(r.total_reserved,(second.saturating_sub(600)).min(600-first));assert_eq!(r.settlement.closing.unattributed,400);}}}
}
