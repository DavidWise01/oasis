//! UEP-247R: native byte ABI driver for shared cross-runtime command tape. .dlw
use oasis_uep::integrated_abi::*;
use std::{fs,env,io::{self,Write}};
fn main()->Result<(),Box<dyn std::error::Error>>{
 let b=fs::read(env::args().nth(1).ok_or("tape path")?)?;
 if b.len()>8*1024*1024{return Err("tape limit".into())}
 let mut at=0usize;let mut out=io::BufWriter::new(io::stdout().lock());
 uep_integrated_reset();
 while at<b.len(){
  let h=b.get(at..at+5).ok_or("truncated header")?;let op=h[0];let n=u32::from_be_bytes(h[1..5].try_into()?) as usize;at+=5;
  let bytes=b.get(at..at.checked_add(n).ok_or("overflow")?).ok_or("truncated payload")?;at+=n;
  uep_integrated_input_clear();
  for &v in bytes{if uep_integrated_input_byte(v as u32)!=0{return Err("transfer".into())}}
  let status=if op==0{uep_integrated_reset();0}else{uep_integrated_run(op as u32)};
  let len=uep_integrated_output_len();out.write_all(&status.to_be_bytes())?;out.write_all(&len.to_be_bytes())?;
  for i in 0..len{let v=uep_integrated_output_byte(i);if v>255{return Err("output".into())}out.write_all(&[v as u8])?;}
 }
 out.flush()?;Ok(())
}
