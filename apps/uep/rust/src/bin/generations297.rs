//! UEP-295R: qualified execution attribution with sealed byte parity. .dlw
use oasis_uep::{checkpoint,multi_archive,linked_segment::Anchor as LegacyAnchor,authenticated_state::State,qualified_recovery,qualified_delta::Qualified,state_hash,executable::Request,equilibrium::Step,population::Period,bridge::Shares,dividend::Revenue,capacity::Input,verification_profile::{self,NAMES}};
use std::{env,fs,path::Path};
use oasis_uep::authenticated_recovery;
use sha2::{Digest,Sha256};
const ROOT:&[u8]=include_bytes!("../../../UEP-259R-integrated-generations/root.archive");
const CP:&[u8]=include_bytes!("../../../UEP-259R-integrated-generations/root.checkpoint");
const A:&[u8]=include_bytes!("../../../UEP-259R-integrated-generations/anchors.bin");
const S1:&[u8]=include_bytes!("../../../UEP-259R-integrated-generations/segment-720.bin");
const S2:&[u8]=include_bytes!("../../../UEP-259R-integrated-generations/segment-1080.bin");
fn main()->Result<(),Box<dyn std::error::Error>>{
 let dir=env::args().nth(1).ok_or("output directory")?;let dir=Path::new(&dir);
 let cp=checkpoint::decode(CP)?;assert_eq!(A.len(),144);
 let legacy:Vec<LegacyAnchor>=A.chunks_exact(72).map(|b|LegacyAnchor{total:u64::from_be_bytes(b[..8].try_into().unwrap()),ancestry:b[8..40].try_into().unwrap(),closing:b[40..72].try_into().unwrap()}).collect();
 let root=multi_archive::recover(ROOT,&cp,&legacy,&legacy[1],|i|Ok(if i==0{S1}else{S2}.to_vec()))?;
 let original=state_hash::encode(root.universe())?;assert_eq!(original.as_slice(),include_bytes!("../../../UEP-259R-integrated-generations/terminal.state"));
 let s=State::build(root.universe(),legacy[1].closing)?;let u=s.compact(root.universe(),&s.root())?;
 let qualified=Qualified::import(&s,&u,&s.root())?;

 let mut tape=qualified_recovery::Tape::start(&qualified,qualified.root())?;
 let mut legacy=authenticated_recovery::Tape::start(&s,&u,&s.root())?;
 let mut current="G_36".to_string();let mut csv=String::from("generation,start,end,bytes,known,lots,arrears,sha256\n");let mut anchors=Vec::new();
 for generation in 0..3u64{
 let opening=tape.clone();let lo=legacy.clone();let start=tape.universe().total_observations();
 for t in 0..360u64{
 let k=generation*360+t;let (enter,depart)=if t%30==0{let id=format!("X_{k}");let old=std::mem::replace(&mut current,id.clone());(vec![id],vec![old])}else{(vec![],vec![])};
 let funding=if generation==0{500}else if generation==1{750}else{600};
 let st=Step{period:Period{enter,depart,award:100,funding},restitution:Shares{carbon:100,ai:25},revenue:Revenue{public_equity:600,licensing:0,automation_royalties:0,infrastructure_return:0},dividend_cap:100,resources:Input{inflow:[100;4],essential:[20;4],decay_bps:1000,work_ceiling:17}};
 let mut future=st.clone();future.period.enter.clear();future.period.depart.clear();future.period.funding=750;
 let r=Request{present:st,requested:0,complete:0,accept:0,future:vec![future]};
 let (n,c)=verification_profile::measure(||tape.append(&r))?;tape=n?;legacy=legacy.append(&r)?;
 assert_eq!((c.calls[1],c.calls[10],c.calls[11],c.calls[12],c.calls[28]),(1,0,0,0,0));assert_eq!(tape.projection().root(),&legacy.projection().root());assert_eq!(tape.universe(),legacy.universe());
 }
 let raw=tape.encode()?;assert_eq!(raw,legacy.encode()?);assert_eq!(raw.len(),tape.encoded_len());let a=tape.anchor()?;let b=legacy.anchor()?;assert_eq!((a.total,a.digest,&a.closing),(b.total,b.digest,&b.closing));
 let path=dir.join(format!("generation-{}.bin",generation+1));fs::write(&path,&raw)?;
 let recovered=qualified_recovery::recover_file(opening.projection(),opening.projection().root(),&path,&a)?;assert_eq!(recovered,tape);
 let old=authenticated_recovery::recover_file(lo.projection(),lo.universe(),&lo.projection().root(),&path,&b)?;assert_eq!(old,legacy);
 let mut bad=a.clone();bad.digest[0]^=1;assert!(qualified_recovery::recover_file(opening.projection(),opening.projection().root(),&path,&bad).is_err());
 if generation>0{assert!(qualified_recovery::recover(&qualified,qualified.root(),&raw,&a).is_err());}
 let pop=tape.universe().population_ledger();let digest=format!("{:x}",Sha256::digest(&raw));csv.push_str(&format!("{},{start},{},{},{},{},{},{digest}\n",generation+1,a.total,raw.len(),pop.known.len(),pop.lots.len(),pop.outstanding()?));
 anchors.extend_from_slice(&a.total.to_be_bytes());anchors.extend_from_slice(&a.digest);anchors.extend_from_slice(&a.closing.encode());
 fs::write(dir.join(format!("generation-{}.state",generation+1)),state_hash::encode(tape.universe())?)?;
 tape=recovered.successor(&a)?;legacy=old.successor(&b)?;assert_eq!(tape.encoded_len(),192);assert_eq!(tape.projection().root(),&legacy.projection().root());assert_eq!(tape.universe(),legacy.universe());assert!(tape.universe().observations().is_empty());
 }
 assert_eq!(tape.universe().total_observations(),2160);assert_eq!(state_hash::encode(root.universe())?,original);fs::write(dir.join("generations297.csv"),csv)?;fs::write(dir.join("anchors297.bin"),anchors)?;
 println!("{{\"generations\":3,\"newPeriods\":1080,\"terminal\":2160,\"recoveries\":6,\"exactParity\":true,\"actualPayments\":0}}");Ok(())
}
