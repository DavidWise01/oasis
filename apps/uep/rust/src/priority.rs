//! UEP-206R: aggregate case prioritization; no personal inherited liability. .dlw
use crate::bridge::{Bridge,Shares};
use crate::evidence::{Event,Ledger};
use crate::population::{Period,Settlement};
use crate::restitution::{assessed_estimate,Estimate};
use std::collections::BTreeMap;
#[derive(Clone,Debug,PartialEq,Eq)]
pub struct Priority { pub origin:u64, pub affected:u64, pub deprivation:u16, pub harm:u16, pub urgency:u16, pub source_ref:String }
#[derive(Clone,Debug,PartialEq,Eq)]
pub struct Case { pub id:String, pub priority:Priority, pub assessed:Shares, pub reserved:Shares }
#[derive(Clone,Debug,PartialEq,Eq)]
pub struct Engine { bridge:Bridge, cases:BTreeMap<String,Case>, epoch:u64 }
#[derive(Clone,Debug,PartialEq,Eq)]
pub struct Allocation { pub id:String, pub amount:Shares }
#[derive(Clone,Debug,PartialEq,Eq)]
pub struct Frame { pub next:Engine, pub allocations:Vec<Allocation>, pub universal:Settlement, pub unallocated:Shares }
impl Engine {
 pub fn genesis()->Self{Self{bridge:Bridge::genesis(),cases:BTreeMap::new(),epoch:6}}
 pub fn cases(&self)->&BTreeMap<String,Case>{&self.cases}
 pub fn sync(&self,l:&Ledger,head:[u8;32],metadata:&BTreeMap<String,Priority>)->Result<Self,&'static str>{
    let mut next=self.clone();next.bridge=self.bridge.sync(l,head)?;
    let mut estimates=BTreeMap::<String,Estimate>::new();
    for r in l.records(){match &r.event{
      Event::Estimate{id,valuation,assessment}=>{estimates.insert(id.clone(),assessed_estimate(*valuation,assessment)?);}
      Event::AcceptModel{estimate_id,..}=>{
        let p=metadata.get(estimate_id).ok_or("missing priority")?;
        if p.origin>self.epoch||p.affected==0||p.affected>1_000_000_000||[p.deprivation,p.harm,p.urgency].iter().any(|&x|x>1000)||p.source_ref.trim().is_empty()||p.source_ref.len()>4096{return Err("invalid priority")}
        if let Some(old)=next.cases.get(estimate_id){if &old.priority!=p{return Err("priority rewrite")}}
        else {let e=estimates.get(estimate_id).ok_or("missing estimate")?;next.cases.insert(estimate_id.clone(),Case{id:estimate_id.clone(),priority:p.clone(),assessed:Shares{carbon:e.carbon_cents,ai:e.ai_cents},reserved:Shares::default()});}
      }
    }}
    if metadata.len()!=next.cases.len(){return Err("unexpected priority metadata")}
    next.reconcile()?;Ok(next)
 }
 fn reconcile(&self)->Result<(),&'static str>{
    let a=self.cases.values().fold((0u128,0u128,0u128,0u128),|(a,b,c,d),x|(a+x.assessed.carbon as u128,b+x.assessed.ai as u128,c+x.reserved.carbon as u128,d+x.reserved.ai as u128));
    let s=self.bridge.assessed();let f=self.bridge.funded();
    if a!=(s.carbon as u128,s.ai as u128,f.carbon as u128,f.ai as u128)||self.cases.values().any(|x|x.reserved.carbon>x.assessed.carbon||x.reserved.ai>x.assessed.ai){return Err("case reconciliation")}Ok(())
 }
 pub fn advance(&self,p:&Period,funds:Shares)->Result<Frame,&'static str>{
    self.reconcile()?;let b=self.bridge.advance(p,funds.clone())?;let mut next=self.clone();
    next.epoch=self.epoch.checked_add(1).ok_or("epoch overflow")?;
    let mut order:Vec<_>=self.cases.values().collect();
    // Lexicographic: urgency, deprivation, harm, age, affected population, stable ID.
    order.sort_by(|a,b|b.priority.urgency.cmp(&a.priority.urgency).then(b.priority.deprivation.cmp(&a.priority.deprivation)).then(b.priority.harm.cmp(&a.priority.harm)).then(a.priority.origin.cmp(&b.priority.origin)).then(b.priority.affected.cmp(&a.priority.affected)).then(a.id.cmp(&b.id)));
    let mut left=funds;let mut allocations=Vec::new();
    for x in order{let c=next.cases.get_mut(&x.id).ok_or("missing case")?;
        let amount=Shares{carbon:left.carbon.min(c.assessed.carbon-c.reserved.carbon),ai:left.ai.min(c.assessed.ai-c.reserved.ai)};
        c.reserved.carbon+=amount.carbon;c.reserved.ai+=amount.ai;left.carbon-=amount.carbon;left.ai-=amount.ai;
        if amount.carbon>0||amount.ai>0{allocations.push(Allocation{id:x.id.clone(),amount});}
    }
    if left!=b.unallocated{return Err("fund reconciliation")}
    next.bridge=b.next;next.reconcile()?;Ok(Frame{next,allocations,universal:b.universal,unallocated:left})
 }
}
#[cfg(test)]
mod tests{
 use super::*;use crate::restitution::Assessment;
 fn fixture()->(Ledger,BTreeMap<String,Priority>){
   let mut l=Ledger::default();let mut m=BTreeMap::new();
   for (id,origin,urgency) in [("old",1,300),("urgent",5,900),("middle",3,300)]{
     l=l.append(Event::Estimate{id:id.into(),valuation:10000,assessment:Assessment{target:"synthetic aggregate".into(),evidence_refs:vec!["source".into()],human_observation_ref:"human".into(),ai_observation_ref:"ai".into(),positive:[999;22],negative:[0;22]}}).unwrap();
     l=l.append(Event::AcceptModel{id:format!("accept-{id}"),estimate_id:id.into(),decision_ref:"model".into()}).unwrap();
     m.insert(id.into(),Priority{origin,affected:100,deprivation:500,harm:500,urgency,source_ref:"synthetic metadata".into()});
   }(l,m)
 }
 fn period()->Period{Period{enter:vec![],depart:vec![],award:100,funding:500}}
 #[test]fn order_and_non_offset(){let(l,m)=fixture();let e=Engine::genesis().sync(&l,l.head(),&m).unwrap();let r=e.advance(&period(),Shares{carbon:2000,ai:500}).unwrap();assert_eq!(r.allocations.iter().map(|x|x.id.as_str()).collect::<Vec<_>>(),vec!["urgent","old"]);assert_eq!(r.allocations[0].amount,Shares{carbon:1640,ai:410});assert_eq!(r.allocations[1].amount,Shares{carbon:360,ai:90});assert_eq!(r.universal,Engine::genesis().advance(&period(),Shares::default()).unwrap().universal);}
 #[test]fn replay_and_rewrite(){let(l,mut m)=fixture();let e=Engine::genesis().sync(&l,l.head(),&m).unwrap();assert_eq!(e.sync(&l,l.head(),&m).unwrap(),e);m.get_mut("old").unwrap().urgency=1000;assert!(e.sync(&l,l.head(),&m).is_err());}
 #[test]fn grid(){let(l,m)=fixture();let root=Engine::genesis().sync(&l,l.head(),&m).unwrap();for c in [0,500,2000]{for a in [0,100,500]{for ubi in [0,500,900]{let mut e=root.clone();let mut z=Engine::genesis();for _ in 0..360{let mut p=period();p.funding=ubi;let r=e.advance(&p,Shares{carbon:c,ai:a}).unwrap();let b=z.advance(&p,Shares::default()).unwrap();assert_eq!(r.universal,b.universal);assert_eq!(r.allocations.iter().map(|x|x.amount.carbon).sum::<u64>()+r.unallocated.carbon,c);assert_eq!(r.allocations.iter().map(|x|x.amount.ai).sum::<u64>()+r.unallocated.ai,a);e=r.next;z=b.next;}}}}}
}
