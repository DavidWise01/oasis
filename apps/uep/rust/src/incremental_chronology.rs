//! UEP-286R: qualified chronological obligation advancement; full oracle retained. .dlw
use crate::{chronology_tree::{Queue,LotProof},population::{Population,Period},arrears::{self,Audit}};
type Hash=[u8;32];
#[derive(Clone,Debug,PartialEq,Eq)]
pub struct Chronology{queue:Queue}
impl Chronology{
 pub fn build(p:&Population,expected:Hash)->Result<Self,&'static str>{let queue=Queue::build(p)?;if queue.commitment()!=expected{return Err("opening anchor")}Ok(Self{queue})}
 pub fn from_qualified(queue:&Queue,p:&Population,expected:Hash)->Result<Self,&'static str>{queue.verify(p)?;if queue.commitment()!=expected{return Err("opening anchor")}Ok(Self{queue:queue.clone()})}
 pub fn commitment(&self)->Hash{self.queue.commitment()}
 pub fn root(&self)->Hash{self.queue.root()}
 pub fn head(&self)->u64{self.queue.head()}
 pub fn tail(&self)->u64{self.queue.tail()}
 pub fn retirement(&self)->Hash{self.queue.retirement()}
 pub fn proof(&self,i:u64)->LotProof{self.queue.proof(i)}
 pub fn verify_full(&self,p:&Population)->Result<(),&'static str>{self.queue.verify(p)}
 /// The opening population must be the authoritative population paired with this queue.
 pub fn advance(&self,p:&Population,r:&Period,expected:Hash)->Result<(Self,Audit,usize),&'static str>{let a=arrears::advance(p,r)?;let(n,w)=self.apply_audit(p,r,&a,expected)?;Ok((n,a,w))}
 pub(crate) fn apply_audit(&self,p:&Population,r:&Period,a:&Audit,expected:Hash)->Result<(Self,usize),&'static str>{let(queue,w)=self.queue.apply_qualified(p,r,a,expected)?;Ok((Self{queue},w))}
}
#[cfg(test)]mod tests{
 use super::*;use crate::verification_profile;
 fn req(f:u64)->Period{Period{enter:vec![],depart:vec![],award:100,funding:f}}
 fn fixture()->(Population,Chronology,Queue){let p=Population::phase_ix();let q=Queue::build(&p).unwrap();let n=Chronology::build(&p,q.commitment()).unwrap();(p,n,q)}
 #[test]fn mixed(){let(mut p,mut n,mut o)=fixture();for t in 0..120{let r=req([0,500,600,750,1200][t%5]);let(a,c)=verification_profile::measure(||n.advance(&p,&r,n.commitment())).unwrap();let(z,a,w)=a.unwrap();assert_eq!(c.calls[12],0);let(v,b,k)=o.advance(&p,&r).unwrap();assert_eq!((a,w),(b,k));assert_eq!(z.queue,v);p=a.settlement.closing;n=z;o=v;}n.verify_full(&p).unwrap();}
 #[test]fn partial(){let(p,n,_)=fixture();let(z,a,_)=n.advance(&p,&req(0),n.commitment()).unwrap();let(v,b,w)=z.advance(&a.settlement.closing,&req(750),z.commitment()).unwrap();assert_eq!((v.head(),v.tail(),w),(1,6,2));assert_eq!(v.proof(1).lot.unwrap().amount,50);assert_eq!(z.proof(0).lot.unwrap().amount,100);assert!(v.proof(0).lot.is_none());v.verify_full(&b.settlement.closing).unwrap();}
 #[test]fn retirement(){let(p,n,_)=fixture();let(z,a,_)=n.advance(&p,&req(0),n.commitment()).unwrap();let(v,b,w)=z.advance(&a.settlement.closing,&req(1200),z.commitment()).unwrap();assert_eq!((v.head(),v.tail(),w),(6,6,6));let fresh=Queue::build(&b.settlement.closing).unwrap();assert_eq!(v.root(),fresh.root());assert_ne!(v.commitment(),fresh.commitment());let restored=Chronology::from_qualified(&v.queue,&b.settlement.closing,v.commitment()).unwrap();assert_eq!(restored,v);let(next,_,_)=v.advance(&b.settlement.closing,&req(500),v.commitment()).unwrap();assert_eq!((next.head(),next.tail()),(6,12));}
 #[test]fn scarcity_no_changes(){let(mut p,mut n,_)=fixture();for _ in 0..120{let(z,a,w)=n.advance(&p,&req(500),n.commitment()).unwrap();assert_eq!(w,6);p=a.settlement.closing;n=z;}assert_eq!(n.tail(),720);let(a,c)=verification_profile::measure(||n.advance(&p,&req(600),n.commitment())).unwrap();let(z,a,w)=a.unwrap();assert_eq!((w,c.calls[12],c.calls[15]),(0,0,0));assert_eq!(z.root(),n.root());z.verify_full(&a.settlement.closing).unwrap();}
 #[test]fn tamper_and_departure(){let(p,n,_)=fixture();assert!(n.advance(&p,&req(600),[0;32]).is_err());let(z,a,_)=n.advance(&p,&req(0),n.commitment()).unwrap();let q=a.settlement.closing;let mut r=req(650);r.enter=vec!["G".into()];r.depart=vec!["A_1".into()];let(v,a,_)=z.advance(&q,&r,z.commitment()).unwrap();assert!(a.receipts[0].departed);assert_eq!(v.proof(0).lot.as_ref().unwrap().id,"A_1");let mut proof=v.proof(0);assert!(proof.verify(0,v.root()).unwrap());proof.siblings[0][0]^=1;assert!(!proof.verify(0,v.root()).unwrap());assert!(z.advance(&a.settlement.closing,&req(600),z.commitment()).is_err());let mut bad=arrears::advance(&q,&r).unwrap();bad.receipts[0].reserved+=1;assert!(z.apply_audit(&q,&r,&bad,z.commitment()).is_err());}
}
