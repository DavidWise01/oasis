//! UEP-283R: authenticated single-path membership transitions; policy remains external. .dlw
use crate::{membership_tree::Proof,compact_membership::Compact};
type Hash=[u8;32];
#[derive(Clone,Debug,PartialEq,Eq)]
pub struct Change{pub id:String,pub opening:Proof,pub replacement:u64}
impl Change{
 /// Verify both endpoints using exactly the same sibling path.
 pub fn verify(&self,id:&str,before:u64,after:u64,opening:Hash,closing:Hash)->Result<(),&'static str>{
 if self.id!=id||self.opening.value!=before||self.replacement!=after||before>1||after>1{return Err("transition policy")}
 if !self.opening.verify(id,opening)?{return Err("opening proof")}
 let mut next=self.opening.clone();next.value=after;
 if !next.verify(id,closing)?{return Err("closing proof")}Ok(())
 }
}
pub fn apply(t:&Compact,id:&str,before:u64,after:u64)->Result<(Compact,Change),&'static str>{
 if before>1||after>1{return Err("membership bit")}
 let p=Change{id:id.into(),opening:t.proof(id)?,replacement:after};
 if p.opening.value!=before{return Err("opening membership")}
 let n=if before==after{t.clone()}else if after==1{t.insert(id)?}else{t.remove(id)?};
 p.verify(id,before,after,t.root(),n.root())?;Ok((n,p))
}
/// Ordered transitions: caller supplies expected identities, bits and each anchored root.
/// A self-consistent chain is not evidence of authorization.
pub fn verify_chain(opening:Hash,closing:Hash,steps:&[(String,u64,u64,Hash)],proofs:&[Change])->Result<(),&'static str>{
 if steps.len()!=proofs.len()||steps.len()>10000{return Err("chain length")}
 let mut root=opening;for ((id,b,a,next),p)in steps.iter().zip(proofs){p.verify(id,*b,*a,root,*next)?;root=*next;}
 if root!=closing{return Err("terminal root")}Ok(())
}
#[cfg(test)]mod tests{
 use super::*;use crate::{population::Population,membership_tree::Membership};
 fn fixture()->(Population,Compact){let p=Population::phase_ix();let mut t=Compact::new();for id in &p.known{t=t.insert(id).unwrap()}(p,t)}
 #[test]fn insertion(){let(mut p,t)=fixture();let(n,c)=apply(&t,"G",0,1).unwrap();p.known.insert("G".into());assert_eq!(n.root(),Membership::build(&p).unwrap().known_root());c.verify("G",0,1,t.root(),n.root()).unwrap();assert_eq!(t.proof("G").unwrap().value,0);}
 #[test]fn removal(){let(mut p,t)=fixture();let(n,c)=apply(&t,"A_0",1,0).unwrap();p.known.remove("A_0");assert_eq!(n.root(),Membership::build(&p).unwrap().known_root());c.verify("A_0",1,0,t.root(),n.root()).unwrap();assert_eq!(t.proof("A_0").unwrap().value,1);}
 #[test]fn unchanged(){let(_,t)=fixture();for(id,b)in [("A_0",1),("G",0)]{let(n,c)=apply(&t,id,b,b).unwrap();assert_eq!(n,t);c.verify(id,b,b,t.root(),t.root()).unwrap();}assert!(apply(&t,"A_0",0,1).is_err());assert!(apply(&t,"G",0,2).is_err());}
 #[test]fn tampering(){let(_,t)=fixture();let(n,c)=apply(&t,"G",0,1).unwrap();for i in [0,127,255]{let mut bad=c.clone();bad.opening.siblings[i][0]^=1;assert!(bad.verify("G",0,1,t.root(),n.root()).is_err());}let mut bad=c.clone();bad.opening.siblings.pop();assert!(bad.verify("G",0,1,t.root(),n.root()).is_err());assert!(c.verify("H",0,1,t.root(),n.root()).is_err());assert!(c.verify("G",0,0,t.root(),n.root()).is_err());assert!(c.verify("G",0,1,n.root(),n.root()).is_err());assert!(c.verify("G",0,1,t.root(),t.root()).is_err());}
 #[test]fn ordered_chain(){let(mut p,mut t)=fixture();let start=t.root();let mut steps=vec![];let mut proofs=vec![];for i in 0..30{let id=format!("G_{i}");let(n,c)=apply(&t,&id,0,1).unwrap();p.known.insert(id.clone());steps.push((id,0,1,n.root()));proofs.push(c);t=n;}let end=t.root();assert_eq!(end,Membership::build(&p).unwrap().known_root());verify_chain(start,end,&steps,&proofs).unwrap();proofs.swap(0,1);assert!(verify_chain(start,end,&steps,&proofs).is_err());assert!(verify_chain(start,end,&steps[..29],&proofs).is_err());assert!(verify_chain(start,end,&[],&[]).is_err());}
}
