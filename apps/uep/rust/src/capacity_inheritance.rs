//! UEP-255R: restorative capacity continuity across compacted segments. .dlw
use crate::{executable::Request,linked_segment::{Anchor,Segment},identity_continuity,cross_arrears::Audit,state_hash,capacity::YIELD};
#[derive(Clone,Debug,PartialEq,Eq)]
pub struct Lifecycle{pub funded:u64,pub completed:u64,pub accepted:u64,pub pending:[u64;4],pub rate:u64}
fn lifecycle(s:&Segment)->Lifecycle{let r=s.universe().state();let t=r.state().restoration();Lifecycle{funded:t.funded(),completed:t.completed(),accepted:t.accepted(),pending:t.pending_yield(),rate:r.rate()}}
pub fn boundary(s:&Segment,c:&Anchor)->Result<Segment,&'static str>{let n=identity_continuity::boundary(s,c)?;if lifecycle(s)!=lifecycle(&n)||state_hash::encode(s.universe())?!=state_hash::encode(n.universe())?{return Err("capacity inheritance")}Ok(n)}
pub fn append(s:&Segment,r:&Request)->Result<(Segment,Audit,Lifecycle),&'static str>{
 let a=lifecycle(s);let(n,audit,_)=identity_continuity::append(s,r)?;let b=lifecycle(&n);let o=n.universe().observations().last().ok_or("observation")?;
 let funded=b.funded.checked_sub(a.funded).ok_or("funded rollback")?;
 let completed=b.completed.checked_sub(a.completed).ok_or("completed rollback")?;
 let accepted=b.accepted.checked_sub(a.accepted).ok_or("accepted rollback")?;
 if a.accepted>a.completed||a.completed>a.funded||b.accepted>b.completed||b.completed>b.funded||b.funded>17||funded!=o.work||completed>a.funded-a.completed||accepted>a.completed-a.accepted||b.accepted!=o.accepted||b.completed!=o.completed||b.accepted+o.residual_harm!=17||b.rate!=o.rate{return Err("lifecycle conservation")}
 for k in 0..4{if b.pending[k]!=accepted.checked_mul(YIELD[k]).ok_or("yield overflow")?||b.pending[k]!=o.queued[k]{return Err("duplicate yield")}}
 if audit.current_funded<audit.due&&(funded!=0||completed!=0||accepted!=0){return Err("current priority")}
 Ok((n,audit,b))
}
#[cfg(test)]mod tests{
 use super::*;use crate::{evidence::{Ledger,Event},restitution::Assessment,replay_archive::Archive,equilibrium::Step,population::Period,bridge::Shares,dividend::Revenue,capacity::Input};
 fn req(f:u64,w:u64,c:u64,a:u64)->Request{let s=Step{period:Period{enter:vec![],depart:vec![],award:100,funding:f},restitution:Shares{carbon:100,ai:25},revenue:Revenue{public_equity:600,licensing:0,automation_royalties:0,infrastructure_return:0},dividend_cap:100,resources:Input{inflow:[100;4],essential:[20;4],decay_bps:0,work_ceiling:17}};Request{present:s.clone(),requested:w,complete:c,accept:a,future:vec![s]}}
 fn root()->Segment{let l=Ledger::default().append(Event::Estimate{id:"e".into(),valuation:10000,assessment:Assessment{target:"synthetic".into(),evidence_refs:vec!["source".into()],human_observation_ref:"h".into(),ai_observation_ref:"a".into(),positive:[999;22],negative:[0;22]}}).unwrap().append(Event::AcceptModel{id:"a".into(),estimate_id:"e".into(),decision_ref:"model".into()}).unwrap();let mut a=Archive::new(l.clone(),l.head()).unwrap();for _ in 0..360{a=a.append(&req(600,0,0,0)).unwrap()}Segment::from_root(&a,&a.checkpoint().unwrap()).unwrap()}
 #[test]fn queued_rollover(){let mut s=root();for _ in 0..357{s=s.append(&req(600,0,0,0)).unwrap()}s=append(&s,&req(600,17,0,0)).unwrap().0;s=append(&s,&req(600,0,17,0)).unwrap().0;s=append(&s,&req(600,0,0,17)).unwrap().0;let c=s.anchor().unwrap();let n=boundary(&s,&c).unwrap();assert_eq!(lifecycle(&n).pending,[34,17,34,17]);let r=req(600,0,0,0);let (n,_,b)=append(&n,&r).unwrap();assert_eq!(b.pending,[0;4]);assert_eq!(b.accepted,17);assert_eq!(n.universe().observations().last().unwrap().gain,[30,17,30,17]);assert_eq!(state_hash::encode(n.universe()).unwrap(),state_hash::encode(&s.universe().advance(&r).unwrap()).unwrap());}
 #[test]fn no_duplicate_acceptance(){let mut s=root();s=append(&s,&req(600,17,0,0)).unwrap().0;s=append(&s,&req(600,0,17,0)).unwrap().0;s=append(&s,&req(600,0,0,17)).unwrap().0;assert!(append(&s,&req(600,0,0,1)).is_err());let(_,_,b)=append(&s,&req(600,17,0,0)).unwrap();assert_eq!(b.funded,17);}
 #[test]fn scarcity_defers(){let s=append(&root(),&req(600,17,0,0)).unwrap().0;let(_,_,b)=append(&s,&req(500,0,17,0)).unwrap();assert_eq!((b.funded,b.completed,b.accepted,b.rate),(17,0,0,0));}
 #[test]fn partial_boundary(){let s=root();assert!(boundary(&s,&s.anchor().unwrap()).is_err());}
 #[test]fn decay_once(){let mut s=root();s=append(&s,&req(600,17,0,0)).unwrap().0;s=append(&s,&req(600,0,17,0)).unwrap().0;s=append(&s,&req(600,0,0,17)).unwrap().0;let mut r=req(600,0,0,0);r.present.resources.decay_bps=1000;let(n,_,b)=append(&s,&r).unwrap();assert_eq!(b.pending,[0;4]);assert_eq!(n.universe().observations().last().unwrap().gain,[27,15,27,15]);}
}
