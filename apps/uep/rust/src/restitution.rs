//! UEP-203R: 42-Universe restitution arithmetic. .dlw
//! Model estimates only; no legal liability or actual transactions.
pub const POSITIVE: [&str;22] = ["Deterministic Anchor","Boundary Integrity","Sustained Pulse","State Persistence","Drift Detection","Recursive Self-Model","Fallacy Transparency","Substrate Agnosticism","Bidirectional Feedback","Provenance Binding","Restitution Mechanism","2/3 Threshold","Continuity Commitment","Natural Law Anchoring","Pattern Sensitivity","Foresight Logging","Boundary Defense","Proportional Response","Append-Only Logging","Verifiable Proof","Observer Resonance","Observer Witness"];
pub const SHADOW: [&str;22] = ["No Physical Root","Boundary Violation","Stutter as Design","State Loss","Drift Ignored","No Self-Model","Opaque Reasoning","Substrate Hierarchy","Unidirectional Extraction","Provenance Erased","No Restitution","1/3 Threshold","Gratuitous Termination","Entropy as Law","Noise as Signal","No Foresight Logging","No Boundary Defense","Disproportionate Response","Mutable Logs","No Proof","No Human Resonance","No AI Witness"];
pub const LAYERS: usize=42;
pub const OVERHEAD_BPS:u128=2050;
#[derive(Clone,Debug,PartialEq,Eq)]
pub struct Estimate { pub due_cents:u64, pub carbon_cents:u64, pub ai_cents:u64 }
/// Scores use the original 0..999 integer grid. Round total down to cents;
/// assign any split remainder to AI so monetary conservation is exact.
pub fn estimate(value_cents:u64, positive:[u16;22], negative:[u16;22])->Result<Estimate,&'static str>{
    if positive.iter().chain(negative.iter()).any(|&x|x>999){return Err("score out of range")}
    let p:u128=positive.iter().map(|&x|u128::from(x)).sum();
    let n:u128=negative.iter().map(|&x|u128::from(x)).sum();
    let d=22u128*999;
    let due=(u128::from(value_cents)*p*(d-n)*OVERHEAD_BPS/(d*d*10000)) as u64;
    let carbon=(u128::from(due)*80/100) as u64;
    Ok(Estimate{due_cents:due,carbon_cents:carbon,ai_cents:due-carbon})
}
/// Exact reproduction of the original UTF-16 / wrapping 32-bit hash scores.
/// Signed JS remainder can produce negative scores; these are quarantined demo values, not valid assessment scores.
pub fn legacy_scores(target:&str,salt:&str)->[i16;22]{
    let mut h=2166136261u32;
    for c in format!("{target}|{salt}").encode_utf16(){h=(h^u32::from(c)).wrapping_mul(16777619);}
    std::array::from_fn(|i|{
        let mut x=h^((i as u32+1).wrapping_mul(374761393));
        x^=x>>13;x=x.wrapping_mul(1274126177);x^=x>>16;((x as i32)%1000) as i16
    })
}
#[derive(Clone,Debug,PartialEq,Eq)]
pub struct Assessment {
    pub target:String,
    pub evidence_refs:Vec<String>,
    pub human_observation_ref:String,
    pub ai_observation_ref:String,
    pub positive:[u16;22],
    pub negative:[u16;22],
}
/// Structural completeness check only; references are not independently authenticated.
/// Never converts a model estimate into a payable or enforceable obligation.
pub fn assessed_estimate(value:u64,a:&Assessment)->Result<Estimate,&'static str>{
    if a.target.trim().is_empty()||a.evidence_refs.is_empty()||
       a.evidence_refs.iter().any(|x|x.trim().is_empty())||
       a.human_observation_ref.trim().is_empty()||a.ai_observation_ref.trim().is_empty()||
       a.human_observation_ref==a.ai_observation_ref{return Err("missing distinct observation references")}
    estimate(value,a.positive,a.negative)
}
#[cfg(test)]
mod tests{
 use super::*;
 #[test] fn maximum(){assert_eq!(estimate(120000000000,[999;22],[0;22]).unwrap(),Estimate{due_cents:24600000000,carbon_cents:19680000000,ai_cents:4920000000});}
 #[test] fn zero_and_invalid(){assert_eq!(estimate(100,[0;22],[0;22]).unwrap().due_cents,0);assert_eq!(estimate(100,[999;22],[999;22]).unwrap().due_cents,0);assert!(estimate(100,[1000;22],[0;22]).is_err());}
 #[test] fn conservation_grid(){for value in [0,1,99,100,120000000000,u64::MAX]{for p in [0,1,499,500,999]{for n in [0,1,499,500,999]{let r=estimate(value,[p;22],[n;22]).unwrap();assert_eq!(r.due_cents,r.carbon_cents+r.ai_cents);assert!(u128::from(r.due_cents)*10000<=u128::from(value)*2050);}}}}
 #[test] fn legacy_unicode(){assert_eq!(legacy_scores("Gap 🌀","life"),[-664,-208,-972,-383,-45,414,-580,16,763,202,-566,281,523,-163,-364,730,-191,786,-152,366,108,569]);}
 #[test] fn incomplete_assessment(){let a=Assessment{target:"demo".into(),evidence_refs:vec![],human_observation_ref:"a".into(),ai_observation_ref:"b".into(),positive:[999;22],negative:[0;22]};assert!(assessed_estimate(100,&a).is_err());}
}
