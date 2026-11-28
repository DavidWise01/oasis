//! UEP-284R: qualified compact historical and active registries; full oracle retained. .dlw
use crate::{compact_membership::Compact,changed_path,membership_tree::Membership,population::{Population,Period},identity_continuity};
use sha2::{Digest,Sha256};
type Hash=[u8;32];
#[derive(Clone,Debug,PartialEq,Eq)]
pub struct Registry{known:Compact,active:Compact,epoch:u64,count:u64,active_count:u64}
#[derive(Clone,Debug,PartialEq,Eq)]
pub struct Work{pub historical_paths:usize,pub active_paths:usize}
impl Registry{
 pub fn build(p:&Population,expected:Hash)->Result<Self,&'static str>{
 let oracle=Membership::build(p)?;if oracle.commitment()!=expected{return Err("opening anchor")}
 let mut known=Compact::new();let mut active=Compact::new();for id in &p.known{known=known.insert(id)?;}for id in &p.active{active=active.insert(id)?;}
 let n=Self{known,active,epoch:p.epoch,count:p.known.len() as u64,active_count:p.active.len() as u64};if n.commitment()!=expected{return Err("compact parity")}Ok(n)
 }
 pub fn known_root(&self)->Hash{self.known.root()}
 pub fn active_root(&self)->Hash{self.active.root()}
 pub fn commitment(&self)->Hash{let mut h=Sha256::new();h.update(b"OASIS-UEP-273R-membership-v1");for v in [self.epoch,self.count,self.active_count]{h.update(v.to_be_bytes())}h.update(self.known_root());h.update(self.active_root());h.finalize().into()}
 pub fn known_proof(&self,id:&str)->Result<crate::membership_tree::Proof,&'static str>{self.known.proof(id)}
 pub fn active_proof(&self,id:&str)->Result<crate::membership_tree::Proof,&'static str>{self.active.proof(id)}
 pub fn nodes(&self)->(usize,usize){(self.known.nodes(),self.active.nodes())}
 pub fn verify_full(&self,p:&Population)->Result<(),&'static str>{if Membership::build(p)?.commitment()!=self.commitment(){return Err("full parity")}Ok(())}
 /// Opening population must be the authoritative state paired with this qualified registry.
 /// Public callers cannot inject proof deltas or construct unchecked registry fields.
 pub fn advance(&self,p:&Population,q:&Population,r:&Period,expected:Hash)->Result<(Self,Work),&'static str>{
 if self.commitment()!=expected||self.epoch!=p.epoch||self.count!=p.known.len() as u64||self.active_count!=p.active.len() as u64{return Err("opening metadata")}
 let d=identity_continuity::verify(p,q,r)?;if q.known.len()>10000{return Err("identity limit")}
 let mut n=self.clone();let mut w=Work{historical_paths:0,active_paths:0};
 for id in d.departed{if n.known.proof(&id)?.value!=1{return Err("unknown departure")}let(t,_)=changed_path::apply(&n.active,&id,1,0)?;n.active=t;n.active_count=n.active_count.checked_sub(1).ok_or("active count")?;w.active_paths+=1;}
 for id in d.entered{let(t,_)=changed_path::apply(&n.known,&id,0,1)?;n.known=t;let(t,_)=changed_path::apply(&n.active,&id,0,1)?;n.active=t;n.count=n.count.checked_add(1).ok_or("known count")?;n.active_count=n.active_count.checked_add(1).ok_or("active count")?;w.historical_paths+=1;w.active_paths+=1;}
 n.epoch=q.epoch;if n.count!=q.known.len() as u64||n.active_count!=q.active.len() as u64{return Err("closing metadata")}Ok((n,w))
 }
}
#[cfg(test)]mod tests{
 use super::*;use crate::{population::settle,verification_profile};
 fn fixture()->(Population,Registry){let p=Population::phase_ix();let n=Registry::build(&p,Membership::build(&p).unwrap().commitment()).unwrap();(p,n)}
 fn req()->Period{Period{enter:vec![],depart:vec![],award:100,funding:600}}
 #[test]fn unchanged(){let(p,n)=fixture();let q=settle(&p,&req()).unwrap().closing;let((z,w),c)= {let(a,c)=verification_profile::measure(||n.advance(&p,&q,&req(),n.commitment())).unwrap();(a.unwrap(),c)};assert_eq!((w.historical_paths,w.active_paths,c.calls[11]),(0,0,0));assert_eq!(n.known_root(),z.known_root());assert_eq!(n.active_root(),z.active_root());z.verify_full(&q).unwrap();}
 #[test]fn churn(){let(mut p,mut n)=fixture();let mut current="A_1".to_string();for i in 0..120{let mut r=req();let id=format!("G_{i}");r.depart=vec![std::mem::replace(&mut current,id.clone())];r.enter=vec![id];let q=settle(&p,&r).unwrap().closing;let(a,c)=verification_profile::measure(||n.advance(&p,&q,&r,n.commitment())).unwrap();let(z,w)=a.unwrap();assert_eq!((w.historical_paths,w.active_paths,c.calls[11]),(1,2,0));z.verify_full(&q).unwrap();p=q;n=z;}assert_eq!(n.nodes(),(253,11));assert_eq!(n.known_proof("A_1").unwrap().value,1);assert_eq!(n.active_proof("A_1").unwrap().value,0);}
 #[test]fn invalid(){let(p,n)=fixture();let mut r=req();r.enter=vec!["A_0".into()];assert!(n.advance(&p,&p,&r,n.commitment()).is_err());let mut q=settle(&p,&req()).unwrap().closing;q.known.remove("A_0");assert!(n.advance(&p,&q,&req(),n.commitment()).is_err());assert!(Registry::build(&p,[0;32]).is_err());assert!(n.advance(&p,&p,&req(),[0;32]).is_err());}
 #[test]fn batch(){let(p,n)=fixture();let mut r=req();r.enter=vec!["Z".into(),"G".into()];r.depart=vec!["A_1".into(),"B_0".into()];let q=settle(&p,&r).unwrap().closing;let(z,w)=n.advance(&p,&q,&r,n.commitment()).unwrap();assert_eq!((w.historical_paths,w.active_paths),(2,4));z.verify_full(&q).unwrap();r.enter.reverse();r.depart.reverse();assert_eq!(z,n.advance(&p,&q,&r,n.commitment()).unwrap().0);}
 #[test]fn departed_debt(){let(p,n)=fixture();let mut r=req();r.funding=0;let q=settle(&p,&r).unwrap().closing;let(z,_)=n.advance(&p,&q,&r,n.commitment()).unwrap();let mut r=req();r.enter=vec!["G".into()];r.depart=vec!["A_1".into()];let v=settle(&q,&r).unwrap().closing;let(w,_)=z.advance(&q,&v,&r,z.commitment()).unwrap();assert!(v.lots.iter().any(|l|l.id=="A_1"));assert_eq!(w.known_proof("A_1").unwrap().value,1);assert_eq!(w.active_proof("A_1").unwrap().value,0);w.verify_full(&v).unwrap();}
}
