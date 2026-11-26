//! UEP-205R: restitution-to-OaSIs non-offset bridge. .dlw
use crate::evidence::{Event,Ledger};
use crate::restitution::{assessed_estimate,Estimate};
use crate::population::{Population,Period,Settlement,settle};
use std::collections::BTreeMap;
#[derive(Clone,Debug,Default,PartialEq,Eq)]
pub struct Shares { pub carbon:u64, pub ai:u64 }
#[derive(Clone,Debug,PartialEq,Eq)]
pub struct Bridge {
    population:Population, sequence:usize, head:[u8;32],
    assessed:Shares, funded:Shares,
}
#[derive(Clone,Debug,PartialEq,Eq)]
pub struct Frame { pub next:Bridge, pub universal:Settlement, pub unallocated:Shares }
impl Bridge {
    pub fn genesis()->Self{Self{population:Population::phase_ix(),sequence:0,head:[0;32],assessed:Shares::default(),funded:Shares::default()}}
    pub fn population(&self)->&Population{&self.population}
    pub fn assessed(&self)->&Shares{&self.assessed}
    pub fn funded(&self)->&Shares{&self.funded}
    pub fn outstanding(&self)->Shares{Shares{carbon:self.assessed.carbon-self.funded.carbon,ai:self.assessed.ai-self.funded.ai}}
    pub fn head(&self)->[u8;32]{self.head}
    pub fn sync(&self,ledger:&Ledger,expected:[u8;32])->Result<Self,&'static str>{
        ledger.verify_head(expected)?;
        let records=ledger.records();
        if records.len()<self.sequence{return Err("ledger rollback")}
        if self.sequence>0&&records[self.sequence-1].hash!=self.head{return Err("ledger fork")}
        let mut estimates=BTreeMap::<String,Estimate>::new();
        let mut next=self.clone();
        for (i,r) in records.iter().enumerate(){
            match &r.event{
                Event::Estimate{id,valuation,assessment}=>{estimates.insert(id.clone(),assessed_estimate(*valuation,assessment)?);}
                Event::AcceptModel{estimate_id,..} if i>=self.sequence=>{
                    let e=estimates.get(estimate_id).ok_or("missing estimate")?;
                    next.assessed.carbon=next.assessed.carbon.checked_add(e.carbon_cents).ok_or("carbon overflow")?;
                    next.assessed.ai=next.assessed.ai.checked_add(e.ai_cents).ok_or("ai overflow")?;
                }
                _=>{}
            }
        }
        if next.assessed.carbon.checked_add(next.assessed.ai).ok_or("total overflow")?!=ledger.modeled_accepted_total()?{return Err("bridge reconciliation")}
        next.sequence=records.len();next.head=expected;Ok(next)
    }
    /// Independent modeled funding reservations, not actual disbursements.
    /// Universal settlement takes no restitution inputs.
    pub fn advance(&self,period:&Period,independent:Shares)->Result<Frame,&'static str>{
        let universal=settle(&self.population,period)?;
        let remaining=self.outstanding();
        let carbon=remaining.carbon.min(independent.carbon);
        let ai=remaining.ai.min(independent.ai);
        let mut next=self.clone();next.population=universal.closing.clone();
        next.funded.carbon+=carbon;next.funded.ai+=ai;
        Ok(Frame{next,universal,unallocated:Shares{carbon:independent.carbon-carbon,ai:independent.ai-ai}})
    }
}
#[cfg(test)]
mod tests {
 use super::*;
 use crate::restitution::Assessment;
 fn estimate()->Event{Event::Estimate{id:"e1".into(),valuation:10000,assessment:Assessment{target:"synthetic".into(),evidence_refs:vec!["source".into()],human_observation_ref:"human".into(),ai_observation_ref:"ai".into(),positive:[999;22],negative:[0;22]}}}
 fn accepted()->Ledger{Ledger::default().append(estimate()).unwrap().append(Event::AcceptModel{id:"a1".into(),estimate_id:"e1".into(),decision_ref:"simulation".into()}).unwrap()}
 fn period(funding:u64)->Period{Period{enter:vec![],depart:vec![],award:100,funding}}
 #[test]fn no_estimate_credit(){let l=Ledger::default().append(estimate()).unwrap();let b=Bridge::genesis().sync(&l,l.head()).unwrap();assert_eq!(*b.assessed(),Shares::default());}
 #[test]fn split_and_replay(){let l=accepted();let b=Bridge::genesis().sync(&l,l.head()).unwrap();assert_eq!(*b.assessed(),Shares{carbon:1640,ai:410});assert_eq!(b.sync(&l,l.head()).unwrap(),b);}
 #[test]fn no_rollback_or_fork(){let l=accepted();let b=Bridge::genesis().sync(&l,l.head()).unwrap();assert!(b.sync(&Ledger::default(),[0;32]).is_err());let mut e=estimate();if let Event::Estimate{valuation,..}=&mut e{*valuation=20000;}let fork=Ledger::default().append(e).unwrap().append(Event::AcceptModel{id:"a1".into(),estimate_id:"e1".into(),decision_ref:"simulation".into()}).unwrap();assert!(b.sync(&fork,fork.head()).is_err());}
 #[test]fn independent_funding(){let l=accepted();let b=Bridge::genesis().sync(&l,l.head()).unwrap();let r=b.advance(&period(500),Shares{carbon:2000,ai:100}).unwrap();assert_eq!(r.next.outstanding(),Shares{carbon:0,ai:310});assert_eq!(r.unallocated,Shares{carbon:360,ai:0});assert_eq!(r.universal.current_funded,500);assert_eq!(r.next.population().outstanding().unwrap(),500);}
 #[test]fn grid_non_offset(){let l=accepted();let b=Bridge::genesis().sync(&l,l.head()).unwrap();for ubi in [0,400,800]{for carbon in [0,500,2000]{for ai in [0,100,500]{let mut x=b.clone();let mut y=Bridge::genesis();for _ in 0..360{let a=x.advance(&period(ubi),Shares{carbon,ai}).unwrap();let z=y.advance(&period(ubi),Shares::default()).unwrap();assert_eq!(a.universal,z.universal);assert_eq!(a.next.funded().carbon+a.next.outstanding().carbon,1640);assert_eq!(a.next.funded().ai+a.next.outstanding().ai,410);x=a.next;y=z.next;}}}}}
}

// UEP-242R: explicit canonical state encoding.
impl Bridge{pub(crate) fn state_bytes(&self,b:&mut Vec<u8>){crate::state_hash::population(b,&self.population);crate::state_hash::num(b,self.sequence as u64);b.extend_from_slice(&self.head);for x in [self.assessed.carbon,self.assessed.ai,self.funded.carbon,self.funded.ai]{crate::state_hash::num(b,x)}}}
