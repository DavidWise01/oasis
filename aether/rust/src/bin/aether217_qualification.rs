//! AETHER-217-RS — reproducible executable documentary qualification.
//! Running this binary validates the historical AETHER-216 JSON freeze.
//! It cannot authenticate original remote custody or authorize physical ACT.
use aether_evidence::phase_xvii_freeze::{assess,FreezeRecord};
use serde_json::{json,Value};
use std::process::ExitCode;

const BOUND:&str="AETHER-217";
const FIXTURE:&str=include_str!("../../../216/decision.json");

fn result()->Result<Value,String>{
 let frozen:FreezeRecord=serde_json::from_str(FIXTURE)
  .map_err(|e|format!("FROZEN_DECISION_PARSE_ERROR: {e}"))?;
 let decision=assess(&frozen);
 let ok=decision.verdict=="DOCUMENTARY_PHASE_XVII_FREEZE_CONSISTENT"
  &&decision.reasons.is_empty()&&decision.documentary_software_percent==100
  &&decision.physical_qualification_percent==0
  &&decision.operational_authority=="HOLD"&&!decision.physical_act_allowed
  &&!decision.may_repair&&!decision.may_recover
  &&!decision.may_reclaim_lock&&!decision.may_choose_history;
 Ok(json!({
  "schema":"AETHER-217/executable-qualification-v1",
  "bound":BOUND,
  "source_freeze":"AETHER-216",
  "source_freeze_verdict":decision.verdict,
  "source_freeze_reasons":decision.reasons,
  "documentary_decision_consistent":ok,
  "native_binary_executed":true,
  "native_test_suite_executed":false,
  "independently_authenticated_remote_receipts":0,
  "independently_authenticated_physical_witnesses":0,
  "physical_qualification_percent":0,
  "may_recover":false,
  "may_repair":false,
  "may_reclaim_lock":false,
  "may_choose_history":false,
  "operational_authority":"HOLD",
  "physical_act_allowed":false,
  "note":"Native execution evaluates embedded documentary freeze only. CI tests require separate job evidence."
 }))
}
fn main()->ExitCode{
 let artifact=match result(){
  Ok(v)=>v,
  Err(reason)=>{
   eprintln!("AETHER-217 QUALIFICATION HOLD: {reason}");
   return ExitCode::from(2);
  },
 };
 let passed=artifact.get("documentary_decision_consistent").and_then(Value::as_bool)==Some(true);
 match serde_json::to_string_pretty(&artifact){
  Ok(value)=>println!("{value}"),
  Err(_)=>return ExitCode::from(3),
 }
 if passed{ExitCode::SUCCESS}else{ExitCode::from(1)}
}
