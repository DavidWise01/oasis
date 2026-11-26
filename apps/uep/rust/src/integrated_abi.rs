//! UEP-245R: bounded byte-oriented native/WASM session ABI, no raw pointers. .dlw
use crate::{checkpoint,journal,replay_archive::{self,Archive},request_codec};
use std::cell::RefCell;
const LIMIT:usize=1024*1024;
const ARCHIVE_LIMIT:usize=LIMIT-checkpoint::SIZE;
#[derive(Default)]
struct Session{archive:Option<Archive>,input:Vec<u8>,output:Vec<u8>,poisoned:bool}
impl Session{
 fn run(&mut self,op:u32)->Result<(),&'static str>{
  self.output.clear();
  if self.poisoned{return Err("invalid input transfer")}
  match op{
   // Initialize from externally supplied ledger count + head + canonical ledger.
   1=>{if self.archive.is_some(){return Err("already initialized")}if self.input.len()<40{return Err("ledger header")}
    let count=u64::from_be_bytes(self.input[..8].try_into().map_err(|_|"count")?);
    let head=self.input[8..40].try_into().map_err(|_|"head")?;
    let l=journal::decode(&self.input[40..],&journal::Checkpoint{count,head})?;
    let a=Archive::new(l,head)?;if a.encode()?.len()>ARCHIVE_LIMIT{return Err("session archive limit")}self.archive=Some(a);}
   // Append exactly one canonical request.
   2=>{let a=self.archive.as_ref().ok_or("uninitialized")?;let r=request_codec::decode(&self.input)?;
    let next=a.append(&r)?;let b=next.encode()?;if b.len()>ARCHIVE_LIMIT{return Err("session archive limit")}self.archive=Some(next);}
   3=>{self.output=self.archive.as_ref().ok_or("uninitialized")?.encode()?;}
   4=>{self.output=checkpoint::encode(&self.archive.as_ref().ok_or("uninitialized")?.checkpoint()?)?;}
   // Import externally supplied checkpoint + canonical archive into empty session.
   5=>{if self.archive.is_some(){return Err("already initialized")}if self.input.len()<checkpoint::SIZE{return Err("checkpoint header")}
    let c=checkpoint::decode(&self.input[..checkpoint::SIZE])?;
    let a=replay_archive::decode(&self.input[checkpoint::SIZE..],&c)?;self.archive=Some(a);}
   // Canonical state bytes; compact observation access follows in 246R.
   6=>{self.output=crate::state_hash::encode(self.archive.as_ref().ok_or("uninitialized")?.universe())?;}
   // UEP-246R: versioned observation packet, no JS economic calculation.
   7=>{if !self.input.is_empty(){return Err("unexpected input")}let u=self.archive.as_ref().ok_or("uninitialized")?.universe();let o=u.observations().last().ok_or("no observation")?;
    let stage=u.state().state().restoration();
    self.output=b"UEP246R\0".to_vec();
    for v in [o.epoch,o.due,o.funded,o.arrears,o.carbon_reserved,o.ai_reserved,o.dividend,o.work,stage.funded(),o.completed,o.accepted,o.residual_harm,o.rate,o.historical_reserved,u.population_count() as u64,u64::from(o.rejected),o.first_violation.map_or(u64::MAX,|x|x as u64)]{self.output.extend_from_slice(&v.to_be_bytes())}
    for v in o.stock.iter().chain(o.gain.iter()).chain(o.queued.iter()){self.output.extend_from_slice(&v.to_be_bytes())}
    self.output.extend_from_slice(&o.digest);}
   // Synthetic assessment fixture; explicit initialization only, not a real claim.
   8=>{if self.archive.is_some()||!self.input.is_empty(){return Err("fixture initialization")}
    use crate::{evidence::{Ledger,Event},restitution::Assessment};
    let l=Ledger::default().append(Event::Estimate{id:"fixture-e".into(),valuation:10000,assessment:Assessment{target:"synthetic aggregate resource harm".into(),evidence_refs:vec!["synthetic reference".into()],human_observation_ref:"fixture-h".into(),ai_observation_ref:"fixture-a".into(),positive:[999;22],negative:[0;22]}})?.append(Event::AcceptModel{id:"fixture-a".into(),estimate_id:"fixture-e".into(),decision_ref:"synthetic model only".into()})?;
    let head=l.head();self.archive=Some(Archive::new(l,head)?);}
   _=>return Err("operation")
  }
  if self.output.len()>LIMIT{self.output.clear();return Err("output limit")}Ok(())
 }
}
thread_local!{static SESSION:RefCell<Session>=RefCell::new(Session::default());}
#[no_mangle]pub extern "C" fn uep_integrated_version()->u32{245}
#[no_mangle]pub extern "C" fn uep_observation_version()->u32{246}
#[no_mangle]pub extern "C" fn uep_integrated_reset(){SESSION.with(|s|*s.borrow_mut()=Session::default())}
#[no_mangle]pub extern "C" fn uep_integrated_input_clear(){SESSION.with(|s|{let mut s=s.borrow_mut();s.input.clear();s.output.clear();s.poisoned=false;})}
#[no_mangle]pub extern "C" fn uep_integrated_input_byte(v:u32)->u32{SESSION.with(|s|{let mut s=s.borrow_mut();s.output.clear();if v>255||s.input.len()>=LIMIT{s.poisoned=true;return 1}s.input.push(v as u8);0})}
#[no_mangle]pub extern "C" fn uep_integrated_run(op:u32)->u32{SESSION.with(|s|{let mut s=s.borrow_mut();let r=s.run(op);s.input.clear();s.poisoned=false;if r.is_ok(){0}else{1}})}
#[no_mangle]pub extern "C" fn uep_integrated_output_len()->u32{SESSION.with(|s|s.borrow().output.len() as u32)}
#[no_mangle]pub extern "C" fn uep_integrated_output_byte(i:u32)->u32{SESSION.with(|s|s.borrow().output.get(i as usize).map_or(256,|&v|v as u32))}
#[cfg(test)]
mod tests{
 use super::*;use crate::{evidence::Ledger,executable::Request,equilibrium::Step,population::Period,bridge::Shares,dividend::Revenue,capacity::Input};
 fn init()->Vec<u8>{let mut b=vec![0;40];b.extend(journal::encode(&Ledger::default()).unwrap());b}
 fn req()->Vec<u8>{let s=Step{period:Period{enter:vec![],depart:vec![],award:100,funding:600},restitution:Shares::default(),revenue:Revenue{public_equity:0,licensing:0,automation_royalties:0,infrastructure_return:0},dividend_cap:0,resources:Input{inflow:[100;4],essential:[20;4],decay_bps:0,work_ceiling:17}};request_codec::encode(&Request{present:s.clone(),requested:0,complete:0,accept:0,future:vec![s]}).unwrap()}
 fn op(n:u32,b:&[u8])->u32{uep_integrated_input_clear();for &v in b{assert_eq!(uep_integrated_input_byte(v as u32),0)}uep_integrated_run(n)}
 fn out()->Vec<u8>{(0..uep_integrated_output_len()).map(|i|uep_integrated_output_byte(i) as u8).collect()}
 #[test]fn native_parity(){uep_integrated_reset();assert_eq!(op(1,&init()),0);assert_eq!(op(2,&req()),0);assert_eq!(op(3,&[]),0);let a=Archive::new(Ledger::default(),[0;32]).unwrap().append(&request_codec::decode(&req()).unwrap()).unwrap();assert_eq!(out(),a.encode().unwrap());}
 #[test]fn recover(){uep_integrated_reset();assert_eq!(op(1,&init()),0);assert_eq!(op(2,&req()),0);assert_eq!(op(4,&[]),0);let mut b=out();assert_eq!(op(3,&[]),0);let a=out();b.extend(&a);uep_integrated_reset();assert_eq!(op(5,&b),0);assert_eq!(op(3,&[]),0);assert_eq!(out(),a);}
 #[test]fn fail_closed(){uep_integrated_reset();assert_eq!(op(1,&init()),0);assert_eq!(op(3,&[]),0);let a=out();assert_eq!(op(2,b"bad"),1);assert_eq!(uep_integrated_output_len(),0);assert_eq!(op(3,&[]),0);assert_eq!(out(),a);}
 #[test]fn no_reinitialize(){uep_integrated_reset();assert_eq!(op(1,&init()),0);assert_eq!(op(1,&init()),1);assert_eq!(op(5,&[]),1);}
 #[test]fn bounds(){uep_integrated_reset();assert_eq!(uep_integrated_input_byte(256),1);assert_eq!(uep_integrated_output_byte(0),256);assert_eq!(op(99,&[]),1);for _ in 0..LIMIT{assert_eq!(uep_integrated_input_byte(0),0)}assert_eq!(uep_integrated_input_byte(0),1);}
}

#[cfg(test)]mod observation_tests{
 use super::*;use crate::{executable::Request,equilibrium::Step,population::Period,bridge::Shares,dividend::Revenue,capacity::Input};
 fn req()->Vec<u8>{let s=Step{period:Period{enter:vec![],depart:vec![],award:100,funding:600},restitution:Shares{carbon:100,ai:25},revenue:Revenue{public_equity:600,licensing:0,automation_royalties:0,infrastructure_return:0},dividend_cap:100,resources:Input{inflow:[100;4],essential:[20;4],decay_bps:0,work_ceiling:17}};request_codec::encode(&Request{present:s.clone(),requested:10,complete:0,accept:0,future:vec![s]}).unwrap()}
 #[test]fn observation_layout(){let mut s=Session::default();s.run(8).unwrap();assert!(s.run(7).is_err());s.input=req();s.run(2).unwrap();s.input.clear();s.run(7).unwrap();assert_eq!(s.output.len(),272);assert_eq!(&s.output[..8],b"UEP246R\0");let a=s.archive.as_ref().unwrap();let o=a.universe().observations().last().unwrap();assert_eq!(&s.output[240..],&o.digest);assert_eq!(u64::from_be_bytes(s.output[72..80].try_into().unwrap()),5);}
 #[test]fn fixture_guard(){let mut s=Session::default();s.input.push(0);assert!(s.run(8).is_err());s.input.clear();s.run(8).unwrap();assert!(s.run(8).is_err());}
 #[test]fn observation_read_only(){let mut s=Session::default();s.run(8).unwrap();s.input=req();s.run(2).unwrap();s.input.clear();let a=s.archive.clone();s.run(7).unwrap();let b=s.output.clone();s.run(7).unwrap();assert_eq!(s.output,b);assert_eq!(s.archive,a);}
}
