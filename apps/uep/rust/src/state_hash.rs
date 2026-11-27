//! UEP-242R: canonical authoritative state and transition commitments. .dlw
use crate::{executable::{Universe,Request},population::Population,request_codec};
use sha2::{Digest,Sha256};
pub(crate) fn num(b:&mut Vec<u8>,n:u64){b.extend_from_slice(&n.to_be_bytes())}
fn string(b:&mut Vec<u8>,s:&str){num(b,s.len() as u64);b.extend_from_slice(s.as_bytes())}
pub(crate) fn population(b:&mut Vec<u8>,p:&Population){
 num(b,p.epoch);for set in [&p.active,&p.known]{num(b,set.len() as u64);for s in set{string(b,s)}}
 num(b,p.lots.len() as u64);for l in &p.lots{num(b,l.origin);string(b,&l.id);num(b,l.amount)}
 num(b,p.unattributed);match &p.cursor{None=>b.push(0),Some(s)=>{b.push(1);string(b,s)}}
}
pub fn encode(u:&Universe)->Result<Vec<u8>,&'static str>{let _profile=crate::verification_profile::span(2);let mut b=b"UEP242R\0".to_vec();u.state_bytes(&mut b)?;Ok(b)}
pub fn fingerprint(u:&Universe)->Result<[u8;32],&'static str>{let _profile=crate::verification_profile::span(3);let mut h=Sha256::new();h.update(b"OASIS-UEP-242R-state-v1");h.update(encode(u)?);Ok(h.finalize().into())}
#[derive(Clone,Debug,PartialEq,Eq)]
pub struct Commitment{pub opening:[u8;32],pub request:[u8;32],pub closing:[u8;32],pub digest:[u8;32]}
impl Commitment{
 fn new(opening:[u8;32],request:[u8;32],closing:[u8;32])->Self{let mut h=Sha256::new();h.update(b"OASIS-UEP-242R-transition-v1");h.update(opening);h.update(request);h.update(closing);Self{opening,request,closing,digest:h.finalize().into()}}
 pub fn verify(&self)->bool{*self==Self::new(self.opening,self.request,self.closing)}
}
pub fn advance(u:&Universe,r:&Request)->Result<(Universe,Commitment),&'static str>{
 let opening=fingerprint(u)?;let request=request_codec::fingerprint(r)?;
 let next=u.advance(r)?;let closing=fingerprint(&next)?;
 Ok((next,Commitment::new(opening,request,closing)))
}
#[cfg(test)]
mod tests{
 use super::*;use crate::{evidence::Ledger,equilibrium::Step,population::Period,bridge::Shares,dividend::Revenue,capacity::Input};
 fn root()->Universe{Universe::new(Ledger::default(),[0;32]).unwrap()}
 fn req()->Request{let s=Step{period:Period{enter:vec![],depart:vec![],award:100,funding:600},restitution:Shares::default(),revenue:Revenue{public_equity:0,licensing:0,automation_royalties:0,infrastructure_return:0},dividend_cap:0,resources:Input{inflow:[100;4],essential:[20;4],decay_bps:0,work_ceiling:17}};Request{present:s.clone(),requested:0,complete:0,accept:0,future:vec![s]}}
 #[test]fn deterministic(){let u=root();assert_eq!(advance(&u,&req()).unwrap(),advance(&u,&req()).unwrap());}
 #[test]fn hidden_reserve(){let u=root();let a=req();let mut b=a.clone();b.present.revenue.public_equity=1;let (x,c)=advance(&u,&a).unwrap();let (y,d)=advance(&u,&b).unwrap();assert_eq!(x.observations(),y.observations());assert_ne!(c.closing,d.closing);}
 #[test]fn future_binding(){let u=root();let a=req();let mut b=a.clone();b.future[0].resources.inflow[0]=101;let (x,c)=advance(&u,&a).unwrap();let(y,d)=advance(&u,&b).unwrap();assert_eq!(x,y);assert_ne!(c.digest,d.digest);assert_eq!(c.closing,d.closing);}
 #[test]fn chain(){let mut u=root();let mut previous=fingerprint(&u).unwrap();for _ in 0..12{let(n,c)=advance(&u,&req()).unwrap();assert_eq!(c.opening,previous);assert!(c.verify());previous=c.closing;u=n;}}
 #[test]fn tamper(){let(_,mut c)=advance(&root(),&req()).unwrap();c.closing[0]^=1;assert!(!c.verify());}
}
