//! UEP-239R: one committed recovery state, replayable ordered observations. Synthetic only. .dlw
use crate::{adaptive::Recovery,forward,evidence::Ledger,equilibrium::Step,population::Population,bridge::Shares,arrears};
use sha2::{Digest,Sha256};
#[derive(Clone,Debug,PartialEq,Eq)]
pub struct Request{pub present:Step,pub requested:u64,pub complete:u64,pub accept:u64,pub future:Vec<Step>}
#[derive(Clone,Debug,PartialEq,Eq)]
pub struct Observation{pub epoch:u64,pub due:u64,pub funded:u64,pub arrears:u64,pub carbon_reserved:u64,pub ai_reserved:u64,pub dividend:u64,pub work:u64,pub completed:u64,pub accepted:u64,pub residual_harm:u64,pub stock:[u64;4],pub gain:[u64;4],pub queued:[u64;4],pub rate:u64,pub rejected:bool,pub first_violation:Option<usize>,pub historical_reserved:u64,pub previous:[u8;32],pub digest:[u8;32]}
impl Observation{
 fn hash(&self)->[u8;32]{let mut h=Sha256::new();h.update(b"OASIS-UEP-239R-observation-v1");h.update(self.previous);
 for v in [self.epoch,self.due,self.funded,self.arrears,self.carbon_reserved,self.ai_reserved,self.dividend,self.work,self.completed,self.accepted,self.residual_harm,self.rate,self.historical_reserved,self.first_violation.map_or(u64::MAX,|v|v as u64)]{h.update(v.to_be_bytes());}
 h.update([u8::from(self.rejected)]);for v in self.stock.iter().chain(self.gain.iter()).chain(self.queued.iter()){h.update(v.to_be_bytes());}h.finalize().into()}
}
#[derive(Clone,Debug,PartialEq,Eq)]
pub struct Universe{state:Recovery,population:Population,ledger:Ledger,head:[u8;32],observations:Vec<Observation>}
impl Universe{
 pub fn new(ledger:Ledger,head:[u8;32])->Result<Self,&'static str>{ledger.verify_head(head)?;Ok(Self{state:Recovery::new(&ledger,head)?,population:Population::phase_ix(),ledger,head,observations:vec![]})}
 pub fn observations(&self)->&[Observation]{&self.observations}
 pub fn state(&self)->&Recovery{&self.state}
 pub fn advance(&self,r:&Request)->Result<Self,&'static str>{
  if self.observations.len()>=10000{return Err("observation limit")}
  let audit=arrears::advance(&self.population,&r.present.period)?;
  let f=forward::advance(&self.state,&r.present,r.requested,r.complete,r.accept,&r.future)?;
  let g=&f.chosen.regeneration;let e=&g.lifecycle.expenditure;let u=&e.economic.universal;
  if u!=&audit.settlement||e.economic.next.bridge().head()!=self.head{return Err("ancestry or universal parity")}
  let shares:&Shares=e.economic.next.bridge().funded();let stage=g.next.restoration();
  if stage.accepted()>stage.completed()||stage.completed()>stage.funded()||stage.accepted()+g.lifecycle.residual_harm!=17{return Err("stage parity")}
  let mut o=Observation{epoch:u.closing.epoch,due:u.current_due,funded:u.current_funded,arrears:u.closing.outstanding()?,carbon_reserved:shares.carbon,ai_reserved:shares.ai,dividend:e.economic.dividend_total,work:e.units,completed:stage.completed(),accepted:stage.accepted(),residual_harm:g.lifecycle.residual_harm,stock:e.physical.next.stock(),gain:e.physical.next.gain(),queued:g.queued,rate:f.chosen.next.rate(),rejected:f.rejected,first_violation:f.first_violation,historical_reserved:audit.total_reserved,previous:self.observations.last().map_or(self.head,|x|x.digest),digest:[0;32]};
  o.digest=o.hash();let mut n=self.clone();n.state=f.chosen.next;n.population=u.closing.clone();n.observations.push(o);Ok(n)
 }
 pub fn verify_observations(&self)->Result<(),&'static str>{let mut prev=self.head;for (i,o) in self.observations.iter().enumerate(){if o.previous!=prev||o.digest!=o.hash()||o.epoch!=7+i as u64{return Err("observation chain")}prev=o.digest;}Ok(())}
 pub fn replay(ledger:Ledger,head:[u8;32],requests:&[Request])->Result<Self,&'static str>{let mut n=Self::new(ledger,head)?;for r in requests{n=n.advance(r)?;}n.verify_observations()?;Ok(n)}
}
#[cfg(test)]
mod tests{
 use super::*;use crate::{evidence::Event,restitution::Assessment,capacity::Input,dividend::Revenue,population::Period};
 fn ledger()->Ledger{Ledger::default().append(Event::Estimate{id:"e".into(),valuation:10000,assessment:Assessment{target:"synthetic".into(),evidence_refs:vec!["source".into()],human_observation_ref:"h".into(),ai_observation_ref:"a".into(),positive:[999;22],negative:[0;22]}}).unwrap().append(Event::AcceptModel{id:"a".into(),estimate_id:"e".into(),decision_ref:"model".into()}).unwrap()}
 fn step()->Step{Step{period:Period{enter:vec![],depart:vec![],award:100,funding:600},restitution:Shares{carbon:100,ai:25},revenue:Revenue{public_equity:600,licensing:0,automation_royalties:0,infrastructure_return:0},dividend_cap:100,resources:Input{inflow:[100;4],essential:[20;4],decay_bps:0,work_ceiling:17}}}
 fn req(s:&Universe)->Request{let r=s.state().state().restoration();Request{present:step(),requested:17,complete:r.funded()-r.completed(),accept:r.completed()-r.accepted(),future:vec![step()]}}
 fn root()->Universe{let l=ledger();Universe::new(l.clone(),l.head()).unwrap()}
 #[test]fn integrated(){let mut s=root();for _ in 0..12{s=s.advance(&req(&s)).unwrap();}let o=s.observations().last().unwrap();assert_eq!((o.accepted,o.residual_harm),(17,0));assert_eq!(o.funded,600);s.verify_observations().unwrap();}
 #[test]fn replay(){let mut s=root();let mut rs=vec![];for _ in 0..12{let r=req(&s);s=s.advance(&r).unwrap();rs.push(r);}let l=ledger();assert_eq!(s,Universe::replay(l.clone(),l.head(),&rs).unwrap());}
 #[test]fn tamper(){let mut s=root();s=s.advance(&req(&s)).unwrap();s.observations[0].stock[0]+=1;assert!(s.verify_observations().is_err());}
 #[test]fn scarcity(){let mut s=root();let mut r=req(&s);r.present.period.funding=500;s=s.advance(&r).unwrap();let o=&s.observations()[0];assert_eq!((o.work,o.funded,o.arrears),(0,500,500));}
 #[test]fn wrong_head(){assert!(Universe::new(ledger(),[0;32]).is_err());}
}
