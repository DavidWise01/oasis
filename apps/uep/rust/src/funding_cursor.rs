//! UEP-264R: incremental chronological queue, qualified against authoritative settlement. .dlw
use crate::{population::{Population,Period,Lot},arrears::{self,Audit,Receipt}};
use std::collections::VecDeque;
#[derive(Clone,Debug,PartialEq,Eq)]
pub struct Cursor{epoch:u64,queue:VecDeque<Lot>,retired:u64,identified:u64,unattributed:u64}
#[derive(Clone,Debug,PartialEq,Eq)]
pub struct Work{pub opening_lots:usize,pub visited:usize,pub retired:usize,pub appended:usize}
impl Cursor{
 pub fn build(p:&Population)->Result<Self,&'static str>{
  if p.lots.windows(2).any(|w|w[0].origin>w[1].origin)||p.lots.iter().any(|l|l.amount==0||l.origin>p.epoch||!p.known.contains(&l.id)){return Err("invalid chronology")}
  Ok(Self{epoch:p.epoch,queue:p.lots.iter().cloned().collect(),retired:0,identified:p.outstanding()?.checked_sub(p.unattributed).ok_or("balance")?,unattributed:p.unattributed})
 }
 pub fn total(&self)->Result<u64,&'static str>{self.identified.checked_add(self.unattributed).ok_or("total")}
 pub fn len(&self)->usize{self.queue.len()}
 pub fn retired(&self)->u64{self.retired}
 pub fn verify(&self,p:&Population)->Result<(),&'static str>{
  if self.epoch!=p.epoch||self.unattributed!=p.unattributed||self.total()?!=p.outstanding()?||!self.queue.iter().eq(p.lots.iter()){return Err("cursor mismatch")}Ok(())
 }
 /// Qualification mode: original settlement remains authoritative.
 /// Only the incremental queue loop is counted as visited work; clones and scans are excluded.
 pub fn advance(&self,p:&Population,r:&Period)->Result<(Self,Audit,Work),&'static str>{
  self.verify(p)?;let audit=arrears::advance(p,r)?;let mut n={let _profile=crate::verification_profile::span(8);self.clone()};
  let mut left=r.funding.checked_sub(audit.settlement.current_funded).ok_or("funding")?;
  let mut receipts=Vec::new();let mut work=Work{opening_lots:n.len(),visited:0,retired:0,appended:0};
  while left>0{
   let Some(l)=n.queue.front_mut() else{break};
   work.visited+=1;let paid=left.min(l.amount);left-=paid;l.amount-=paid;n.identified=n.identified.checked_sub(paid).ok_or("debit")?;
   receipts.push(Receipt{origin:l.origin,beneficiary:l.id.clone(),opening_index:work.retired,reserved:paid,remainder:l.amount,departed:!audit.settlement.closing.active.contains(&l.id)});
   if l.amount==0{n.queue.pop_front();work.retired+=1;n.retired=n.retired.checked_add(1).ok_or("retired overflow")?;}
  }
  n.epoch=audit.settlement.closing.epoch;
  for a in &audit.settlement.awards{let amount=a.due.checked_sub(a.funded).ok_or("award")?;if amount>0{n.queue.push_back(Lot{origin:n.epoch,id:a.id.clone(),amount});n.identified=n.identified.checked_add(amount).ok_or("credit")?;work.appended+=1;}}
  n.verify(&audit.settlement.closing)?;
  if receipts!=audit.receipts||left!=audit.settlement.unallocated||audit.settlement.current_funded!=audit.settlement.current_due.min(r.funding){return Err("receipt parity")}
  if u128::from(self.total()?)+u128::from(audit.settlement.current_due)!=u128::from(n.total()?)+u128::from(audit.settlement.current_funded)+u128::from(audit.total_reserved){return Err("conservation")}
  Ok((n,audit,work))
 }
}
#[cfg(test)]mod tests{
 use super::*;
 fn req(f:u64)->Period{Period{enter:vec![],depart:vec![],award:100,funding:f}}
 #[test]fn zero_surplus(){let mut p=Population::phase_ix();let mut c=Cursor::build(&p).unwrap();for _ in 0..360{let(n,a,w)=c.advance(&p,&req(500)).unwrap();assert_eq!(w.visited,0);assert_eq!(w.appended,6);p=a.settlement.closing;c=n;}assert_eq!(c.len(),2160);assert_eq!(c.total().unwrap(),36400);let(_,_,w)=c.advance(&p,&req(600)).unwrap();assert_eq!(w.visited,0);}
 #[test]fn partial_front(){let p=Population::phase_ix();let(c,a,_)=Cursor::build(&p).unwrap().advance(&p,&req(0)).unwrap();let(n,b,w)=c.advance(&a.settlement.closing,&req(750)).unwrap();assert_eq!((w.visited,w.retired,w.appended),(2,1,0));assert_eq!(n.len(),5);assert_eq!(b.receipts[1].remainder,50);assert_eq!(n.retired(),1);}
 #[test]fn departed_and_tie_order(){let p=Population::phase_ix();let(c,a,_)=Cursor::build(&p).unwrap().advance(&p,&req(0)).unwrap();let mut r=req(650);r.enter=vec!["G".into()];r.depart=vec!["A_1".into()];let(n,b,w)=c.advance(&a.settlement.closing,&r).unwrap();assert_eq!(w.visited,1);assert_eq!(b.receipts[0].beneficiary,"A_1");assert!(b.receipts[0].departed);assert_eq!(n.queue.front().unwrap().amount,50);}
 #[test]fn stale_and_empty(){let p=Population::phase_ix();let c=Cursor::build(&p).unwrap();let(n,a,_)=c.advance(&p,&req(0)).unwrap();assert!(c.advance(&a.settlement.closing,&req(1200)).is_err());let(z,b,w)=n.advance(&a.settlement.closing,&req(2000)).unwrap();assert_eq!((w.visited,w.retired,z.len()),(6,6,0));assert_eq!(z.total().unwrap(),400);let(_,_,w)=z.advance(&b.settlement.closing,&req(2000)).unwrap();assert_eq!(w.visited,0);}
 #[test]fn mixed_parity(){let mut p=Population::phase_ix();let mut c=Cursor::build(&p).unwrap();for t in 0..360{let r=req([0,500,600,750,1200][t%5]);let(n,a,w)=c.advance(&p,&r).unwrap();assert_eq!(a,arrears::advance(&p,&r).unwrap());assert!(w.visited<=w.opening_lots);assert_eq!(w.visited,a.receipts.len());p=a.settlement.closing;c=n;}c.verify(&p).unwrap();}
}

// UEP-266R: commit exact queue order, partial remainders and retired counter.
impl Cursor{pub(crate) fn commitment_bytes(&self)->Vec<u8>{let _profile=crate::verification_profile::span(5);let mut b=b"UEP266Q\0".to_vec();for v in [self.epoch,self.retired,self.identified,self.unattributed,self.queue.len() as u64]{b.extend_from_slice(&v.to_be_bytes())}for l in &self.queue{b.extend_from_slice(&l.origin.to_be_bytes());b.extend_from_slice(&(l.id.len() as u64).to_be_bytes());b.extend_from_slice(l.id.as_bytes());b.extend_from_slice(&l.amount.to_be_bytes())}b}}
