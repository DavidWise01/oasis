//! UEP-265R: integrated derived working-state projection; no authority transfer. .dlw
use crate::{population::Population,executable::{Universe,Request},state_hash,obligation_index::Index,identity_index::IdentityIndex,funding_cursor::{Cursor,Work},arrears::Audit};
#[derive(Clone,Debug,PartialEq,Eq)]
pub struct Projection{anchor:[u8;32],balances:Index,identities:IdentityIndex,chronology:Cursor}
#[derive(Clone,Debug,PartialEq,Eq)]
pub struct View{pub active:usize,pub known:u64,pub beneficiaries:usize,pub lots:usize,pub outstanding:u64,pub observations:usize,pub cumulative:u64,pub identity_head:[u8;32],pub anchor:[u8;32]}
impl Projection{
 pub fn build(u:&Universe,expected:[u8;32])->Result<Self,&'static str>{
  if state_hash::fingerprint(u)?!=expected{return Err("opening anchor")}
  let p=u.population_ledger();let n=Self{anchor:expected,balances:Index::build(p)?,identities:IdentityIndex::build(p)?,chronology:Cursor::build(p)?};n.verify(u)?;Ok(n)
 }
 fn verify_population(&self,p:&Population)->Result<(),&'static str>{
  self.balances.verify(p)?;self.identities.verify_membership(p)?;self.chronology.verify(p)?;
  if self.balances.total()?!=self.chronology.total()?{return Err("aggregate parity")}Ok(())
 }
 pub fn verify(&self,u:&Universe)->Result<(),&'static str>{if self.anchor!=state_hash::fingerprint(u)?{return Err("projection anchor")}self.verify_population(u.population_ledger())}
 pub fn view(&self,u:&Universe)->Result<View,&'static str>{self.verify(u)?;Ok(View{active:u.population_count(),known:self.identities.count(),beneficiaries:self.balances.beneficiaries(),lots:self.chronology.len(),outstanding:self.balances.total()?,observations:u.observations().len(),cumulative:u.total_observations(),identity_head:self.identities.head(),anchor:self.anchor})}
 pub fn balance(&self,id:&str)->u64{self.balances.balance(id)}
 pub fn known(&self,id:&str)->bool{self.identities.known(id)}
 pub fn advance(&self,u:&Universe,r:&Request)->Result<(Self,Universe,Audit,Work),&'static str>{
  self.verify(u)?;let p=u.population_ledger();
  let (balances,a)=self.balances.advance(p,&r.present.period)?;
  let (chronology,b,work)=self.chronology.advance(p,&r.present.period)?;
  if a!=b{return Err("derived audit parity")}
  let n=u.advance(r)?;let q=n.population_ledger();
  if q!=&a.settlement.closing{return Err("authoritative settlement parity")}
  let o=n.observations().last().ok_or("missing observation")?;
  if (o.due,o.funded,o.arrears,o.historical_reserved)!=(a.settlement.current_due,a.settlement.current_funded,q.outstanding()?,a.total_reserved){return Err("observation parity")}
  let identities=self.identities.advance(p,q,&r.present.period)?;
  let next=Self{anchor:state_hash::fingerprint(&n)?,balances,identities,chronology};next.verify(&n)?;Ok((next,n,a,work))
 }
 /// Compaction does not reset the derived identity chain or funding cursor.
 pub fn compact(&self,u:&Universe)->Result<Universe,&'static str>{self.verify(u)?;let n=u.compact(self.anchor)?;self.verify(&n)?;Ok(n)}
}
#[cfg(test)]mod tests{
 use super::*;use crate::{evidence::Ledger,equilibrium::Step,population::Period,bridge::Shares,dividend::Revenue,capacity::Input};
 fn root()->Universe{Universe::new(Ledger::default(),[0;32]).unwrap()}
 fn req(f:u64)->Request{let s=Step{period:Period{enter:vec![],depart:vec![],award:100,funding:f},restitution:Shares::default(),revenue:Revenue{public_equity:0,licensing:0,automation_royalties:0,infrastructure_return:0},dividend_cap:0,resources:Input{inflow:[100;4],essential:[20;4],decay_bps:0,work_ceiling:17}};Request{present:s.clone(),requested:0,complete:0,accept:0,future:vec![s]}}
 fn build(u:&Universe)->Projection{Projection::build(u,state_hash::fingerprint(u).unwrap()).unwrap()}
 #[test]fn scarcity_and_compaction(){let mut u=root();let mut p=build(&u);for _ in 0..360{let(n,v,_,w)=p.advance(&u,&req(500)).unwrap();assert_eq!(w.visited,0);p=n;u=v;}let before=p.view(&u).unwrap();assert_eq!((before.lots,before.beneficiaries,before.outstanding),(2160,6,36400));let c=p.compact(&u).unwrap();let after=p.view(&c).unwrap();assert_eq!(after.observations,0);assert_eq!(before.anchor,after.anchor);assert_eq!(before.identity_head,after.identity_head);assert_eq!(before.outstanding,after.outstanding);}
 #[test]fn exact_mixed(){let mut u=root();let mut p=build(&u);let mut current="A_1".to_string();for t in 0..72{let mut r=req([0,500,600,750,1200][t%5]);if t%9==0{let next=format!("G_{t}");r.present.period.depart=vec![std::mem::replace(&mut current,next.clone())];r.present.period.enter=vec![next];}let(n,v,_,_)=p.advance(&u,&r).unwrap();assert_eq!(v,u.advance(&r).unwrap());p=n;u=v;}assert!(p.known("A_1"));p.verify(&u).unwrap();}
 #[test]fn stale_and_wrong_anchor(){let u=root();assert!(Projection::build(&u,[1;32]).is_err());let p=build(&u);let(_,n,_,_)=p.advance(&u,&req(500)).unwrap();assert!(p.advance(&n,&req(600)).is_err());assert!(p.compact(&n).is_err());}
 #[test]fn departed_obligation(){let u=root();let(p,n,_,_)=build(&u).advance(&u,&req(0)).unwrap();let mut r=req(650);r.present.period.enter=vec!["G".into()];r.present.period.depart=vec!["A_1".into()];let(q,v,a,w)=p.advance(&n,&r).unwrap();assert_eq!(q.balance("A_1"),50);assert_eq!(q.balance("G"),0);assert!(q.known("A_1"));assert!(a.receipts[0].departed);assert_eq!(w.visited,1);assert_eq!(q.view(&v).unwrap().active,6);}
 #[test]fn rejected_transition_preserves_opening(){let u=root();let p=build(&u);let before=p.clone();let bytes=state_hash::encode(&u).unwrap();let mut r=req(600);r.present.period.enter=vec!["A_0".into()];assert!(p.advance(&u,&r).is_err());assert_eq!(p,before);assert_eq!(state_hash::encode(&u).unwrap(),bytes);}
}
