//! UEP-223R: four-resource regenerative capacity, synthetic physical model. .dlw
pub const RESOURCES:[&str;4]=["water","food","energy","materials"];
pub const COST:[u64;4]=[2,1,3,2];
pub const YIELD:[u64;4]=[2,1,2,1];
#[derive(Clone,Debug,PartialEq,Eq)]
pub struct Capacity{stock:[u64;4],gain:[u64;4],pending:[u64;4],harm:u64}
#[derive(Clone,Debug,PartialEq,Eq)]
pub struct Input{pub inflow:[u64;4],pub essential:[u64;4],pub decay_bps:u64,pub work_ceiling:u64}
#[derive(Clone,Debug,PartialEq,Eq)]
pub struct Frame{pub next:Capacity,pub delivered:[u64;4],pub unmet:[u64;4],pub spilled:[u64;4],pub work:u64,pub blocked:bool}
impl Capacity{
 pub fn genesis()->Self{Self{stock:[90,80,70,80],gain:[15,0,0,0],pending:[0;4],harm:17}}
 pub fn stock(&self)->[u64;4]{self.stock}
 pub fn gain(&self)->[u64;4]{self.gain}
 pub fn harm(&self)->u64{self.harm}
 /// Planning only: work is a candidate, not verified restoration. Harm remains unchanged.
 pub fn advance(&self,i:&Input,universal:&crate::population::Settlement)->Result<Frame,&'static str>{
  if i.decay_bps>10000||i.work_ceiling>1000000||i.inflow.iter().chain(i.essential.iter()).any(|&v|v>1000000){return Err("invalid input")}
  let mut n=self.clone();let mut delivered=[0;4];let mut unmet=[0;4];let mut spilled=[0;4];
  for k in 0..4{n.gain[k]=(n.gain[k]+n.pending[k]).min(30);n.pending[k]=0;let available=n.stock[k]+i.inflow[k]+n.gain[k];spilled[k]=available.saturating_sub(100);n.stock[k]=available.min(100);delivered[k]=i.essential[k].min(n.stock[k].saturating_sub(5));unmet[k]=i.essential[k]-delivered[k];n.stock[k]-=delivered[k];n.gain[k]-=(n.gain[k]*i.decay_bps+9999)/10000;}
  let blocked=universal.current_funded<universal.current_due||unmet.iter().any(|&v|v>0)||n.stock.iter().any(|&v|v<10);
  let work=if blocked{0}else{(0..4).fold(i.work_ceiling.min(n.harm),|w,k|w.min(n.stock[k].saturating_sub(10)/COST[k]))};
  // No expenditure or productive gain is authorized by a feasibility calculation.
  Ok(Frame{next:n,delivered,unmet,spilled,work,blocked})
 }
}
#[cfg(test)]
mod tests{
 use super::*;use crate::population::{Population,Period,settle};
 fn u(funding:u64)->crate::population::Settlement{settle(&Population::phase_ix(),&Period{enter:vec![],depart:vec![],award:100,funding}).unwrap()}
 fn input()->Input{Input{inflow:[20;4],essential:[20;4],decay_bps:1000,work_ceiling:17}}
 #[test]fn bottleneck(){let mut i=input();i.essential[2]=80;let f=Capacity::genesis().advance(&i,&u(600)).unwrap();assert_eq!(f.work,0);assert!(f.blocked==false);assert_eq!(f.next.stock()[2],10);}
 #[test]fn shortage_and_ubi(){let mut i=input();i.essential[1]=100;assert!(Capacity::genesis().advance(&i,&u(600)).unwrap().blocked);assert_eq!(Capacity::genesis().advance(&input(),&u(500)).unwrap().work,0);}
 #[test]fn no_phantom_restoration(){let f=Capacity::genesis().advance(&input(),&u(600)).unwrap();assert!(f.work>0);assert_eq!(f.next.harm(),17);assert_eq!(f.next.stock(),[80,80,70,80]);}
 #[test]fn grid(){for a in [0,20,40]{for b in [10,40,90]{for funds in [0,500,600]{let mut s=Capacity::genesis();let u=u(funds);for _ in 0..360{let f=s.advance(&Input{inflow:[a;4],essential:[b;4],decay_bps:2000,work_ceiling:17},&u).unwrap();assert!(!f.blocked||f.work==0);for k in 0..4{assert!(f.next.stock()[k]<=100);assert!(f.work==0||f.next.stock()[k]-f.work*COST[k]>=10);}assert_eq!(f.next.harm(),17);s=f.next;}}}}}
}

// UEP-234R: consume a freshly computed candidate within the same transition.
impl Capacity {
 pub(crate) fn spend_candidate(&self,i:&Input,u:&crate::population::Settlement,requested:u64,budget:u64,remaining:u64)->Result<(Frame,[u64;4],u64),&'static str>{
  let mut f=self.advance(i,u)?;
  let work=requested.min(f.work).min(budget/2).min(remaining);
  let mut spent=[0;4];
  for k in 0..4{spent[k]=work.checked_mul(COST[k]).ok_or("cost overflow")?;f.next.stock[k]=f.next.stock[k].checked_sub(spent[k]).ok_or("stock underflow")?;if work>0&&f.next.stock[k]<10{return Err("reserve breach")}}
  Ok((f,spent,work))
 }
}
