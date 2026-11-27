//! UEP-275R: unified authenticated economic state; authoritative settlement retained. .dlw
use crate::{balance_tree::Tree,membership_tree::Membership,chronology_tree::Queue,executable::{Universe,Request},state_hash,arrears::Audit};
use sha2::{Digest,Sha256};
type Hash=[u8;32];
#[derive(Clone,Debug,PartialEq,Eq)]
pub struct Root{pub authority:Hash,pub balances:Hash,pub membership:Hash,pub chronology:Hash,pub digest:Hash}
impl Root{
 fn calculate(&self)->Hash{let mut h=Sha256::new();h.update(b"OASIS-UEP-275R-unified-v1");for v in [&self.authority,&self.balances,&self.membership,&self.chronology]{h.update(v)}h.finalize().into()}
 pub fn verify(&self)->bool{self.digest==self.calculate()}
 pub fn encode(&self)->Vec<u8>{let mut b=b"UEP275R\0".to_vec();for v in [&self.authority,&self.balances,&self.membership,&self.chronology,&self.digest]{b.extend_from_slice(v)}b}
}
#[derive(Clone,Debug,PartialEq,Eq)]
pub struct State{authority:Hash,balances:Tree,membership:Membership,chronology:Queue}
#[derive(Clone,Debug,PartialEq,Eq)]
pub struct Work{pub balance_paths:usize,pub chronology_paths:usize}
impl State{
 pub fn build(u:&Universe,expected:Hash)->Result<Self,&'static str>{if state_hash::fingerprint(u)?!=expected{return Err("opening authority")}let p=u.population_ledger();let n=Self{authority:expected,balances:Tree::build(p)?,membership:Membership::build(p)?,chronology:Queue::build(p)?};n.verify(u)?;Ok(n)}
 pub fn root(&self)->Root{let mut r=Root{authority:self.authority,balances:self.balances.commitment(),membership:self.membership.commitment(),chronology:self.chronology.commitment(),digest:[0;32]};r.digest=r.calculate();r}
 pub fn verify(&self,u:&Universe)->Result<(),&'static str>{if self.authority!=state_hash::fingerprint(u)?{return Err("authority mismatch")}let p=u.population_ledger();self.balances.verify(p)?;self.membership.verify(p)?;self.chronology.verify(p)?;if self.balances.total()?!=p.outstanding()?{return Err("total mismatch")}Ok(())}
 pub fn verify_root(&self,u:&Universe,expected:&Root)->Result<(),&'static str>{self.verify(u)?;if !expected.verify()||self.root()!=*expected{return Err("root mismatch")}Ok(())}
 pub fn balance_tree(&self)->&Tree{&self.balances}
 pub fn membership(&self)->&Membership{&self.membership}
 pub fn chronology(&self)->&Queue{&self.chronology}
 pub fn advance(&self,u:&Universe,r:&Request,expected:&Root)->Result<(Self,Universe,Audit,Work),&'static str>{
  self.verify_root(u,expected)?;let p=u.population_ledger();
  let(balances,a,bc)=self.balances.advance(p,&r.present.period)?;
  let(chronology,b,qc)=self.chronology.advance(p,&r.present.period)?;
  if a!=b{return Err("audit parity")}
  let v=u.advance(r)?;let q=v.population_ledger();if q!=&a.settlement.closing{return Err("settlement parity")}
  let o=v.observations().last().ok_or("observation")?;
  if(o.due,o.funded,o.arrears,o.historical_reserved)!=(a.settlement.current_due,a.settlement.current_funded,q.outstanding()?,a.total_reserved){return Err("observation parity")}
  let membership=self.membership.advance(p,q,&r.present.period)?;
  let n=Self{authority:state_hash::fingerprint(&v)?,balances,membership,chronology};n.verify(&v)?;
  Ok((n,v,a,Work{balance_paths:bc,chronology_paths:qc}))
 }
 pub fn compact(&self,u:&Universe,expected:&Root)->Result<Universe,&'static str>{self.verify_root(u,expected)?;let v=u.compact(self.authority)?;self.verify_root(&v,expected)?;Ok(v)}
}
#[cfg(test)]mod tests{
 use super::*;use crate::{evidence::Ledger,equilibrium::Step,population::Period,bridge::Shares,dividend::Revenue,capacity::Input};
 fn opening()->(State,Universe){let u=Universe::new(Ledger::default(),[0;32]).unwrap();let s=State::build(&u,state_hash::fingerprint(&u).unwrap()).unwrap();(s,u)}
 fn req(f:u64)->Request{let s=Step{period:Period{enter:vec![],depart:vec![],award:100,funding:f},restitution:Shares::default(),revenue:Revenue{public_equity:0,licensing:0,automation_royalties:0,infrastructure_return:0},dividend_cap:0,resources:Input{inflow:[100;4],essential:[20;4],decay_bps:0,work_ceiling:17}};Request{present:s.clone(),requested:0,complete:0,accept:0,future:vec![s]}}
 #[test]fn mixed_replay(){let(mut s,mut u)=opening();let mut current="A_1".to_string();for t in 0..30{let mut r=req([0,500,600,750,1200][t%5]);if t%10==0{let next=format!("G_{t}");r.present.period.depart=vec![std::mem::replace(&mut current,next.clone())];r.present.period.enter=vec![next];}let(n,v,_,_)=s.advance(&u,&r,&s.root()).unwrap();assert_eq!(state_hash::encode(&v).unwrap(),state_hash::encode(&u.advance(&r).unwrap()).unwrap());let(m,w,_,_)=s.advance(&u,&r,&s.root()).unwrap();assert_eq!(n.root(),m.root());assert_eq!(v,w);s=n;u=v;}s.verify(&u).unwrap();}
 #[test]fn substituted_root(){let(s,u)=opening();for i in 0..4{let mut r=s.root();match i{0=>r.authority[0]^=1,1=>r.balances[0]^=1,2=>r.membership[0]^=1,_=>r.chronology[0]^=1}r.digest=r.calculate();assert!(r.verify());assert!(s.advance(&u,&req(600),&r).is_err());}assert_eq!(s.root().encode().len(),168);}
 #[test]fn compaction(){let(s,u)=opening();let(n,v,_,_)=s.advance(&u,&req(500),&s.root()).unwrap();let c=n.root();let w=n.compact(&v,&c).unwrap();assert!(w.observations().is_empty());n.verify_root(&w,&c).unwrap();}
 #[test]fn history_and_stale(){let(s,u)=opening();let(n,v,_,_)=s.advance(&u,&req(0),&s.root()).unwrap();let(m,w,_,_)=n.advance(&v,&req(1200),&n.root()).unwrap();let reset=State::build(&w,state_hash::fingerprint(&w).unwrap()).unwrap();assert_ne!(reset.root(),m.root());assert!(m.advance(&w,&req(600),&n.root()).is_err());assert!(s.verify(&w).is_err());}
 #[test]fn departed_balance(){let(s,u)=opening();let(n,v,_,_)=s.advance(&u,&req(0),&s.root()).unwrap();let mut r=req(650);r.present.period.enter=vec!["G".into()];r.present.period.depart=vec!["A_1".into()];let(m,w,a,c)=n.advance(&v,&r,&n.root()).unwrap();assert_eq!(m.balance_tree().balance("A_1").unwrap(),50);assert_eq!(m.membership().known_proof("A_1").unwrap().value,1);assert_eq!(m.membership().active_proof("A_1").unwrap().value,0);assert_eq!(m.chronology().get(0).unwrap().amount,50);assert!(a.receipts[0].departed);assert_eq!((c.balance_paths,c.chronology_paths),(1,1));m.verify(&w).unwrap();}
}

// UEP-276R: reuse the audit generated inside authoritative execution.
// All opening and closing validation remains enabled. No public audit injection.
impl State{
 pub fn advance_delta(&self,u:&Universe,r:&Request,expected:&Root)->Result<(Self,Universe,Audit,Work),&'static str>{
  self.verify_root(u,expected)?;
  let (v,a)=u.advance_audited(r)?;
  let p=u.population_ledger();let q=v.population_ledger();
  if q!=&a.settlement.closing{return Err("settlement parity")}
  let o=v.observations().last().ok_or("observation")?;
  if(o.due,o.funded,o.arrears,o.historical_reserved)!=(a.settlement.current_due,a.settlement.current_funded,q.outstanding()?,a.total_reserved){return Err("observation parity")}
  let (balances,bc)=self.balances.apply_audit(&r.present.period,&a)?;
  let (chronology,qc)=self.chronology.apply_audit(&r.present.period,&a)?;
  let membership=self.membership.advance(p,q,&r.present.period)?;
  let n=Self{authority:state_hash::fingerprint(&v)?,balances,membership,chronology};n.verify(&v)?;
  Ok((n,v,a,Work{balance_paths:bc,chronology_paths:qc}))
 }
}
#[cfg(test)]mod delta_tests{
 use super::*;use crate::{evidence::Ledger,equilibrium::Step,population::Period,bridge::Shares,dividend::Revenue,capacity::Input,verification_profile};
 fn opening()->(State,Universe){let u=Universe::new(Ledger::default(),[0;32]).unwrap();let s=State::build(&u,state_hash::fingerprint(&u).unwrap()).unwrap();(s,u)}
 fn req(f:u64)->Request{let s=Step{period:Period{enter:vec![],depart:vec![],award:100,funding:f},restitution:Shares::default(),revenue:Revenue{public_equity:0,licensing:0,automation_royalties:0,infrastructure_return:0},dividend_cap:0,resources:Input{inflow:[100;4],essential:[20;4],decay_bps:0,work_ceiling:17}};Request{present:s.clone(),requested:0,complete:0,accept:0,future:vec![s]}}

 #[test]fn measured_calls(){let(s,u)=opening();let r=req(500);let(a,x)=verification_profile::measure(||s.advance(&u,&r,&s.root())).unwrap();let(b,y)=verification_profile::measure(||s.advance_delta(&u,&r,&s.root())).unwrap();assert_eq!(a.unwrap(),b.unwrap());assert_eq!((x.calls[1],y.calls[1]),(3,1));}
 #[test]fn mixed_parity(){let(mut s,mut u)=opening();let mut current="A_1".to_string();for t in 0..60{let mut r=req([0,500,600,750,1200][t%5]);if t%10==0{let next=format!("G_{t}");r.present.period.depart=vec![std::mem::replace(&mut current,next.clone())];r.present.period.enter=vec![next];}let a=s.advance(&u,&r,&s.root()).unwrap();let b=s.advance_delta(&u,&r,&s.root()).unwrap();assert_eq!(a,b);s=b.0;u=b.1;}s.verify(&u).unwrap();}
 #[test]fn rejected_unchanged(){let(s,u)=opening();let old=s.clone();let mut r=req(600);r.present.period.enter=vec!["A_0".into()];assert!(s.advance_delta(&u,&r,&s.root()).is_err());assert_eq!(s,old);assert!(u.observations().is_empty());let mut root=s.root();root.digest[0]^=1;assert!(s.advance_delta(&u,&req(600),&root).is_err());}
 #[test]fn scarcity_and_recovery(){let(mut s,mut u)=opening();for _ in 0..30{let a=s.advance(&u,&req(500),&s.root()).unwrap();let b=s.advance_delta(&u,&req(500),&s.root()).unwrap();assert_eq!(a,b);s=b.0;u=b.1;}assert_eq!(s.chronology().tail(),180);assert_eq!(s.balance_tree().total().unwrap(),3400);let a=s.advance(&u,&req(3600),&s.root()).unwrap();let b=s.advance_delta(&u,&req(3600),&s.root()).unwrap();assert_eq!(a,b);assert_eq!(b.0.balance_tree().total().unwrap(),400);assert_eq!(b.0.chronology().head(),180);}
 #[test]fn compacted_continuity(){let(s,u)=opening();let(n,v,_,_)=s.advance_delta(&u,&req(500),&s.root()).unwrap();let c=n.root();let w=n.compact(&v,&c).unwrap();let a=n.advance(&w,&req(750),&c).unwrap();let b=n.advance_delta(&w,&req(750),&c).unwrap();assert_eq!(a,b);}
}
