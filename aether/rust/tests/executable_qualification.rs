//! AETHER-217-RS: exercise the compiled qualification binary in Cargo tests.
use serde_json::Value;
use std::process::Command;

#[test]
fn executable_freeze_evaluation_is_documentary_only(){
 let output=Command::new(env!("CARGO_BIN_EXE_aether217_qualification"))
  .output().expect("Rust qualification binary must execute");
 assert!(output.status.success(),"{}",String::from_utf8_lossy(&output.stderr));
 let report:Value=serde_json::from_slice(&output.stdout).expect("qualification JSON");
 assert_eq!(report["schema"],"AETHER-217/executable-qualification-v1");
 assert_eq!(report["bound"],"AETHER-217");
 assert_eq!(report["source_freeze"],"AETHER-216");
 assert_eq!(report["documentary_decision_consistent"],true);
}
#[test]
fn executable_never_claims_external_custody(){
 let output=Command::new(env!("CARGO_BIN_EXE_aether217_qualification")).output().unwrap();
 let r:Value=serde_json::from_slice(&output.stdout).unwrap();
 assert_eq!(r["independently_authenticated_remote_receipts"],0);
 assert_eq!(r["independently_authenticated_physical_witnesses"],0);
 assert_eq!(r["physical_qualification_percent"],0);
}
#[test]
fn executable_never_promotes_act_or_recovery(){
 let output=Command::new(env!("CARGO_BIN_EXE_aether217_qualification")).output().unwrap();
 let r:Value=serde_json::from_slice(&output.stdout).unwrap();
 assert_eq!(r["operational_authority"],"HOLD");
 for f in ["physical_act_allowed","may_recover","may_repair","may_reclaim_lock","may_choose_history"]{
  assert_eq!(r[f],false,"{f} unexpectedly enabled");
 }
}
#[test]
fn executable_does_not_claim_test_run_evidence(){
 let output=Command::new(env!("CARGO_BIN_EXE_aether217_qualification")).output().unwrap();
 let r:Value=serde_json::from_slice(&output.stdout).unwrap();
 assert_eq!(r["native_binary_executed"],true);
 assert_eq!(r["native_test_suite_executed"],false);
}
