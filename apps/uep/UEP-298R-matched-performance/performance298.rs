//! UEP-298R: five-path matched performance and byte-compatible replay. .dlw
use baseline::{checkpoint,multi_archive,linked_segment::Anchor as LegacyAnchor,indexed_recovery,working_projection::Projection,authenticated_state::State,authenticated_recovery,state_hash,executable::Request,equilibrium::Step,population::Period,bridge::Shares,dividend::Revenue,capacity::Input,verification_profile,qualified_delta::Qualified,qualified_recovery};
use oasis_uep as refined;
use std::{env,fs,path::Path,time::Instant};
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
 let p=Projection::build(root.universe(),legacy[1].closing)?;let u=p.compact(root.universe())?;let pc=p.commitment(&u)?;
 let s=State::build(&u,legacy[1].closing)?;let sc=s.root();let q=Qualified::import(&s,&u,&sc)?;
 let rc=refined::checkpoint::decode(CP)?;
 let ra:Vec<refined::linked_segment::Anchor>=A.chunks_exact(72).map(|b|refined::linked_segment::Anchor{total:u64::from_be_bytes(b[..8].try_into().unwrap()),ancestry:b[8..40].try_into().unwrap(),closing:b[40..72].try_into().unwrap()}).collect();
 let rr=refined::multi_archive::recover(ROOT,&rc,&ra,&ra[1],|i|Ok(if i==0{S1}else{S2}.to_vec()))?;
 let rs=refined::authenticated_state::State::build(rr.universe(),ra[1].closing)?;
 let ru=rs.compact(rr.universe(),&rs.root())?;
 let rq=refined::qualified_delta::Qualified::import(&rs,&ru,&rs.root())?;
 assert_eq!(rq.root().encode(),sc.encode());
 let mut csv=String::from("scenario,period,known,lots,arrears,observations,canonical_bytes,reference_ns,indexed_ns,authenticated_ns,qualified_ns,refined_ns,reference_audits,indexed_audits,authenticated_audits,qualified_audits,qualified_balance_builds,qualified_membership_builds,qualified_chronology_verifies,refined_audits,refined_full_encodes\n");
 let mut recovery=String::from("scenario,path,terminal,tape_bytes,recovery_ns\n");
 fs::write(dir.join("opening.commitment"),sc.encode())?;
 for scenario in ["balanced","scarcity","churn"]{
 let mut reference=u.clone();let mut indexed=indexed_recovery::Tape::start(&p,&u,&pc)?;let mut auth=authenticated_recovery::Tape::start(&s,&u,&sc)?;
 let mut qual=qualified_recovery::Tape::start(&q,&sc)?;let mut rt=refined::qualified_recovery::Tape::start(&rq,rq.root())?;let mut current="G_36".to_string();
 for t in 0..360u64{
 let (enter,depart)=if scenario=="churn"||t%30==0{let id=format!("P_{}",t+1);let old=std::mem::replace(&mut current,id.clone());(vec![id],vec![old])}else{(vec![],vec![])};
 let funding=if scenario=="scarcity"{500}else if scenario=="churn"{600}else if t%30<10{500}else{750};
 let st=Step{period:Period{enter,depart,award:100,funding},restitution:Shares{carbon:100,ai:25},revenue:Revenue{public_equity:600,licensing:0,automation_royalties:0,infrastructure_return:0},dividend_cap:100,resources:Input{inflow:[100;4],essential:[20;4],decay_bps:1000,work_ceiling:17}};
 let mut future=st.clone();future.period.enter.clear();future.period.depart.clear();future.period.funding=750;
 let r=Request{present:st,requested:0,complete:0,accept:0,future:vec![future]};
 let raw=baseline::request_codec::encode(&r)?;let req=refined::request_codec::decode(&raw)?;assert_eq!(refined::request_codec::encode(&req)?,raw);
 let mut times=[0u128;5];let mut rn=None;let mut v=None;let mut i=None;let mut a=None;let mut z=None;
 // Rotate execution order to reduce systematic first-path bias. Timing excludes diagnostic instrumentation.
 for offset in 0..5{let k=(t as usize+offset)%5;let start=Instant::now();match k{0=>v=Some(reference.advance(&r)?),1=>i=Some(indexed.append(&r)?),2=>a=Some(auth.append(&r)?),3=>z=Some(qual.append(&r)?),_=>rn=Some(rt.append(&req)?)}times[k]=start.elapsed().as_nanos();}
 let(v,i,a,z)=(v.unwrap(),i.unwrap(),a.unwrap(),z.unwrap());assert_eq!(a.encode()?,z.encode()?);assert_eq!(a.projection().root(),*z.projection().root());assert_eq!(a.universe(),z.universe());
 let rn=rn.unwrap();assert_eq!(rn.encode()?,z.encode()?);assert_eq!(rn.projection().root().encode(),z.projection().root().encode());
 let bytes=state_hash::encode(&v)?;assert_eq!(bytes,refined::state_hash::encode(rn.universe())?);assert_eq!(bytes,state_hash::encode(i.universe())?);assert_eq!(bytes,state_hash::encode(a.universe())?);assert_eq!(v.observations().last(),a.universe().observations().last());
 // Separate instrumented repetition, excluded from elapsed timings.
 let(v2,vc)=verification_profile::measure(||reference.advance(&r))?;let(i2,ic)=verification_profile::measure(||indexed.append(&r))?;let(a2,ac)=verification_profile::measure(||auth.append(&r))?;
 let(z2,zc)=verification_profile::measure(||qual.append(&r))?;assert_eq!(z,z2?);assert_eq!((zc.calls[1],zc.calls[10],zc.calls[11],zc.calls[12]),(1,0,0,0));assert_eq!(v,v2?);assert_eq!(i,i2?);assert_eq!(a,a2?);assert_eq!((vc.calls[1],ic.calls[1],ac.calls[1]),(1,3,1));
 let (rp,rx)=refined::verification_profile::measure(||rt.append(&req))?;assert_eq!(rp?,rn);assert_eq!((rx.calls[1],rx.calls[10],rx.calls[11],rx.calls[12],rx.calls[28],rx.calls[29]),(1,0,0,0,0,1));
 let pop=v.population_ledger();let o=v.observations().last().ok_or("observation")?;assert_eq!(o.accepted,17);assert_eq!(o.work,0);assert_eq!(o.funded,o.due.min(funding));assert_eq!(a.projection().balance_tree().total()?,pop.outstanding()?);
 csv.push_str(&format!("{scenario},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{}\n",1081+t,pop.known.len(),pop.lots.len(),pop.outstanding()?,v.observations().len(),bytes.len(),times[0],times[1],times[2],times[3],times[4],vc.calls[1],ic.calls[1],ac.calls[1],zc.calls[1],zc.calls[10],zc.calls[11],zc.calls[12],rx.calls[1],rx.calls[28]));
 reference=v;indexed=i;auth=a;qual=z;rt=rn;
 }
 let ia=indexed.anchor()?;let aa=auth.anchor()?;let qa=qual.anchor()?;assert_eq!((qa.total,qa.digest,&qa.closing),(aa.total,aa.digest,&aa.closing));assert_eq!(ia.total,1440);assert_eq!(aa.total,1440);
 let ip=dir.join(format!("{scenario}-indexed.bin"));let ap=dir.join(format!("{scenario}-authenticated.bin"));fs::write(&ip,indexed.encode()?)?;fs::write(&ap,auth.encode()?)?;
 let start=Instant::now();let ir=indexed_recovery::recover_file(&p,&u,&pc,&ip,&ia)?;let it=start.elapsed().as_nanos();assert_eq!(ir,indexed);
 let start=Instant::now();let ar=authenticated_recovery::recover_file(&s,&u,&sc,&ap,&aa)?;let at=start.elapsed().as_nanos();assert_eq!(ar,auth);
 assert_eq!(state_hash::encode(ar.universe())?,state_hash::encode(&reference)?);
 let start=Instant::now();let qr=qualified_recovery::recover_file(&q,&sc,&ap,&qa)?;let qt=start.elapsed().as_nanos();assert_eq!(qr,qual);let qnext=qual.successor(&qa)?;assert_eq!(qnext.projection().root(),&qa.closing);assert!(qnext.universe().observations().is_empty());for(path,file,ns)in [("indexed",&ip,it),("authenticated",&ap,at),("qualified",&ap,qt)]{recovery.push_str(&format!("{scenario},{path},1440,{},{}\n",fs::metadata(file)?.len(),ns));}
 let ra=rt.anchor()?;assert_eq!((ra.total,ra.digest,ra.closing.encode()),(qa.total,qa.digest,qa.closing.encode()));let now=Instant::now();let rec=refined::qualified_recovery::recover_file(&rq,rq.root(),&ap,&ra)?;let ns=now.elapsed().as_nanos();assert_eq!(rec,rt);recovery.push_str(&format!("{scenario},refined,1440,{},{}\n",fs::metadata(&ap)?.len(),ns));
 let sealed=match scenario{"balanced"=>include_bytes!("../../../UEP-289R-integrated-changed-path/balanced-authenticated.bin").as_slice(),"scarcity"=>include_bytes!("../../../UEP-289R-integrated-changed-path/scarcity-authenticated.bin").as_slice(),_=>include_bytes!("../../../UEP-289R-integrated-changed-path/churn-authenticated.bin").as_slice()};assert_eq!(rt.encode()?.as_slice(),sealed);
 let mut anchors=Vec::new();for(total,digest,closing)in [(ia.total,ia.digest,ia.closing.encode()),(aa.total,aa.digest,aa.closing.encode())]{anchors.extend_from_slice(&total.to_be_bytes());anchors.extend_from_slice(&digest);anchors.extend_from_slice(&closing);}
 fs::write(dir.join(format!("{scenario}-anchors.bin")),anchors)?;fs::write(dir.join(format!("{scenario}-terminal.state")),state_hash::encode(&reference)?)?;
 let next=auth.successor(&aa)?;assert_eq!(next.projection().root(),aa.closing);assert!(next.universe().observations().is_empty());
 }
 assert_eq!(state_hash::encode(root.universe())?,original);
 fs::write(dir.join("performance298.csv"),csv)?;fs::write(dir.join("recovery298.csv"),recovery)?;
 println!("{{\"scenarios\":3,\"pairedTransitions\":1080,\"timedTransitions\":5400,\"recoveredTapes\":12,\"canonicalParity\":true,\"instrumentationParity\":true,\"actualPayments\":0}}");Ok(())
}
