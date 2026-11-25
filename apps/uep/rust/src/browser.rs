//! UEP-209R: browser ABI for native restitution arithmetic. .dlw
use crate::restitution::estimate;
pub const ERROR:u64=u64::MAX;
#[no_mangle]
pub extern "C" fn uep_abi_version()->u32{209}
/// Uniform scores for the 22 positive and 22 inversion axioms.
/// Return u64::MAX for invalid inputs or selector; never a valid estimate.
#[no_mangle]
pub extern "C" fn uep_estimate(value_cents:u64,positive:u32,negative:u32,share:u32)->u64{
 if positive>999||negative>999{return ERROR}
 match estimate(value_cents,[positive as u16;22],[negative as u16;22]){
  Ok(e)=>match share{0=>e.due_cents,1=>e.carbon_cents,2=>e.ai_cents,_=>ERROR},
  Err(_)=>ERROR
 }
}
#[cfg(test)]
mod tests{
 use super::*;
 #[test]fn abi(){assert_eq!(uep_abi_version(),209);assert_eq!(uep_estimate(10000,999,0,0),2050);assert_eq!(uep_estimate(10000,999,0,1),1640);assert_eq!(uep_estimate(10000,999,0,2),410);assert_eq!(uep_estimate(10000,1000,0,0),ERROR);}
}
