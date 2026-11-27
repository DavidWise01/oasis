//! UEP-262R: derived beneficiary balances; authoritative chronology unchanged. .dlw
use crate::{population::{Population,Period},arrears::{self,Audit}};
use std::collections::BTreeMap;
#[derive(Clone,Debug,PartialEq,Eq)]
pub struct Index{epoch:u64,balances:BTreeMap<String,u64>,identified:u64,unattributed:u64}
impl Index{
 pub fn build(p:&Population)->Result<Self,&'static str>{
  let mut n=Self{epoch:p.epoch,balances:BTreeMap::new(),identified:0,unattributed:p.unattributed};
  for l in &p.lots{if l.amount==0||l.origin>p.epoch||!p.known.contains(&l.id){return Err("invalid lot")}n.credit(&l.id,l.amount)?;}
  n.total()?;Ok(n)
 }
 fn credit(&mut self,id:&str,amount:u64)->Result<(),&'static str>{if amount==0{return Ok(())}let v=self.balance(id).checked_add(amount).ok_or("beneficiary overflow")?;self.identified=self.identified.checked_add(amount).ok_or("aggregate overflow")?;self.balances.insert(id.into(),v);Ok(())}
 fn debit(&mut self,id:&str,amount:u64)->Result<(),&'static str>{let v=self.balance(id).checked_sub(amount).ok_or("beneficiary underflow")?;self.identified=self.identified.checked_sub(amount).ok_or("aggregate underflow")?;if v==0{self.balances.remove(id);}else{self.balances.insert(id.into(),v);}Ok(())}
 pub fn balance(&self,id:&str)->u64{self.balances.get(id).copied().unwrap_or(0)}
 pub fn beneficiaries(&self)->usize{self.balances.len()}
 pub fn total(&self)->Result<u64,&'static str>{self.identified.checked_add(self.unattributed).ok_or("total overflow")}
 pub fn verify(&self,p:&Population)->Result<(),&'static str>{if *self!=Self::build(p)?{return Err("index mismatch")}Ok(())}
 /// Qualification path: validate opening, derive incremental deltas only from canonical settlement,
 /// then compare against a full closing scan. No untrusted receipts or mutable index authority.
 pub fn advance(&self,p:&Population,r:&Period)->Result<(Self,Audit),&'static str>{
  self.verify(p)?;
  let audit=arrears::advance(p,r)?;
  let mut n=self.clone();
  for (id,v) in &audit.settlement.historical_reserved{n.debit(id,*v)?;}
  for a in &audit.settlement.awards{n.credit(&a.id,a.due.checked_sub(a.funded).ok_or("award")?)?;}
  n.epoch=audit.settlement.closing.epoch;
  n.verify(&audit.settlement.closing)?;
  if audit.settlement.current_funded!=audit.settlement.current_due.min(r.funding){return Err("current priority")}
  if u128::from(self.total()?)+u128::from(audit.settlement.current_due)!=u128::from(n.total()?)+u128::from(audit.settlement.current_funded)+u128::from(audit.total_reserved){return Err("conservation")}
  Ok((n,audit))
 }
}
#[cfg(test)]mod tests{
 use super::*;
 fn req(f:u64)->Period{Period{enter:vec![],depart:vec![],award:100,funding:f}}
 #[test]fn scarcity360(){let mut p=Population::phase_ix();let mut i=Index::build(&p).unwrap();for _ in 0..360{let(n,a)=i.advance(&p,&req(500)).unwrap();p=a.settlement.closing;i=n;}assert_eq!(p.lots.len(),2160);assert_eq!(i.beneficiaries(),6);assert_eq!(i.total().unwrap(),36400);}
 #[test]fn departed_partial(){let p=Population::phase_ix();let(i,a)=Index::build(&p).unwrap().advance(&p,&req(0)).unwrap();let p=a.settlement.closing;let mut r=req(650);r.enter=vec!["G_1".into()];r.depart=vec!["A_1".into()];let(n,a)=i.advance(&p,&r).unwrap();assert_eq!(n.balance("A_1"),50);assert_eq!(n.balance("G_1"),0);assert_eq!(a.receipts[0].beneficiary,"A_1");assert!(a.receipts[0].departed);}
 #[test]fn stale_and_attribution(){let p=Population::phase_ix();let i=Index::build(&p).unwrap();let(n,a)=i.advance(&p,&req(0)).unwrap();let q=a.settlement.closing;assert!(i.advance(&q,&req(600)).is_err());let mut bad=n.clone();bad.balances.insert("A_1".into(),99);bad.balances.insert("B_0".into(),101);assert!(bad.verify(&q).is_err());}
 #[test]fn retirement_once(){let p=Population::phase_ix();let(i,a)=Index::build(&p).unwrap().advance(&p,&req(0)).unwrap();let(n,b)=i.advance(&a.settlement.closing,&req(1200)).unwrap();assert_eq!(n.total().unwrap(),400);assert_eq!(n.beneficiaries(),0);assert!(i.advance(&b.settlement.closing,&req(1200)).is_err());let(_,c)=n.advance(&b.settlement.closing,&req(1200)).unwrap();assert_eq!(c.total_reserved,0);}
 #[test]fn mixed_parity(){let mut p=Population::phase_ix();let mut i=Index::build(&p).unwrap();let mut current="A_1".to_string();for t in 0..360{let mut r=req([0,500,600,750,1200][t%5]);if t%30==0{let next=format!("G_{t}");r.depart=vec![std::mem::replace(&mut current,next.clone())];r.enter=vec![next];}let(n,a)=i.advance(&p,&r).unwrap();assert_eq!(a.settlement,crate::population::settle(&p,&r).unwrap());p=a.settlement.closing;i=n;}i.verify(&p).unwrap();}
}

// UEP-266R: canonical component encoding, sorted by beneficiary.
impl Index{pub(crate) fn commitment_bytes(&self)->Vec<u8>{let mut b=b"UEP266B\0".to_vec();for v in [self.epoch,self.identified,self.unattributed,self.balances.len() as u64]{b.extend_from_slice(&v.to_be_bytes())}for(id,v)in &self.balances{b.extend_from_slice(&(id.len() as u64).to_be_bytes());b.extend_from_slice(id.as_bytes());b.extend_from_slice(&v.to_be_bytes())}b}}
