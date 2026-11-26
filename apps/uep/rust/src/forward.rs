//! UEP-238R: finite supplied-horizon protection, not a guarantee under unknown futures. .dlw
use crate::{adaptive::{Recovery,Frame as Adaptive},equilibrium::Step};
#[derive(Clone,Debug,PartialEq,Eq)]
pub struct Frame{pub chosen:Adaptive,pub rejected:bool,pub compared:usize,pub first_violation:Option<usize>}
fn worse(a:&Adaptive,b:&Adaptive)->bool{
 let x=&a.regeneration.lifecycle.expenditure;let y=&b.regeneration.lifecycle.expenditure;
 x.economic.universal!=y.economic.universal ||
 (0..4).any(|k|x.physical.delivered[k]<y.physical.delivered[k]||
  10u64.saturating_sub(x.physical.next.stock()[k])>10u64.saturating_sub(y.physical.next.stock()[k]))
}
pub fn advance(start:&Recovery,present:&Step,requested:u64,complete:u64,accept:u64,future:&[Step])->Result<Frame,&'static str>{
 if future.is_empty()||future.len()>64{return Err("horizon")}
 let neutral=start.advance(present,0,0,0)?;
 let candidate=start.advance(present,requested,complete,accept)?;
 let mut a=candidate.next.clone();let mut b=neutral.next.clone();
 let mut violation=if worse(&candidate,&neutral){Some(0)}else{None};
 // Evaluate every supplied future period even after a violation, so invalid input cannot hide.
 for (i,s) in future.iter().enumerate(){
  let x=a.advance(s,0,0,0)?;let y=b.advance(s,0,0,0)?;
  if violation.is_none()&&worse(&x,&y){violation=Some(i+1);}
  // Terminal resource stocks must not be below neutral stocks.
  if i+1==future.len()&&violation.is_none(){
   let xs=x.regeneration.lifecycle.expenditure.physical.next.stock();
   let ys=y.regeneration.lifecycle.expenditure.physical.next.stock();
   if (0..4).any(|k|xs[k]<ys[k]){violation=Some(i+1);}
  }
  a=x.next;b=y.next;
 }
 let rejected=violation.is_some();
 Ok(Frame{chosen:if rejected{neutral}else{candidate},rejected,compared:future.len()+1,first_violation:violation})
}
#[cfg(test)]
mod tests{
 use super::*;use crate::{evidence::{Ledger,Event},restitution::Assessment,capacity::Input,dividend::Revenue,population::Period,bridge::Shares};
 fn root()->Recovery{let l=Ledger::default().append(Event::Estimate{id:"e".into(),valuation:10000,assessment:Assessment{target:"synthetic".into(),evidence_refs:vec!["source".into()],human_observation_ref:"h".into(),ai_observation_ref:"a".into(),positive:[999;22],negative:[0;22]}}).unwrap().append(Event::AcceptModel{id:"a".into(),estimate_id:"e".into(),decision_ref:"model".into()}).unwrap();Recovery::new(&l,l.head()).unwrap()}
 fn step()->Step{Step{period:Period{enter:vec![],depart:vec![],award:100,funding:600},restitution:Shares{carbon:100,ai:0},revenue:Revenue{public_equity:0,licensing:0,automation_royalties:0,infrastructure_return:0},dividend_cap:0,resources:Input{inflow:[40;4],essential:[20;4],decay_bps:0,work_ceiling:17}}}
 #[test]fn equal_terminal(){let p=step();let mut q=p.clone();q.resources.inflow=[100;4];let f=advance(&root(),&p,10,0,0,&[q]).unwrap();assert!(!f.rejected);assert_eq!(f.chosen.regeneration.lifecycle.expenditure.units,5);}
 #[test]fn future_shortage(){let p=step();let mut q=p.clone();q.resources.inflow=[0;4];q.resources.essential=[75;4];let f=advance(&root(),&p,10,0,0,&[q]).unwrap();assert!(f.rejected);assert_eq!(f.first_violation,Some(1));assert_eq!(f.chosen,present_neutral(&p));}
 fn present_neutral(p:&Step)->Adaptive{root().advance(p,0,0,0).unwrap()}
 #[test]fn terminal_debt(){let p=step();let mut q=p.clone();q.resources.inflow=[0;4];q.resources.essential=[0;4];let f=advance(&root(),&p,10,0,0,&[q]).unwrap();assert!(f.rejected);}
 #[test]fn horizon_validation(){let p=step();assert!(advance(&root(),&p,0,0,0,&[]).is_err());assert!(advance(&root(),&p,0,0,0,&vec![p.clone();65]).is_err());let mut q=p.clone();q.resources.decay_bps=10001;assert!(advance(&root(),&p,10,0,0,&[p.clone(),q]).is_err());}
 #[test]fn replay(){let p=step();let s=root();let h=vec![p.clone();4];assert_eq!(advance(&s,&p,10,0,0,&h).unwrap(),advance(&s,&p,10,0,0,&h).unwrap());}
}
