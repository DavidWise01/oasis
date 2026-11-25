//! UEP-224R: separate public automation dividends from restitution and universal awards. .dlw
use crate::{bridge::{Bridge,Shares},population::{Period,Settlement}};
#[derive(Clone,Debug,PartialEq,Eq)]
pub struct Revenue {pub public_equity:u64,pub licensing:u64,pub automation_royalties:u64,pub infrastructure_return:u64}
#[derive(Clone,Debug,PartialEq,Eq)]
pub struct Economy {bridge:Bridge,public_reserve:u64,dividend_reserved:u64,revenue_total:u64}
#[derive(Clone,Debug,PartialEq,Eq)]
pub struct Frame{pub next:Economy,pub universal:Settlement,pub dividend_each:u64,pub dividend_total:u64,pub restitution_unallocated:Shares}
impl Economy{
 pub fn new(bridge:Bridge)->Self{Self{bridge,public_reserve:0,dividend_reserved:0,revenue_total:0}}
 pub fn reserve(&self)->u64{self.public_reserve}
 pub fn bridge(&self)->&Bridge{&self.bridge}
 pub fn sync(&self,l:&crate::evidence::Ledger,head:[u8;32])->Result<Self,&'static str>{let mut n=self.clone();n.bridge=self.bridge.sync(l,head)?;Ok(n)}
 /// All revenues are synthetic net public receipts, independent of UBI and restitution funding.
 /// Equal supplemental dividend is capped by explicit policy; no award or liability is reduced.
 pub fn advance(&self,p:&Period,independent:Shares,r:&Revenue,cap_each:u64)->Result<Frame,&'static str>{
  let revenue=[r.public_equity,r.licensing,r.automation_royalties,r.infrastructure_return].into_iter().try_fold(0u64,|a,b|a.checked_add(b).ok_or("revenue overflow"))?;
  let available=self.public_reserve.checked_add(revenue).ok_or("reserve overflow")?;
  let f=self.bridge.advance(p,independent)?;
  let count=f.universal.closing.active.len() as u64;
  let each=available.checked_div(count).unwrap_or(0).min(cap_each);
  let total=each.checked_mul(count).ok_or("dividend overflow")?;
  let mut n=self.clone();n.bridge=f.next;n.public_reserve=available-total;
  n.revenue_total=n.revenue_total.checked_add(revenue).ok_or("cumulative revenue overflow")?;
  n.dividend_reserved=n.dividend_reserved.checked_add(total).ok_or("cumulative dividend overflow")?;
  if n.public_reserve.checked_add(n.dividend_reserved)!=Some(n.revenue_total){return Err("public account conservation")}
  Ok(Frame{next:n,universal:f.universal,dividend_each:each,dividend_total:total,restitution_unallocated:f.unallocated})
 }
}
#[cfg(test)]
mod tests{
 use super::*;use crate::{evidence::{Ledger,Event},restitution::Assessment};
 fn root()->Economy{let l=Ledger::default().append(Event::Estimate{id:"e".into(),valuation:10000,assessment:Assessment{target:"synthetic".into(),evidence_refs:vec!["source".into()],human_observation_ref:"human".into(),ai_observation_ref:"ai".into(),positive:[999;22],negative:[0;22]}}).unwrap().append(Event::AcceptModel{id:"a".into(),estimate_id:"e".into(),decision_ref:"model".into()}).unwrap();Economy::new(Bridge::genesis().sync(&l,l.head()).unwrap())}
 fn p(funding:u64)->Period{Period{enter:vec![],depart:vec![],award:100,funding}}
 fn r(v:u64)->Revenue{Revenue{public_equity:v,licensing:0,automation_royalties:0,infrastructure_return:0}}
 #[test]fn distinct_accounts(){let s=root();let a=s.advance(&p(500),Shares{carbon:100,ai:25},&r(1000),100).unwrap();let b=s.advance(&p(500),Shares{carbon:100,ai:25},&r(0),100).unwrap();assert_eq!(a.universal,b.universal);assert_eq!(a.next.bridge(),b.next.bridge());assert_eq!(a.dividend_each,100);assert_eq!(a.next.reserve(),400);assert_eq!(a.next.bridge().outstanding(),Shares{carbon:1540,ai:385});}
 #[test]fn empty_population(){let s=root();let mut p=p(0);p.depart=s.bridge().population().active.iter().cloned().collect();let f=s.advance(&p,Shares::default(),&r(100),100).unwrap();assert_eq!(f.dividend_total,0);assert_eq!(f.next.reserve(),100);}
 #[test]fn overflow(){assert!(root().advance(&p(600),Shares::default(),&Revenue{public_equity:u64::MAX,licensing:1,automation_royalties:0,infrastructure_return:0},100).is_err());}
 #[test]fn grid(){for rev in [0,300,1000]{for ubi in [0,500,600]{for carbon in [0,100,2000]{let mut a=root();let mut b=root();for _ in 0..360{let f=a.advance(&p(ubi),Shares{carbon,ai:25},&r(rev),100).unwrap();let z=b.advance(&p(ubi),Shares{carbon,ai:25},&r(0),100).unwrap();assert_eq!(f.universal,z.universal);assert_eq!(f.next.bridge(),z.next.bridge());assert_eq!(a.reserve()+rev,f.next.reserve()+f.dividend_total);a=f.next;b=z.next;}}}}}
}
