//! UEP-208R: bounded recovery and paired forecast protection. .dlw
use crate::{infrastructure::{Infrastructure,Conditions,Frame},population::Period,bridge::Shares};
#[derive(Clone,Debug,PartialEq,Eq)]
pub struct Input {pub period:Period,pub funds:Shares,pub conditions:Conditions}
#[derive(Clone,Debug,PartialEq,Eq)]
pub struct Recovery {state:Infrastructure,rate:u64,clear:u64}
#[derive(Clone,Debug,PartialEq,Eq)]
pub enum Decision {Accepted,Scarcity,Recovering,ForwardHold,InvalidCandidate}
#[derive(Clone,Debug,PartialEq,Eq)]
pub struct Outcome {pub next:Recovery,pub frame:Frame,pub decision:Decision}
fn neutral(c:&Conditions)->Conditions{let mut n=c.clone();n.maintenance=0;n.request=None;n}
fn step(s:&Infrastructure,i:&Input,c:&Conditions)->Result<Frame,&'static str>{s.advance(&i.period,i.funds.clone(),c)}
fn protects(a:&Frame,b:&Frame)->bool{a.delivered>=b.delivered&&10u64.saturating_sub(a.next.stock())<=10u64.saturating_sub(b.next.stock())&&a.accounting.universal==b.accounting.universal}
fn forward(mut a:Infrastructure,mut b:Infrastructure,future:&[Input])->Result<bool,&'static str>{
 for i in future{let c=neutral(&i.conditions);let x=step(&a,i,&c)?;let y=step(&b,i,&c)?;if !protects(&x,&y){return Ok(false)}a=x.next;b=y.next;}
 Ok(a.stock()>=b.stock())
}
impl Recovery{
 pub fn new(state:Infrastructure)->Self{Self{state,rate:50,clear:0}}
 pub fn rate(&self)->u64{self.rate}
 pub fn state(&self)->&Infrastructure{&self.state}
 pub fn advance(&self,i:&Input,future:&[Input])->Result<Outcome,&'static str>{
  if future.is_empty()||future.len()>64{return Err("forecast horizon must be 1..64")}
  let base=step(&self.state,i,&neutral(&i.conditions))?;
  let mut next=self.clone();let mut chosen=base.clone();let mut decision=Decision::Recovering;
  if base.blocked{next.rate=0;next.clear=0;decision=Decision::Scarcity;}
  else{next.clear=next.clear.saturating_add(1);if next.clear>=2{next.rate=(next.rate+25).min(100);}
   if next.rate>0{
    let mut c=i.conditions.clone();c.maintenance=c.maintenance.min(30)*next.rate/100;
    if let Some(r)=&mut c.request{if r.spend_units>1_000_000{return Err("request bound")}r.spend_units=r.spend_units*next.rate/100;}
    match step(&self.state,i,&c){
      Err(_)=>decision=Decision::InvalidCandidate,
      Ok(candidate)=>{
       // Exclude new restoration gain; maintenance effects remain modeled.
       let mut shadow=c.clone();if let Some(r)=&mut shadow.request{r.accept_units=0;}
       match step(&self.state,i,&shadow){
        Ok(x) if protects(&candidate,&base)&&protects(&x,&base)&&forward(candidate.next.clone(),base.next.clone(),future)?&&forward(x.next.clone(),base.next.clone(),future)?=>{chosen=candidate;decision=Decision::Accepted;}
        _=>decision=Decision::ForwardHold,
       }
      }
    }
   }
  }
  next.state=chosen.next.clone();Ok(Outcome{next,frame:chosen,decision})
 }
}
