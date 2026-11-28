//! UEP-272R: persistent sparse authenticated beneficiary balances; synthetic only. .dlw
use crate::{population::{Population,Period},arrears::{self,Audit}};
use sha2::{Digest,Sha256};
use std::{sync::Arc,collections::BTreeMap};
type Hash=[u8;32];
const DEPTH:usize=256;
fn hash(domain:&[u8],parts:&[&[u8]])->Hash{let mut h=Sha256::new();h.update(domain);for p in parts{h.update(p)}h.finalize().into()}
fn key(id:&str)->Result<Hash,&'static str>{if id.is_empty()||id.len()>30||!id.bytes().all(|b|b.is_ascii_alphanumeric()||b==b'_'||b==b'-'){return Err("identity syntax")}Ok(hash(b"OASIS-UEP-272R-key-v1",&[id.as_bytes()]))}
fn bit(k:&Hash,d:usize)->usize{usize::from((k[d/8]>>(7-d%8))&1)}
fn leaf(k:&Hash,v:u64)->Hash{hash(b"OASIS-UEP-272R-leaf-v1",&[k,&v.to_be_bytes()])}
fn branch(d:usize,l:&Hash,r:&Hash)->Hash{hash(b"OASIS-UEP-272R-branch-v1",&[&(d as u64).to_be_bytes(),l,r])}
fn empties()->[Hash;257]{let mut e=[[0;32];257];e[256]=hash(b"OASIS-UEP-272R-empty-v1",&[]);for d in (0..256).rev(){e[d]=branch(d,&e[d+1],&e[d+1]);}e}
#[derive(Clone,Debug,PartialEq,Eq)]
struct Node{digest:Hash,value:u64,children:[Option<Arc<Node>>;2],id:Option<String>}
fn profile_node(n:Node)->Arc<Node>{let _profile=crate::verification_profile::span(13);Arc::new(n)}
fn digest(n:&Option<Arc<Node>>,e:&[Hash;257],d:usize)->Hash{n.as_ref().map_or(e[d],|x|x.digest)}
fn update(n:&Option<Arc<Node>>,k:&Hash,id:&str,v:u64,e:&[Hash;257],d:usize)->Result<Option<Arc<Node>>,&'static str>{
 if d==DEPTH{if let Some(x)=n{if x.id.as_deref()!=Some(id){return Err("key collision")}}return Ok(if v==0{None}else{Some(profile_node(Node{digest:leaf(k,v),value:v,children:[None,None],id:Some(id.into())}))})}
 let mut c=n.as_ref().map_or([None,None],|x|x.children.clone());let i=bit(k,d);c[i]=update(&c[i],k,id,v,e,d+1)?;
 if c.iter().all(Option::is_none){return Ok(None)}
 Ok(Some(profile_node(Node{digest:branch(d,&digest(&c[0],e,d+1),&digest(&c[1],e,d+1)),value:0,children:c,id:None})))
}
#[derive(Clone,Debug,PartialEq,Eq)]
pub struct Proof{pub value:u64,pub siblings:Vec<Hash>}
impl Proof{pub fn verify(&self,id:&str,root:Hash)->Result<bool,&'static str>{let k=key(id)?;if self.siblings.len()!=DEPTH{return Err("proof length")}let mut h=if self.value==0{hash(b"OASIS-UEP-272R-empty-v1",&[])}else{leaf(&k,self.value)};for d in (0..DEPTH).rev(){let s=&self.siblings[d];h=if bit(&k,d)==0{branch(d,&h,s)}else{branch(d,s,&h)}}Ok(h==root)}}
#[derive(Clone,Debug,PartialEq,Eq)]
pub struct Tree{root:Option<Arc<Node>>,empty:Arc<[Hash;257]>,identified:u64,unattributed:u64,epoch:u64}
impl Tree{
 pub fn build(p:&Population)->Result<Self,&'static str>{let _profile=crate::verification_profile::span(10);
  let mut n=Self{root:None,empty:Arc::new(empties()),identified:0,unattributed:p.unattributed,epoch:p.epoch};
  let mut m=BTreeMap::<String,u64>::new();for l in &p.lots{if l.amount==0||l.origin>p.epoch||!p.known.contains(&l.id){return Err("invalid lot")}let v=m.entry(l.id.clone()).or_default();*v=v.checked_add(l.amount).ok_or("balance overflow")?;}for(id,v)in m{n.set(&id,v)?;}n.total()?;Ok(n)
 }
 pub fn root(&self)->Hash{digest(&self.root,&self.empty,0)}
 pub fn total(&self)->Result<u64,&'static str>{self.identified.checked_add(self.unattributed).ok_or("aggregate overflow")}
 pub fn proof(&self,id:&str)->Result<Proof,&'static str>{let k=key(id)?;let mut n=self.root.as_ref();let mut siblings=Vec::with_capacity(DEPTH);for d in 0..DEPTH{let i=bit(&k,d);siblings.push(n.map_or(self.empty[d+1],|x|digest(&x.children[1-i],&self.empty,d+1)));n=n.and_then(|x|x.children[i].as_ref());}if let Some(x)=n{if x.id.as_deref()!=Some(id){return Err("key collision")}}Ok(Proof{value:n.map_or(0,|x|x.value),siblings})}
 pub fn balance(&self,id:&str)->Result<u64,&'static str>{let k=key(id)?;let mut n=self.root.as_ref();for d in 0..DEPTH{n=n.and_then(|x|x.children[bit(&k,d)].as_ref());if n.is_none(){return Ok(0)}}let x=n.ok_or("missing leaf")?;if x.id.as_deref()!=Some(id){return Err("key collision")}Ok(x.value)}
 fn set(&mut self,id:&str,v:u64)->Result<(),&'static str>{let old=self.balance(id)?;if old==v{return Ok(())}let total=self.identified.checked_sub(old).and_then(|n|n.checked_add(v)).ok_or("aggregate overflow")?;total.checked_add(self.unattributed).ok_or("total overflow")?;let root=update(&self.root,&key(id)?,id,v,&self.empty,0)?;self.root=root;self.identified=total;Ok(())}
 pub fn commitment(&self)->Hash{hash(b"OASIS-UEP-272R-root-v1",&[&self.epoch.to_be_bytes(),&self.identified.to_be_bytes(),&self.unattributed.to_be_bytes(),&self.root()])}
 pub fn verify(&self,p:&Population)->Result<(),&'static str>{let _profile=crate::verification_profile::span(16);if self.commitment()!=Self::build(p)?.commitment(){return Err("tree parity")}Ok(())}
 /// Qualification mode: derive deltas from canonical audit, then compare with rebuilt tree.
 pub fn advance(&self,p:&Population,r:&Period)->Result<(Self,Audit,usize),&'static str>{
  self.verify(p)?;let a=arrears::advance(p,r)?;let (n,k)=self.apply_audit(r,&a)?;Ok((n,a,k))
 }
 // Internal consumer: caller must establish opening parity and generate canonical audit.
 pub(crate) fn apply_audit(&self,r:&Period,a:&Audit)->Result<(Self,usize),&'static str>{let _profile=crate::verification_profile::span(20);let mut n=self.clone();let mut delta=BTreeMap::<String,i128>::new();
  for(id,v)in &a.settlement.historical_reserved{*delta.entry(id.clone()).or_default()-=i128::from(*v);}
  for x in &a.settlement.awards{*delta.entry(x.id.clone()).or_default()+=i128::from(x.due.checked_sub(x.funded).ok_or("award")?);}
  let mut changed=0;for(id,d)in delta{if d==0{continue}let v=u64::try_from(i128::from(n.balance(&id)?)+d).map_err(|_|"delta range")?;n.set(&id,v)?;changed+=1;}
  n.epoch=a.settlement.closing.epoch;n.verify(&a.settlement.closing)?;
  if n.total()?!=a.settlement.closing.outstanding()?||a.settlement.current_funded!=a.settlement.current_due.min(r.funding){return Err("accounting parity")}Ok((n,changed))
 }
}
#[cfg(test)]mod tests{
 use super::*;
 fn req(f:u64)->Period{Period{enter:vec![],depart:vec![],award:100,funding:f}}
 #[test]fn proofs(){let p=Population::phase_ix();let(t,a,_)=Tree::build(&p).unwrap().advance(&p,&req(0)).unwrap();for id in ["A_1","B_0","unknown"]{let proof=t.proof(id).unwrap();assert!(proof.verify(id,t.root()).unwrap());let mut bad=proof.clone();bad.value+=1;assert!(!bad.verify(id,t.root()).unwrap());let mut bad=proof.clone();bad.siblings[0][0]^=1;assert!(!bad.verify(id,t.root()).unwrap());}assert_eq!(t.balance("unknown").unwrap(),0);assert_eq!(a.settlement.closing.outstanding().unwrap(),1000);}
 #[test]fn canonical_order(){let p=Population::phase_ix();let mut a=Tree::build(&p).unwrap();let mut b=a.clone();for(id,v)in [("A",5),("B",7),("C",9)]{a.set(id,v).unwrap()}for(id,v)in [("C",9),("B",7),("A",5)]{b.set(id,v).unwrap()}assert_eq!(a.commitment(),b.commitment());a.set("B",0).unwrap();b.set("B",0).unwrap();assert_eq!(a.root(),b.root());}
 #[test]fn immutable_update(){let p=Population::phase_ix();let mut a=Tree::build(&p).unwrap();a.set("A",100).unwrap();a.set("B",100).unwrap();let before=a.clone();let mut b=a.clone();b.set("A",50).unwrap();assert_eq!(a,before);assert_eq!(a.balance("A").unwrap(),100);assert_eq!(b.balance("A").unwrap(),50);assert_eq!(b.balance("B").unwrap(),100);assert_ne!(a.root(),b.root());}
 #[test]fn mixed_parity(){let mut p=Population::phase_ix();let mut t=Tree::build(&p).unwrap();for i in 0..120{let(n,a,_)=t.advance(&p,&req([0,500,600,750,1200][i%5])).unwrap();p=a.settlement.closing;t=n;}t.verify(&p).unwrap();assert_eq!(t.total().unwrap(),p.outstanding().unwrap());}
 #[test]fn departed_and_stale(){let p=Population::phase_ix();let(t,a,_)=Tree::build(&p).unwrap().advance(&p,&req(0)).unwrap();let p=a.settlement.closing;let mut r=req(650);r.enter=vec!["G".into()];r.depart=vec!["A_1".into()];let(n,a,c)=t.advance(&p,&r).unwrap();assert_eq!(c,1);assert_eq!(n.balance("A_1").unwrap(),50);assert_eq!(n.balance("G").unwrap(),0);assert!(t.advance(&a.settlement.closing,&req(600)).is_err());assert!(n.proof("A_1").unwrap().verify("A_1",n.root()).unwrap());}
}

// UEP-285R: crate-internal proof-checked replacement; no reconstruction.
impl Tree{
 pub(crate) fn replace_qualified(&self,id:&str,old:u64,new:u64)->Result<Self,&'static str>{
  let p=self.proof(id)?;if p.value!=old||!p.verify(id,self.root())?{return Err("opening leaf")}
  let mut n=self.clone();n.set(id,new)?;
  let mut q=p;q.value=new;if !q.verify(id,n.root())?{return Err("closing leaf")}Ok(n)
 }
 pub(crate) fn finish_qualified(&self,epoch:u64,unattributed:u64,total:u64)->Result<Self,&'static str>{
  if self.epoch.checked_add(1)!=Some(epoch)||self.unattributed!=unattributed||self.total()?!=total{return Err("closing metadata")}
  let mut n=self.clone();n.epoch=epoch;Ok(n)
 }
}
