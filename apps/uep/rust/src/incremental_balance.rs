//! UEP-285R: incremental balance validation against internally generated canonical audit. .dlw
use crate::{balance_tree::{Tree,Proof},population::{Population,Period},arrears::{self,Audit}};
use std::collections::BTreeMap;
type Hash=[u8;32];
#[derive(Clone,Debug,PartialEq,Eq)]
pub struct Balances{tree:Tree,epoch:u64,unattributed:u64}
#[derive(Clone,Debug,PartialEq,Eq)]
pub struct Work{pub changed_paths:usize,pub debits:usize,pub credits:usize}
impl Balances{
 pub fn build(p:&Population,expected:Hash)->Result<Self,&'static str>{let tree=Tree::build(p)?;if tree.commitment()!=expected{return Err("opening anchor")}Ok(Self{tree,epoch:p.epoch,unattributed:p.unattributed})}
 pub fn commitment(&self)->Hash{self.tree.commitment()}
 pub fn root(&self)->Hash{self.tree.root()}
 pub fn total(&self)->Result<u64,&'static str>{self.tree.total()}
 pub fn balance(&self,id:&str)->Result<u64,&'static str>{self.tree.balance(id)}
 pub fn proof(&self,id:&str)->Result<Proof,&'static str>{self.tree.proof(id)}
 pub fn verify_full(&self,p:&Population)->Result<(),&'static str>{self.tree.verify(p)}
 /// Caller must pair the qualified opening balance commitment with the authoritative population.
 /// No externally supplied audit is accepted by the public advancement method.
 pub fn advance(&self,p:&Population,r:&Period,expected:Hash)->Result<(Self,Audit,Work),&'static str>{
  let a=arrears::advance(p,r)?;let(n,w)=self.apply_audit(p,r,&a,expected)?;Ok((n,a,w))
 }
 pub(crate) fn apply_audit(&self,p:&Population,r:&Period,a:&Audit,expected:Hash)->Result<(Self,Work),&'static str>{
  if self.commitment()!=expected||self.epoch!=p.epoch||self.unattributed!=p.unattributed||self.total()?!=p.outstanding()?{return Err("opening metadata")}
  let q=&a.settlement.closing;
  if q.unattributed!=p.unattributed||p.epoch.checked_add(1)!=Some(q.epoch)||a.settlement.current_funded!=a.settlement.current_due.min(r.funding){return Err("settlement metadata")}
  let mut delta=BTreeMap::<String,i128>::new();let mut unpaid=0u128;let mut reserved=0u128;
  for(id,v)in &a.settlement.historical_reserved{reserved+=u128::from(*v);*delta.entry(id.clone()).or_default()-=i128::from(*v);}
  for x in &a.settlement.awards{let v=x.due.checked_sub(x.funded).ok_or("award")?;unpaid+=u128::from(v);*delta.entry(x.id.clone()).or_default()+=i128::from(v);}
  if reserved!=u128::from(a.total_reserved)||u128::from(self.total()?) + unpaid != u128::from(q.outstanding()?) + reserved{return Err("conservation")}
  let mut n=self.clone();let mut w=Work{changed_paths:0,debits:0,credits:0};
  // Apply net debits first to avoid transient aggregate overflow.
  for debit in [true,false]{for(id,d)in &delta{if *d==0||(*d<0)!=debit{continue}let old=n.tree.balance(id)?;let new=u64::try_from(i128::from(old)+*d).map_err(|_|"delta range")?;n.tree=n.tree.replace_qualified(id,old,new)?;w.changed_paths+=1;if debit{w.debits+=1}else{w.credits+=1}}}
  n.tree=n.tree.finish_qualified(q.epoch,q.unattributed,q.outstanding()?)?;n.epoch=q.epoch;Ok((n,w))
 }
}
#[cfg(test)]mod tests{
 use super::*;use crate::verification_profile;
 fn fixture()->(Population,Balances){let p=Population::phase_ix();let n=Balances::build(&p,Tree::build(&p).unwrap().commitment()).unwrap();(p,n)}
 fn req(f:u64)->Period{Period{enter:vec![],depart:vec![],award:100,funding:f}}
 #[test]fn mixed(){let(mut p,mut n)=fixture();for i in 0..120{let r=req([0,500,600,750,1200][i%5]);let(a,c)=verification_profile::measure(||n.advance(&p,&r,n.commitment())).unwrap();let(z,a,w)=a.unwrap();assert_eq!(c.calls[10],0);assert_eq!(w.changed_paths,w.debits+w.credits);let q=a.settlement.closing;z.verify_full(&q).unwrap();assert_eq!(z.total().unwrap(),q.outstanding().unwrap());p=q;n=z;}}
 #[test]fn unchanged(){let(p,n)=fixture();let(z,a,w)=n.advance(&p,&req(600),n.commitment()).unwrap();assert_eq!(w.changed_paths,0);assert_eq!(z.root(),n.root());assert_ne!(z.commitment(),n.commitment());z.verify_full(&a.settlement.closing).unwrap();}
 #[test]fn departed(){let(p,n)=fixture();let(z,a,_)=n.advance(&p,&req(0),n.commitment()).unwrap();let mut r=req(650);r.enter=vec!["G".into()];r.depart=vec!["A_1".into()];let(v,a,w)=z.advance(&a.settlement.closing,&r,z.commitment()).unwrap();assert_eq!(w.changed_paths,1);assert_eq!(v.balance("A_1").unwrap(),50);assert_eq!(v.balance("G").unwrap(),0);assert_eq!(z.balance("A_1").unwrap(),100);v.verify_full(&a.settlement.closing).unwrap();}
 #[test]fn stale_and_tamper(){let(p,n)=fixture();assert!(Balances::build(&p,[0;32]).is_err());assert!(n.advance(&p,&req(600),[0;32]).is_err());let mut a=arrears::advance(&p,&req(0)).unwrap();a.total_reserved=1;assert!(n.apply_audit(&p,&req(0),&a,n.commitment()).is_err());let(z,a,_)=n.advance(&p,&req(0),n.commitment()).unwrap();assert!(n.advance(&a.settlement.closing,&req(600),n.commitment()).is_err());let mut proof=z.proof("A_1").unwrap();proof.siblings[0][0]^=1;assert!(!proof.verify("A_1",z.root()).unwrap());}
 #[test]fn recovery(){let(mut p,mut n)=fixture();for _ in 0..30{let(z,a,_)=n.advance(&p,&req(500),n.commitment()).unwrap();p=a.settlement.closing;n=z;}assert_eq!(n.total().unwrap(),3400);let(z,a,w)=n.advance(&p,&req(3600),n.commitment()).unwrap();assert_eq!(z.total().unwrap(),400);assert_eq!(w.debits,6);assert_eq!(w.credits,0);assert!(a.settlement.closing.lots.is_empty());z.verify_full(&a.settlement.closing).unwrap();}
}
