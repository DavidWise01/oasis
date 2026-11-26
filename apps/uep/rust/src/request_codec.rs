//! UEP-241R: canonical ordered request encoding; structural validity is not execution authority. .dlw
use crate::{executable::Request,equilibrium::Step,population::Period,bridge::Shares,dividend::Revenue,capacity::Input};
use sha2::{Digest,Sha256};
const MAGIC:&[u8;8]=b"UEP241R\0";
const LIMIT:usize=64*1024*1024;
fn number(b:&mut Vec<u8>,v:u64){b.extend_from_slice(&v.to_be_bytes())}
fn ids(b:&mut Vec<u8>,v:&[String])->Result<(),&'static str>{
 if v.len()>10000{return Err("identity count")}
 number(b,v.len() as u64);
 for s in v{if s.is_empty()||s.len()>30||!s.bytes().all(|x|x.is_ascii_alphanumeric()||x==b'_'||x==b'-'){return Err("identity syntax")}number(b,s.len() as u64);b.extend_from_slice(s.as_bytes());}
 Ok(())
}
fn step(b:&mut Vec<u8>,s:&Step)->Result<(),&'static str>{
 ids(b,&s.period.enter)?;ids(b,&s.period.depart)?;
 for v in [s.period.award,s.period.funding,s.restitution.carbon,s.restitution.ai,s.revenue.public_equity,s.revenue.licensing,s.revenue.automation_royalties,s.revenue.infrastructure_return,s.dividend_cap]{number(b,v)}
 for v in s.resources.inflow.iter().chain(s.resources.essential.iter()){number(b,*v)}
 number(b,s.resources.decay_bps);number(b,s.resources.work_ceiling);Ok(())
}
pub fn encode(r:&Request)->Result<Vec<u8>,&'static str>{
 if r.future.is_empty()||r.future.len()>64{return Err("horizon")}
 let mut b=MAGIC.to_vec();step(&mut b,&r.present)?;
 for v in [r.requested,r.complete,r.accept,r.future.len() as u64]{number(&mut b,v)}
 for s in &r.future{step(&mut b,s)?;if b.len()>LIMIT{return Err("request size")}}
 Ok(b)
}
struct Reader<'a>{b:&'a[u8],p:usize}
impl<'a> Reader<'a>{
 fn take(&mut self,n:usize)->Result<&'a[u8],&'static str>{let end=self.p.checked_add(n).ok_or("length overflow")?;let v=self.b.get(self.p..end).ok_or("truncated request")?;self.p=end;Ok(v)}
 fn n(&mut self)->Result<u64,&'static str>{Ok(u64::from_be_bytes(self.take(8)?.try_into().map_err(|_|"number")?))}
 fn ids(&mut self)->Result<Vec<String>,&'static str>{let n=self.n()?;if n>10000{return Err("identity count")}let mut v=Vec::new();for _ in 0..n{let k=self.n()?;if k==0||k>30{return Err("identity length")}let x=self.take(k as usize)?;if !x.iter().all(|&b|b.is_ascii_alphanumeric()||b==b'_'||b==b'-'){return Err("identity syntax")}v.push(std::str::from_utf8(x).map_err(|_|"identity utf8")?.to_owned());}Ok(v)}
 fn four(&mut self)->Result<[u64;4],&'static str>{Ok([self.n()?,self.n()?,self.n()?,self.n()?])}
 fn step(&mut self)->Result<Step,&'static str>{Ok(Step{period:Period{enter:self.ids()?,depart:self.ids()?,award:self.n()?,funding:self.n()?},restitution:Shares{carbon:self.n()?,ai:self.n()?},revenue:Revenue{public_equity:self.n()?,licensing:self.n()?,automation_royalties:self.n()?,infrastructure_return:self.n()?},dividend_cap:self.n()?,resources:Input{inflow:self.four()?,essential:self.four()?,decay_bps:self.n()?,work_ceiling:self.n()?}})}
}
pub fn decode(b:&[u8])->Result<Request,&'static str>{
 if b.len()>LIMIT{return Err("request size")}
 let mut d=Reader{b,p:0};if d.take(8)?!=MAGIC{return Err("request version")}
 let present=d.step()?;let requested=d.n()?;let complete=d.n()?;let accept=d.n()?;let n=d.n()?;
 if n==0||n>64{return Err("horizon")}let mut future=Vec::new();for _ in 0..n{future.push(d.step()?)}
 if d.p!=b.len(){return Err("trailing bytes")}
 Ok(Request{present,requested,complete,accept,future})
}
pub fn fingerprint(r:&Request)->Result<[u8;32],&'static str>{let mut h=Sha256::new();h.update(b"OASIS-UEP-241R-request-v1");h.update(encode(r)?);Ok(h.finalize().into())}
#[cfg(test)]
mod tests{
 use super::*;
 fn fixture()->Request{let s=Step{period:Period{enter:vec!["new_1".into(),"new_2".into()],depart:vec!["A_1".into()],award:100,funding:600},restitution:Shares{carbon:100,ai:25},revenue:Revenue{public_equity:600,licensing:2,automation_royalties:3,infrastructure_return:4},dividend_cap:100,resources:Input{inflow:[1,2,3,4],essential:[5,6,7,8],decay_bps:2000,work_ceiling:17}};Request{present:s.clone(),requested:5,complete:1,accept:2,future:vec![s]}}
 #[test]fn roundtrip(){let r=fixture();let b=encode(&r).unwrap();assert_eq!(decode(&b).unwrap(),r);assert_eq!(encode(&decode(&b).unwrap()).unwrap(),b);}
 #[test]fn every_truncation(){let b=encode(&fixture()).unwrap();for i in 0..b.len(){assert!(decode(&b[..i]).is_err());}}
 #[test]fn reject_structure(){let mut b=encode(&fixture()).unwrap();b.push(0);assert!(decode(&b).is_err());b.pop();b[0]^=1;assert!(decode(&b).is_err());let mut r=fixture();r.future.clear();assert!(encode(&r).is_err());r=fixture();r.present.period.enter.push("bad id".into());assert!(encode(&r).is_err());}
 #[test]fn order_and_future(){let r=fixture();let h=fingerprint(&r).unwrap();let mut q=r.clone();q.present.period.enter.swap(0,1);assert_ne!(h,fingerprint(&q).unwrap());q=r.clone();q.future[0].resources.inflow[3]+=1;assert_ne!(h,fingerprint(&q).unwrap());q=r.clone();q.accept+=1;assert_ne!(h,fingerprint(&q).unwrap());}
 #[test]fn all_numeric_fields(){let r=fixture();let b=encode(&r).unwrap();assert_eq!(&b[..8],MAGIC);let mut q=r.clone();q.present.period.funding=u64::MAX;assert_eq!(decode(&encode(&q).unwrap()).unwrap(),q);assert_ne!(fingerprint(&q).unwrap(),fingerprint(&r).unwrap());}
}
