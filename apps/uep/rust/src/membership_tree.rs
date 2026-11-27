//! UEP-273R: domain-separated authenticated identity membership. .dlw
use crate::{population::{Population,Period},identity_continuity};
use sha2::{Digest,Sha256};
use std::sync::Arc;
type Hash=[u8;32];
const DEPTH:usize=256;
fn hash(domain:&[u8],parts:&[&[u8]])->Hash{let mut h=Sha256::new();h.update(domain);for p in parts{h.update(p)}h.finalize().into()}
fn key(id:&str)->Result<Hash,&'static str>{if id.is_empty()||id.len()>30||!id.bytes().all(|b|b.is_ascii_alphanumeric()||b==b'_'||b==b'-'){return Err("identity syntax")}Ok(hash(b"OASIS-UEP-273R-key-v1",&[id.as_bytes()]))}
fn bit(k:&Hash,d:usize)->usize{usize::from((k[d/8]>>(7-d%8))&1)}
fn leaf(k:&Hash,v:u64)->Hash{hash(b"OASIS-UEP-273R-leaf-v1",&[k,&v.to_be_bytes()])}
fn branch(d:usize,l:&Hash,r:&Hash)->Hash{hash(b"OASIS-UEP-273R-branch-v1",&[&(d as u64).to_be_bytes(),l,r])}
fn empties()->[Hash;257]{let mut e=[[0;32];257];e[256]=hash(b"OASIS-UEP-273R-empty-v1",&[]);for d in (0..256).rev(){e[d]=branch(d,&e[d+1],&e[d+1]);}e}
#[derive(Clone,Debug,PartialEq,Eq)]
struct Node{digest:Hash,value:u64,children:[Option<Arc<Node>>;2],id:Option<String>}
fn profile_node(n:Node)->Arc<Node>{let _profile=crate::verification_profile::span(14);Arc::new(n)}
fn digest(n:&Option<Arc<Node>>,e:&[Hash;257],d:usize)->Hash{n.as_ref().map_or(e[d],|x|x.digest)}
fn update(n:&Option<Arc<Node>>,k:&Hash,id:&str,v:u64,e:&[Hash;257],d:usize)->Result<Option<Arc<Node>>,&'static str>{
 if d==DEPTH{if let Some(x)=n{if x.id.as_deref()!=Some(id){return Err("key collision")}}return Ok(if v==0{None}else{Some(profile_node(Node{digest:leaf(k,v),value:v,children:[None,None],id:Some(id.into())}))})}
 let mut c=n.as_ref().map_or([None,None],|x|x.children.clone());let i=bit(k,d);c[i]=update(&c[i],k,id,v,e,d+1)?;
 if c.iter().all(Option::is_none){return Ok(None)}
 Ok(Some(profile_node(Node{digest:branch(d,&digest(&c[0],e,d+1),&digest(&c[1],e,d+1)),value:0,children:c,id:None})))
}
#[derive(Clone,Debug,PartialEq,Eq)]
pub struct Proof{pub value:u64,pub siblings:Vec<Hash>}
impl Proof{pub fn verify(&self,id:&str,root:Hash)->Result<bool,&'static str>{let k=key(id)?;if self.siblings.len()!=DEPTH{return Err("proof length")}let mut h=if self.value==0{hash(b"OASIS-UEP-273R-empty-v1",&[])}else{leaf(&k,self.value)};for d in (0..DEPTH).rev(){let s=&self.siblings[d];h=if bit(&k,d)==0{branch(d,&h,s)}else{branch(d,s,&h)}}Ok(h==root)}}

#[derive(Clone,Debug,PartialEq,Eq)]
pub struct Membership{known:Option<Arc<Node>>,active:Option<Arc<Node>>,empty:Arc<[Hash;257]>,epoch:u64,count:u64,active_count:u64}
fn lookup(n:&Option<Arc<Node>>,id:&str,e:&[Hash;257])->Result<Proof,&'static str>{let k=key(id)?;let mut n=n.as_ref();let mut siblings=Vec::with_capacity(DEPTH);for d in 0..DEPTH{let i=bit(&k,d);siblings.push(n.map_or(e[d+1],|x|digest(&x.children[1-i],e,d+1)));n=n.and_then(|x|x.children[i].as_ref());}if let Some(x)=n{if x.id.as_deref()!=Some(id){return Err("key collision")}}Ok(Proof{value:n.map_or(0,|x|x.value),siblings})}
impl Membership{
 pub fn build(p:&Population)->Result<Self,&'static str>{let _profile=crate::verification_profile::span(11);
  if p.known.len()>10000||!p.active.is_subset(&p.known){return Err("population")}
  let mut n=Self{known:None,active:None,empty:Arc::new(empties()),epoch:p.epoch,count:p.known.len() as u64,active_count:p.active.len() as u64};
  for id in &p.known{n.known=update(&n.known,&key(id)?,id,1,&n.empty,0)?;}
  for id in &p.active{n.active=update(&n.active,&key(id)?,id,1,&n.empty,0)?;}Ok(n)
 }
 pub fn known_root(&self)->Hash{digest(&self.known,&self.empty,0)}
 pub fn active_root(&self)->Hash{digest(&self.active,&self.empty,0)}
 pub fn known_proof(&self,id:&str)->Result<Proof,&'static str>{lookup(&self.known,id,&self.empty)}
 pub fn active_proof(&self,id:&str)->Result<Proof,&'static str>{lookup(&self.active,id,&self.empty)}
 pub fn commitment(&self)->Hash{hash(b"OASIS-UEP-273R-membership-v1",&[&self.epoch.to_be_bytes(),&self.count.to_be_bytes(),&self.active_count.to_be_bytes(),&self.known_root(),&self.active_root()])}
 pub fn verify(&self,p:&Population)->Result<(),&'static str>{let _profile=crate::verification_profile::span(17);if self.commitment()!=Self::build(p)?.commitment(){return Err("membership parity")}Ok(())}
 pub fn advance(&self,p:&Population,q:&Population,r:&Period)->Result<Self,&'static str>{let _profile=crate::verification_profile::span(21);
  self.verify(p)?;let delta=identity_continuity::verify(p,q,r)?;let mut n=self.clone();
  for id in delta.departed{n.active=update(&n.active,&key(&id)?,&id,0,&n.empty,0)?;n.active_count=n.active_count.checked_sub(1).ok_or("active count")?;}
  for id in delta.entered{if n.known_proof(&id)?.value!=0{return Err("identity reuse")}let k=key(&id)?;n.known=update(&n.known,&k,&id,1,&n.empty,0)?;n.active=update(&n.active,&k,&id,1,&n.empty,0)?;n.count=n.count.checked_add(1).ok_or("count")?;n.active_count=n.active_count.checked_add(1).ok_or("active count")?;}
  n.epoch=q.epoch;n.verify(q)?;Ok(n)
 }
}
#[cfg(test)]mod tests{use super::*;use crate::population::settle;
fn req()->Period{Period{enter:vec![],depart:vec![],award:100,funding:600}}
#[test]fn proofs(){let p=Population::phase_ix();let m=Membership::build(&p).unwrap();for(id,known,active)in [("A_0",1,0),("A_1",1,1),("new",0,0)]{let k=m.known_proof(id).unwrap();let a=m.active_proof(id).unwrap();assert_eq!((k.value,a.value),(known,active));assert!(k.verify(id,m.known_root()).unwrap());assert!(a.verify(id,m.active_root()).unwrap());let mut bad=k.clone();bad.value^=1;assert!(!bad.verify(id,m.known_root()).unwrap());}}
#[test]fn departure(){let p=Population::phase_ix();let m=Membership::build(&p).unwrap();let mut r=req();r.depart=vec!["A_1".into()];let q=settle(&p,&r).unwrap().closing;let n=m.advance(&p,&q,&r).unwrap();assert_eq!(m.known_root(),n.known_root());assert_ne!(m.active_root(),n.active_root());assert_eq!(n.known_proof("A_1").unwrap().value,1);assert_eq!(n.active_proof("A_1").unwrap().value,0);}
#[test]fn churn(){let mut p=Population::phase_ix();let mut m=Membership::build(&p).unwrap();let mut current="A_1".to_string();for t in 0..30{let mut r=req();let next=format!("G_{t}");r.depart=vec![std::mem::replace(&mut current,next.clone())];r.enter=vec![next];let q=settle(&p,&r).unwrap().closing;m=m.advance(&p,&q,&r).unwrap();p=q;}assert_eq!(m.count,37);assert_eq!(m.active_count,6);assert_eq!(m.known_proof("A_1").unwrap().value,1);}
#[test]fn reject_reuse_erasure(){let p=Population::phase_ix();let m=Membership::build(&p).unwrap();let mut r=req();r.enter=vec!["A_0".into()];assert!(m.advance(&p,&p,&r).is_err());let mut q=settle(&p,&req()).unwrap().closing;q.known.remove("A_0");assert!(m.advance(&p,&q,&req()).is_err());}
#[test]fn immutable_and_stale(){let p=Population::phase_ix();let m=Membership::build(&p).unwrap();let mut r=req();r.enter=vec!["G".into()];let q=settle(&p,&r).unwrap().closing;let n=m.advance(&p,&q,&r).unwrap();assert_eq!(m.known_proof("G").unwrap().value,0);assert_eq!(n.known_proof("G").unwrap().value,1);assert!(m.verify(&q).is_err());assert!(n.verify(&p).is_err());}
}
