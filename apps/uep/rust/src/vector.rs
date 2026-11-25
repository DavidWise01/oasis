//! UEP-216R: full axiom vector ABI, preserving ABI 209. .dlw
use crate::{browser::ERROR,restitution::estimate};
#[no_mangle]
pub extern "C" fn uep_vector_version()->u32{216}
/// Four groups of eleven ten-bit scores would exceed a u64.
/// Instead use eight words, each carrying six ten-bit scores.
/// Last four slots must be zero. No pointer or mutable global state.
#[no_mangle]
pub extern "C" fn uep_vector_estimate(value:u64,share:u32,a:u64,b:u64,c:u64,d:u64,e:u64,f:u64,g:u64,h:u64)->u64{
 let mut scores=[0u16;48];
 for (i,w) in [a,b,c,d,e,f,g,h].into_iter().enumerate(){
  if w>>60!=0{return ERROR}
  for j in 0..6{let v=((w>>(j*10))&1023) as u16;if v>999{return ERROR}scores[i*6+j]=v;}
 }
 if scores[44..].iter().any(|&v|v!=0){return ERROR}
 let mut p=[0;22];let mut n=[0;22];p.copy_from_slice(&scores[..22]);n.copy_from_slice(&scores[22..44]);
 match estimate(value,p,n){Ok(r)=>match share{0=>r.due_cents,1=>r.carbon_cents,2=>r.ai_cents,_=>ERROR},Err(_)=>ERROR}
}
#[cfg(test)]
mod tests{
 use super::*;
 fn call(v:u64,s:u32,x:[u16;48])->u64{let w:[u64;8]=std::array::from_fn(|i|(0..6).fold(0,|a,j|a|(u64::from(x[i*6+j])<<(10*j))));uep_vector_estimate(v,s,w[0],w[1],w[2],w[3],w[4],w[5],w[6],w[7])}
 #[test]fn all_slots(){for k in 0..44{let mut x=[0;48];x[..22].fill(999);x[k]=500;let mut p=[0;22];let mut n=[0;22];p.copy_from_slice(&x[..22]);n.copy_from_slice(&x[22..44]);let r=estimate(u64::MAX,p,n).unwrap();assert_eq!(call(u64::MAX,0,x),r.due_cents);assert_eq!(call(u64::MAX,1,x),r.carbon_cents);assert_eq!(call(u64::MAX,2,x),r.ai_cents);}}
 #[test]fn reject(){let mut x=[0;48];x[44]=1;assert_eq!(call(100,0,x),ERROR);x[44]=0;x[21]=1000;assert_eq!(call(100,0,x),ERROR);assert_eq!(call(100,3,[0;48]),ERROR);assert_eq!(uep_vector_estimate(100,0,1<<60,0,0,0,0,0,0,0),ERROR);}
}
