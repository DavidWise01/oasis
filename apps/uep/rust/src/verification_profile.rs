//! UEP-271R: opt-in thread-local diagnostic counters; no settlement authority. .dlw
use std::{cell::RefCell,time::Instant};
pub const N:usize=10;
pub const NAMES:[&str;N]=["settle","arrears","state_encode","state_fingerprint","projection_verify","component_encode","observation_verify","universe_clone","projection_component_clone","tape_clone"];
#[derive(Clone,Debug,Default,PartialEq,Eq)]
pub struct Counts{pub calls:[u64;N],pub inclusive_ns:[u128;N]}
thread_local!{static ACTIVE:RefCell<Option<Counts>>=const{RefCell::new(None)};}
pub struct Span{slot:usize,start:Option<Instant>}
pub fn span(slot:usize)->Span{let enabled=ACTIVE.with(|a|{let mut a=a.borrow_mut();if let Some(c)=a.as_mut(){c.calls[slot]+=1;true}else{false}});Span{slot,start:if enabled{Some(Instant::now())}else{None}}}
impl Drop for Span{fn drop(&mut self){if let Some(t)=self.start{ACTIVE.with(|a|{if let Some(c)=a.borrow_mut().as_mut(){c.inclusive_ns[self.slot]+=t.elapsed().as_nanos();}})}}}
struct Reset;
impl Drop for Reset{fn drop(&mut self){ACTIVE.with(|a|{a.borrow_mut().take();});}}
pub fn measure<T>(f:impl FnOnce()->T)->Result<(T,Counts),&'static str>{ACTIVE.with(|a|{let mut a=a.borrow_mut();if a.is_some(){return Err("nested measurement")}*a=Some(Counts::default());Ok(())})?;let _reset=Reset;let v=f();let c=ACTIVE.with(|a|a.borrow_mut().take().unwrap());Ok((v,c))}
#[cfg(test)]mod tests{use super::*;#[test]fn scoped(){let(_,c)=measure(||{let _s=span(0);let _t=span(1);}).unwrap();assert_eq!(c.calls[0],1);assert_eq!(c.calls[1],1);let(_,c)=measure(||()).unwrap();assert_eq!(c.calls,[0;N]);}#[test]fn nested(){let(v,_)=measure(||measure(||())).unwrap();assert!(v.is_err());}#[test]fn unwind(){let _=std::panic::catch_unwind(||{let _=measure(||panic!("probe"));});assert!(measure(||()).is_ok());}}
