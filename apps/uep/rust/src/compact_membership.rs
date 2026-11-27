//! UEP-282R: compressed binary radix tree preserving UEP-273R logical roots. .dlw
use sha2::{Digest,Sha256};
use std::sync::Arc;
type Hash=[u8;32];
fn hash(d:&[u8],p:&[&[u8]])->Hash{let mut h=Sha256::new();h.update(d);for x in p{h.update(x)}h.finalize().into()}
fn key(id:&str)->Result<Hash,&'static str>{if id.is_empty()||id.len()>30||!id.bytes().all(|b|b.is_ascii_alphanumeric()||b==b'_'||b==b'-'){return Err("identity syntax")}Ok(hash(b"OASIS-UEP-273R-key-v1",&[id.as_bytes()]))}
fn bit(k:&Hash,d:usize)->usize{((k[d/8]>>(7-d%8))&1) as usize}
fn branch(d:usize,l:Hash,r:Hash)->Hash{hash(b"OASIS-UEP-273R-branch-v1",&[&(d as u64).to_be_bytes(),&l,&r])}
fn empty()->[Hash;257]{let mut e=[[0;32];257];e[256]=hash(b"OASIS-UEP-273R-empty-v1",&[]);for d in (0..256).rev(){e[d]=branch(d,e[d+1],e[d+1])}e}
fn lift(mut h:Hash,k:&Hash,from:usize,to:usize,e:&[Hash;257])->Hash{for d in (to..from).rev(){h=if bit(k,d)==0{branch(d,h,e[d+1])}else{branch(d,e[d+1],h)}}h}
#[derive(Clone,Debug,PartialEq,Eq)]
struct Node{key:Hash,depth:usize,digest:Hash,kind:Kind}
#[derive(Clone,Debug,PartialEq,Eq)]
enum Kind{Leaf(String),Fork(Arc<Node>,Arc<Node>)}
fn leaf(id:&str,k:Hash)->Arc<Node>{Arc::new(Node{key:k,depth:256,digest:hash(b"OASIS-UEP-273R-leaf-v1",&[&k,&1u64.to_be_bytes()]),kind:Kind::Leaf(id.into())})}
fn fork(d:usize,a:Arc<Node>,b:Arc<Node>,e:&[Hash;257])->Arc<Node>{let(l,r)=if bit(&a.key,d)==0{(a,b)}else{(b,a)};Arc::new(Node{key:l.key,depth:d,digest:branch(d,lift(l.digest,&l.key,l.depth,d+1,e),lift(r.digest,&r.key,r.depth,d+1,e)),kind:Kind::Fork(l,r)})}
fn common(a:&Hash,b:&Hash)->usize{(0..256).find(|&i|bit(a,i)!=bit(b,i)).unwrap_or(256)}
fn insert(n:&Arc<Node>,id:&str,k:Hash,e:&[Hash;257])->Result<Arc<Node>,&'static str>{let d=common(&n.key,&k);if d<n.depth{return Ok(fork(d,n.clone(),leaf(id,k),e))}match &n.kind{Kind::Leaf(old)=>if old==id{Ok(n.clone())}else{Err("key collision")},Kind::Fork(l,r)=>if bit(&k,n.depth)==0{Ok(fork(n.depth,insert(l,id,k,e)?,r.clone(),e))}else{Ok(fork(n.depth,l.clone(),insert(r,id,k,e)?,e))}}}
fn remove(n:&Arc<Node>,id:&str,k:&Hash,e:&[Hash;257])->Result<Option<Arc<Node>>,&'static str>{if common(&n.key,k)<n.depth{return Ok(Some(n.clone()))}match &n.kind{Kind::Leaf(old)=>if old==id{Ok(None)}else{Err("key collision")},Kind::Fork(l,r)=>{if bit(k,n.depth)==0{Ok(Some(match remove(l,id,k,e)?{Some(x)=>fork(n.depth,x,r.clone(),e),None=>r.clone()}))}else{Ok(Some(match remove(r,id,k,e)?{Some(x)=>fork(n.depth,l.clone(),x,e),None=>l.clone()}))}}}}
#[derive(Clone,Debug,PartialEq,Eq)]
pub struct Compact{root:Option<Arc<Node>>,empty:Arc<[Hash;257]>}
impl Compact{
 pub fn new()->Self{Self{root:None,empty:Arc::new(empty())}}
 pub fn root(&self)->Hash{self.root.as_ref().map_or(self.empty[0],|n|lift(n.digest,&n.key,n.depth,0,&self.empty))}
 pub fn insert(&self,id:&str)->Result<Self,&'static str>{let k=key(id)?;Ok(Self{root:Some(match &self.root{Some(n)=>insert(n,id,k,&self.empty)?,None=>leaf(id,k)}),empty:self.empty.clone()})}
 pub fn remove(&self,id:&str)->Result<Self,&'static str>{let k=key(id)?;Ok(Self{root:match &self.root{Some(n)=>remove(n,id,&k,&self.empty)?,None=>None},empty:self.empty.clone()})}
 pub fn nodes(&self)->usize{fn count(n:&Node)->usize{match &n.kind{Kind::Leaf(_)=>1,Kind::Fork(l,r)=>1+count(l)+count(r)}}self.root.as_ref().map_or(0,|n|count(n))}
 pub fn proof(&self,id:&str)->Result<crate::membership_tree::Proof,&'static str>{let k=key(id)?;let mut siblings=self.empty[1..].to_vec();let mut n=self.root.as_ref();let mut value=0;while let Some(x)=n{let d=common(&x.key,&k);if d<x.depth{siblings[d]=lift(x.digest,&x.key,x.depth,d+1,&self.empty);break}match &x.kind{Kind::Leaf(old)=>{if old!=id{return Err("key collision")}value=1;break},Kind::Fork(l,r)=>{let(a,b)=if bit(&k,x.depth)==0{(l,r)}else{(r,l)};siblings[x.depth]=lift(b.digest,&b.key,b.depth,x.depth+1,&self.empty);n=Some(a)}}}Ok(crate::membership_tree::Proof{value,siblings})}
}
impl Default for Compact{fn default()->Self{Self::new()}}
#[cfg(test)]mod tests{
 use super::*;use crate::{population::Population,membership_tree::Membership};
 fn fixture()->(Population,Compact){let p=Population::phase_ix();let mut t=Compact::new();for id in &p.known{t=t.insert(id).unwrap()}(p,t)}
 #[test]fn root_and_proof(){let(p,t)=fixture();let m=Membership::build(&p).unwrap();assert_eq!(t.root(),m.known_root());for id in ["A_0","A_1","B_0","unknown","G_0"]{let a=t.proof(id).unwrap();assert_eq!(a,m.known_proof(id).unwrap());assert!(a.verify(id,t.root()).unwrap());}assert_eq!(t.nodes(),2*p.known.len()-1);}
 #[test]fn order(){let(p,a)=fixture();let mut b=Compact::new();for id in p.known.iter().rev(){b=b.insert(id).unwrap()}assert_eq!(a.root(),b.root());assert_eq!(a,b);}
 #[test]fn removal(){let(mut p,t)=fixture();let n=t.remove("A_0").unwrap();p.known.remove("A_0");assert_eq!(n.root(),Membership::build(&p).unwrap().known_root());assert_eq!(t.proof("A_0").unwrap().value,1);assert_eq!(n.proof("A_0").unwrap().value,0);assert_eq!(n.remove("missing").unwrap(),n);}
 #[test]fn churn(){let(mut p,mut t)=fixture();for i in 0..100{let id=format!("G_{i}");p.known.insert(id.clone());t=t.insert(&id).unwrap();if i%10==0{assert_eq!(t.root(),Membership::build(&p).unwrap().known_root());assert_eq!(t.nodes(),2*p.known.len()-1);}}assert_eq!(t.root(),Membership::build(&p).unwrap().known_root());}
 #[test]fn empty_and_single(){let a=Compact::new();let b=a.insert("X").unwrap();assert_eq!(b.nodes(),1);assert_eq!(b.insert("X").unwrap(),b);assert_eq!(b.remove("X").unwrap(),a);assert!(a.proof("X").unwrap().verify("X",a.root()).unwrap());assert!(b.proof("Y").unwrap().verify("Y",b.root()).unwrap());assert!(a.insert("bad id").is_err());}
}
