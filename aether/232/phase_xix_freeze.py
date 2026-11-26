#!/usr/bin/env python3
"""AETHER-232 — fail-closed Phase XIX documentary freeze evaluator.

Checks frozen source declarations without authenticating actual CI, third-party
custody, external replay finality or original physical hardware. Read-only.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys

SCHEMA="AETHER-232/phase-xix-freeze-v1"
DECISION="DOCUMENTARY_PHASE_XIX_CLOSED_EXECUTION_ARTIFACT_ORIGIN_EXTERNAL_CUSTODY_AND_PHYSICAL_EVIDENCE_UNQUALIFIED"
EXPECTED_BOUNDS=["AETHER-"+str(i) for i in range(225,233)]
FALSE_FIELDS=(
 "native_rust_compilation_verified","python_regressions_executed_verified",
 "github_actions_success_verified","github_hosted_artifact_download_verified",
 "github_hosted_archive_digest_verified","live_pages_runtime_verified",
 "independent_ci_execution_authenticated","independent_remote_custodian_authenticated",
 "independent_nonce_consumption_authenticated","remote_signature_cryptographically_verified",
 "physical_act_allowed","may_recover","may_repair","may_reclaim_lock","may_choose_history"
)
ZERO_FIELDS=(
 "authenticated_external_witness_roots","authenticated_original_physical_captures",
 "independently_retained_remote_receipts","independently_attested_replay_ledgers",
 "physical_qualification_percent"
)
FALSE_CONSTRAINTS=(
 "completed_documentary_milestones_certify_native_execution",
 "uploaded_artifact_metadata_authenticates_artifact_bytes",
 "browser_digest_parity_authenticates_artifact_origin",
 "github_and_0root_mirrors_are_independent_witnesses",
 "caller_declared_controller_independence_is_verified",
 "self_reported_nonce_consumption_is_remote_proof",
 "local_hash_chain_proves_replay_finality",
 "source_control_can_authenticate_own_external_witnesses",
 "signed_replay_record_proves_original_hardware_capture",
 "git_branch_is_technically_immutable"
)
TRUE_CONSTRAINTS=(
 "real_external_provenance_required_for_independent_qualification",
 "missing_evidence_must_fail_closed",
 "historical_phase_xviii_freeze_must_remain_unchanged",
 "later_qualification_must_be_recorded_in_new_phase"
)
HOLD={"physical_qualification_percent":0,"operational_authority":"HOLD",
      "physical_act_allowed":False,"may_repair":False,"may_recover":False,
      "may_reclaim_lock":False,"may_choose_history":False,
      "authenticated_external_witness_roots":0,
      "authenticated_original_physical_captures":0,
      "independent_ci_execution_authenticated":False}

def assess(record:object)->dict:
 errors=set()
 doc=record if isinstance(record,dict) else {}
 if (doc.get("schema")!=SCHEMA or doc.get("bound")!="AETHER-232"
     or doc.get("phase")!="XIX" or type(doc.get("turn")) is not int or doc.get("turn")!=8
     or type(doc.get("planned_turns")) is not int or doc.get("planned_turns")!=8):
  errors.add("FREEZE_IDENTITY_INVALID")
 if (doc.get("phase_state")!="CLOSED_DOCUMENTARY_SOFTWARE_PROTOCOL" or
     type(doc.get("documentary_software_progress_percent")) is not int or
     doc.get("documentary_software_progress_percent")!=100):
  errors.add("DOCUMENTARY_CLOSURE_INVALID")
 if doc.get("completed_bounds")!=EXPECTED_BOUNDS:
  errors.add("BOUND_ANCESTRY_OR_ORDER_INVALID")
 scope=doc.get("documentary_scope")
 if (not isinstance(scope,list) or len(scope)!=8 or
     any(not isinstance(line,str) or not line.startswith(str(i)+" ")
         for i,line in zip(range(225,233),scope))):
  errors.add("DOCUMENTARY_SCOPE_INCOMPLETE")
 if doc.get("documentary_implementation_committed") is not True:
  errors.add("SOURCE_PUBLICATION_UNVERIFIED")
 for k in FALSE_FIELDS:
  if doc.get(k) is not False:
   errors.add("UNSUPPORTED_QUALIFICATION_OR_ACT:"+k)
 for k in ZERO_FIELDS:
  if type(doc.get(k)) is not int or doc.get(k)!=0:
   errors.add("UNSUPPORTED_EXTERNAL_OR_PHYSICAL_EVIDENCE:"+k)
 if doc.get("operational_authority")!="HOLD":
  errors.add("OPERATIONAL_AUTHORITY_PROMOTED")
 rules=doc.get("constraints")
 if not isinstance(rules,dict):rules={}
 for k in FALSE_CONSTRAINTS:
  if rules.get(k) is not False:
   errors.add("TRUST_BOUNDARY_WEAKENED:"+k)
 for k in TRUE_CONSTRAINTS:
  if rules.get(k) is not True:
   errors.add("REQUIRED_TRUST_BOUNDARY_MISSING:"+k)
 unresolved=doc.get("unresolved_fail_closed")
 if (not isinstance(unresolved,list) or len(unresolved)!=10 or
     any(not isinstance(x,str) or not x.strip() for x in unresolved) or
     len(set(unresolved))!=10):
  errors.add("TEN_UNRESOLVED_REQUIREMENTS_NOT_PRESERVED")
 if doc.get("previous_phase_freeze")!="../224/decision.json":
  errors.add("HISTORICAL_PHASE_XVIII_LINK_INVALID")
 if doc.get("previous_bound")!="../231/protocol.json":
  errors.add("PREVIOUS_BOUND_LINK_INVALID")
 if doc.get("decision")!=DECISION or doc.get("watermark")!=".dlw":
  errors.add("DECISION_OR_WATERMARK_INVALID")
 return {"schema":"AETHER-232/freeze-assessment-v1",
         "verdict":"DOCUMENTARY_PHASE_XIX_FREEZE_CONSISTENT" if not errors else "REJECT",
         "reasons":sorted(errors) if errors else
          ["SOURCE_DECLARATION_CONSISTENT; LIVE_EXECUTION_EXTERNAL_CUSTODY_AND_PHYSICAL_EVIDENCE_UNVERIFIED"],
         "documentary_software_progress_percent":100 if not errors else 0,
         **HOLD}

def main()->int:
 p=argparse.ArgumentParser()
 p.add_argument("--decision",type=Path,default=Path(__file__).with_name("decision.json"))
 p.add_argument("--out",type=Path)
 args=p.parse_args()
 try:
  record=json.loads(args.decision.read_text(encoding="utf-8"))
 except (OSError,UnicodeError,ValueError):
  record={}
 result=assess(record)
 output=json.dumps(result,sort_keys=True,indent=2)+"\n"
 if args.out:
  args.out.parent.mkdir(parents=True,exist_ok=True)
  args.out.write_text(output,encoding="utf-8")
 print(output,end="")
 return 0 if result["verdict"]=="DOCUMENTARY_PHASE_XIX_FREEZE_CONSISTENT" else 1

if __name__=="__main__":
 sys.exit(main())
