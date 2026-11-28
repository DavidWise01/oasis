//! UEP-287R: qualified unified delta execution; privately paired authority and components. .dlw
use crate::{authenticated_state::{State,Root},incremental_balance::Balances,incremental_membership::Registry,incremental_chronology::Chronology,executable::{Universe,Request},state_hash,arrears::Audit};
use sha2::{Sha256,Digest};
type Hash=[u8;32];
#[derive(Clone,Debug,PartialEq,Eq)]
pub struct Qualified{universe:Universe,balances:Balances,membership:Registry,chronology:Chronology,root:Root}
#[derive(Clone,Debug,PartialEq,Eq)]
pub struct Work{pub balance_paths:usize,pub historical_paths:usize,pub active_paths:usize,pub chronology_paths:usize}
fn root(authority:Hash,b:&Balances,m:&Registry,q:&Chronology)->Root{
 let mut r=Root{authority,balances:b.commitment(),membership:m.commitment(),chronology:q.commitment(),digest:[0;32]};let mut h=Sha256::new();h.update(b"OASIS-UEP-275R-unified-v1");for v in [&r.authority,&r.balances,&r.membership,&r.chronology]{h.update(v)}r.digest=h.finalize().into();r
}
impl Qualified{
 /// Import only a fully checked legacy opening; preserve chronological retirement history.
 pub fn import(s:&State,u:&Universe,expected:&Root)->Result<Self,&'static str>{
 s.verify_root(u,expected)?;let p=u.population_ledger();
 let balances=Balances::build(p,expected.balances)?;let membership=Registry::build(p,expected.membership)?;let chronology=Chronology::from_qualified(s.chronology(),p,expected.chronology)?;
 let n=Self{universe:u.clone(),balances,membership,chronology,root:expected.clone()};n.verify_full(expected)?;Ok(n)
 }
 pub fn universe(&self)->&Universe{&self.universe}
 pub fn root(&self)->&Root{&self.root}
 pub fn balances(&self)->&Balances{&self.balances}
 pub fn membership(&self)->&Registry{&self.membership}
 pub fn chronology(&self)->&Chronology{&self.chronology}
 fn verify_anchor(&self,expected:&Root)->Result<(),&'static str>{
 if !expected.verify()||self.root!=*expected||root(state_hash::fingerprint(&self.universe)?,&self.balances,&self.membership,&self.chronology)!=*expected{return Err("qualified opening mismatch")}Ok(())
 }
 pub fn verify_full(&self,expected:&Root)->Result<(),&'static str>{
 self.verify_anchor(expected)?;let p=self.universe.population_ledger();self.balances.verify_full(p)?;self.membership.verify_full(p)?;self.chronology.verify_full(p)?;if self.balances.total()?!=p.outstanding()?{return Err("total mismatch")}Ok(())
 }
 pub fn advance(&self,r:&Request,expected:&Root)->Result<(Self,Audit,Work),&'static str>{
 self.verify_anchor(expected)?;let(v,a)=self.universe.advance_audited(r)?;let p=self.universe.population_ledger();let q=v.population_ledger();
 if q!=&a.settlement.closing{return Err("settlement parity")}
 let o=v.observations().last().ok_or("observation")?;if(o.due,o.funded,o.arrears,o.historical_reserved)!=(a.settlement.current_due,a.settlement.current_funded,q.outstanding()?,a.total_reserved){return Err("observation parity")}
 let(b,bw)=self.balances.apply_audit(p,&r.present.period,&a,expected.balances)?;
 let(m,mw)=self.membership.advance(p,q,&r.present.period,expected.membership)?;
 let(c,cw)=self.chronology.apply_audit(p,&r.present.period,&a,expected.chronology)?;
 if b.total()?!=q.outstanding()?{return Err("closing total")}
 let root=root(state_hash::fingerprint(&v)?,&b,&m,&c);
 let n=Self{universe:v,balances:b,membership:m,chronology:c,root};
 Ok((n,a,Work{balance_paths:bw.changed_paths,historical_paths:mw.historical_paths,active_paths:mw.active_paths,chronology_paths:cw}))
 }
 pub fn compact(&self,expected:&Root)->Result<Self,&'static str>{self.verify_anchor(expected)?;let mut n=self.clone();n.universe=self.universe.compact(expected.authority)?;n.verify_anchor(expected)?;Ok(n)}
}
#[cfg(test)]mod tests{
 use super::*;use crate::{evidence::Ledger,equilibrium::Step,population::Period,bridge::Shares,dividend::Revenue,capacity::Input,verification_profile};
 fn opening()->(State,Universe,Qualified){let u=Universe::new(Ledger::default(),[0;32]).unwrap();let s=State::build(&u,state_hash::fingerprint(&u).unwrap()).unwrap();let n=Qualified::import(&s,&u,&s.root()).unwrap();(s,u,n)}
 fn req(f:u64)->Request{let s=Step{period:Period{enter:vec![],depart:vec![],award:100,funding:f},restitution:Shares::default(),revenue:Revenue{public_equity:0,licensing:0,automation_royalties:0,infrastructure_return:0},dividend_cap:0,resources:Input{inflow:[100;4],essential:[20;4],decay_bps:0,work_ceiling:17}};Request{present:s.clone(),requested:0,complete:0,accept:0,future:vec![s]}}
 fn pair(s:&State,u:&Universe,n:&Qualified,r:&Request)->(State,Universe,Qualified){
 let(a,c)=verification_profile::measure(||n.advance(r,n.root())).unwrap();let(z,a,w)= {let(z,a,w)=a.unwrap();(z,a,w)};
 assert_eq!((c.calls[1],c.calls[10],c.calls[11],c.calls[12]),(1,0,0,0));
 let(v,q,b,k)=s.advance_delta(u,r,&s.root()).unwrap();assert_eq!(a,b);assert_eq!(z.universe(),&q);assert_eq!(z.root(),&v.root());assert_eq!((w.balance_paths,w.chronology_paths),(k.balance_paths,k.chronology_paths));z.verify_full(z.root()).unwrap();(v,q,z)
 }
 #[test]fn mixed(){let(mut s,mut u,mut n)=opening();let mut current="A_1".to_string();for t in 0..60{let mut r=req([0,500,600,750,1200][t%5]);if t%3==0{let id=format!("G_{t}");r.present.period.enter=vec![id.clone()];r.present.period.depart=vec![std::mem::replace(&mut current,id)];}(s,u,n)=pair(&s,&u,&n,&r);}}
 #[test]fn scarcity(){let(mut s,mut u,mut n)=opening();for _ in 0..30{(s,u,n)=pair(&s,&u,&n,&req(500));}assert_eq!(n.balances().total().unwrap(),3400);let(_,_,z)=pair(&s,&u,&n,&req(3600));assert_eq!(z.balances().total().unwrap(),400);assert_eq!(z.chronology().head(),180);}
 #[test]fn substituted(){let(s,u,n)=opening();let (_,v,_)=pair(&s,&u,&n,&req(500));assert!(Qualified::import(&s,&v,n.root()).is_err());let mut r=n.root().clone();r.membership[0]^=1;assert!(n.advance(&req(600),&r).is_err());let mut forged=n.clone();forged.universe=v;assert!(forged.advance(&req(600),n.root()).is_err());}
 #[test]fn compaction_and_import(){let(s,u,n)=opening();let(s,u,n)=pair(&s,&u,&n,&req(0));let(s,u,n)=pair(&s,&u,&n,&req(1200));let z=n.compact(n.root()).unwrap();assert!(z.universe().observations().is_empty());let v=s.compact(&u,&s.root()).unwrap();assert_eq!(Qualified::import(&s,&v,&s.root()).unwrap(),z);assert_eq!(z.chronology().head(),6);let(_,_,w)=pair(&s,&v,&z,&req(500));assert_eq!(w.chronology().tail(),12);}
 #[test]fn rejected_unchanged(){let(_,_,n)=opening();let before=n.clone();let mut r=req(600);r.present.period.enter=vec!["A_0".into()];assert!(n.advance(&r,n.root()).is_err());assert_eq!(n,before);assert!(n.universe().observations().is_empty());}
}
