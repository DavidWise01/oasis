//! UEP-274R: persistent authenticated FIFO obligations, stable local sequence positions. .dlw
use crate::{population::{Population,Period,Lot},arrears::{self,Audit,Receipt}};
use sha2::{Digest,Sha256};
use std::sync::Arc;
type Hash=[u8;32];
fn hash(d:&[u8],p:&[&[u8]])->Hash{let mut h=Sha256::new();h.update(d);for x in p{h.update(x)}h.finalize().into()}
fn leaf(i:u64,l:&Lot)->Hash{hash(b"OASIS-UEP-274R-lot-v1",&[&i.to_be_bytes(),&l.origin.to_be_bytes(),&(l.id.len() as u64).to_be_bytes(),l.id.as_bytes(),&l.amount.to_be_bytes()])}
fn branch(d:usize,l:Hash,r:Hash)->Hash{hash(b"OASIS-UEP-274R-node-v1",&[&(d as u64).to_be_bytes(),&l,&r])}
fn empties()->[Hash;65]{let mut e=[[0;32];65];e[64]=hash(b"OASIS-UEP-274R-empty-v1",&[]);for d in (0..64).rev(){e[d]=branch(d,e[d+1],e[d+1])}e}
#[derive(Clone,Debug,PartialEq,Eq)]
struct Node{h:Hash,c:[Option<Arc<Node>>;2],lot:Option<Lot>}
fn root(n:&Option<Arc<Node>>,e:&[Hash;65],d:usize)->Hash{n.as_ref().map_or(e[d],|x|x.h)}
fn bit(i:u64,d:usize)->usize{((i>>(63-d))&1) as usize}
fn set(n:&Option<Arc<Node>>,e:&[Hash;65],i:u64,l:Option<Lot>,d:usize)->Option<Arc<Node>>{
 if d==64{return l.map(|l|Arc::new(Node{h:leaf(i,&l),c:[None,None],lot:Some(l)}))}
 let mut c=n.as_ref().map_or([None,None],|x|x.c.clone());let b=bit(i,d);c[b]=set(&c[b],e,i,l,d+1);
 if c.iter().all(Option::is_none){return None}
 Some(Arc::new(Node{h:branch(d,root(&c[0],e,d+1),root(&c[1],e,d+1)),c,lot:None}))
}
#[derive(Clone,Debug,PartialEq,Eq)]
pub struct Queue{tree:Option<Arc<Node>>,empty:Arc<[Hash;65]>,head:u64,tail:u64,epoch:u64,total:u64,unattributed:u64,retirement:Hash}
impl Queue{
 pub fn build(p:&Population)->Result<Self,&'static str>{if p.lots.windows(2).any(|w|w[0].origin>w[1].origin){return Err("chronology")}let mut n=Self{tree:None,empty:Arc::new(empties()),head:0,tail:0,epoch:p.epoch,total:0,unattributed:p.unattributed,retirement:hash(b"OASIS-UEP-274R-retirement-genesis-v1",&[])};for l in &p.lots{if l.amount==0||l.origin>p.epoch||!p.known.contains(&l.id){return Err("lot")}n.push(l.clone())?;}n.verify(p)?;Ok(n)}
 pub fn head(&self)->u64{self.head}
 pub fn tail(&self)->u64{self.tail}
 pub fn root(&self)->Hash{root(&self.tree,&self.empty,0)}
 pub fn retirement(&self)->Hash{self.retirement}
 pub fn commitment(&self)->Hash{hash(b"OASIS-UEP-274R-queue-v1",&[&self.epoch.to_be_bytes(),&self.head.to_be_bytes(),&self.tail.to_be_bytes(),&self.total.to_be_bytes(),&self.unattributed.to_be_bytes(),&self.root(),&self.retirement])}
 pub fn get(&self,i:u64)->Option<&Lot>{let mut n=self.tree.as_ref();for d in 0..64{n=n.and_then(|x|x.c[bit(i,d)].as_ref());}n.and_then(|x|x.lot.as_ref())}
 fn push(&mut self,l:Lot)->Result<(),&'static str>{let t=self.tail.checked_add(1).ok_or("tail")?;let v=self.total.checked_add(l.amount).ok_or("balance")?;v.checked_add(self.unattributed).ok_or("total")?;self.tree=set(&self.tree,&self.empty,self.tail,Some(l),0);self.tail=t;self.total=v;Ok(())}
 pub fn verify(&self,p:&Population)->Result<(),&'static str>{if self.epoch!=p.epoch||self.unattributed!=p.unattributed||self.tail.checked_sub(self.head)!=Some(p.lots.len() as u64)||self.total.checked_add(self.unattributed)!=Some(p.outstanding()?){return Err("queue metadata")}for(i,l)in (self.head..self.tail).zip(&p.lots){if self.get(i)!=Some(l){return Err("lot parity")}}Ok(())}
 pub fn advance(&self,p:&Population,r:&Period)->Result<(Self,Audit,usize),&'static str>{
 self.verify(p)?;let a=arrears::advance(p,r)?;let mut n=self.clone();let mut left=r.funding.checked_sub(a.settlement.current_funded).ok_or("funding")?;let mut receipts=Vec::new();let mut changes=0;
 while left>0&&n.head<n.tail{let i=n.head;let l=n.get(i).ok_or("head missing")?.clone();let paid=left.min(l.amount);left-=paid;let remaining=l.amount-paid;n.total=n.total.checked_sub(paid).ok_or("debit")?;
 receipts.push(Receipt{origin:l.origin,beneficiary:l.id.clone(),opening_index:usize::try_from(i-self.head).map_err(|_|"index")?,reserved:paid,remainder:remaining,departed:!a.settlement.closing.active.contains(&l.id)});
 if remaining==0{n.retirement=hash(b"OASIS-UEP-274R-retire-v1",&[&n.retirement,&leaf(i,&l),&a.settlement.closing.epoch.to_be_bytes()]);n.tree=set(&n.tree,&n.empty,i,None,0);n.head=n.head.checked_add(1).ok_or("head")?;}else{n.tree=set(&n.tree,&n.empty,i,Some(Lot{amount:remaining,..l}),0);}changes+=1;}
 n.epoch=a.settlement.closing.epoch;for x in &a.settlement.awards{let v=x.due.checked_sub(x.funded).ok_or("award")?;if v>0{n.push(Lot{origin:n.epoch,id:x.id.clone(),amount:v})?;changes+=1;}}
 if receipts!=a.receipts||left!=a.settlement.unallocated{return Err("receipt parity")}n.verify(&a.settlement.closing)?;Ok((n,a,changes))
 }
}
#[cfg(test)]mod tests{use super::*;fn r(f:u64)->Period{Period{enter:vec![],depart:vec![],award:100,funding:f}}
#[test]fn scarcity(){let mut p=Population::phase_ix();let mut q=Queue::build(&p).unwrap();for _ in 0..120{let(n,a,c)=q.advance(&p,&r(500)).unwrap();assert_eq!(c,6);assert_eq!(n.head(),0);p=a.settlement.closing;q=n;}assert_eq!(q.tail(),720);let(n,_,c)=q.advance(&p,&r(600)).unwrap();assert_eq!(c,0);assert_eq!(n.root(),q.root());}
#[test]fn partial(){let p=Population::phase_ix();let(q,a,_)=Queue::build(&p).unwrap().advance(&p,&r(0)).unwrap();let(n,b,c)=q.advance(&a.settlement.closing,&r(750)).unwrap();assert_eq!((n.head(),n.tail(),c),(1,6,2));assert_eq!(n.get(1).unwrap().amount,50);assert_eq!(q.get(0).unwrap().amount,100);assert_eq!(b.receipts[1].remainder,50);assert_ne!(q.retirement(),n.retirement());}
#[test]fn retirement(){let p=Population::phase_ix();let(q,a,_)=Queue::build(&p).unwrap().advance(&p,&r(0)).unwrap();let(n,b,_)=q.advance(&a.settlement.closing,&r(1200)).unwrap();assert_eq!(n.head(),6);assert_eq!(n.tail(),6);let rebuilt=Queue::build(&b.settlement.closing).unwrap();assert_eq!(n.root(),rebuilt.root());assert_ne!(n.commitment(),rebuilt.commitment());let(z,_,_)=n.advance(&b.settlement.closing,&r(500)).unwrap();assert_eq!(z.tail(),12);}
#[test]fn departed_stale(){let p=Population::phase_ix();let(q,a,_)=Queue::build(&p).unwrap().advance(&p,&r(0)).unwrap();let mut x=r(650);x.enter=vec!["G".into()];x.depart=vec!["A_1".into()];let(n,b,_)=q.advance(&a.settlement.closing,&x).unwrap();assert!(b.receipts[0].departed);assert_eq!(n.get(0).unwrap().id,"A_1");assert!(q.advance(&b.settlement.closing,&r(600)).is_err());}
#[test]fn mixed(){let mut p=Population::phase_ix();let mut q=Queue::build(&p).unwrap();for t in 0..120{let(n,a,_)=q.advance(&p,&r([0,500,600,750,1200][t%5])).unwrap();p=a.settlement.closing;q=n;}q.verify(&p).unwrap();}
}
