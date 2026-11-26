#!/usr/bin/env python3
"""AETHER-231 — fail-closed integrated independent-evidence adjudicator.

Inputs are read-only assessments from AETHER-226..230. This evaluator verifies
cross-record consistency, not external origin, signatures, hardware, or CI.
Even a perfectly consistent synthetic ensemble never grants operational ACT.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

SCHEMA="AETHER-231/integrated-adversarial-review-v1"
HEX40=re.compile(r"^[0-9a-f]{40}$")
HEX64=re.compile(r"^[0-9a-f]{64}$")
EXPECTED={
 "ci_provenance":("AETHER-226/github-run-provenance-v1","DOCUMENTARY_GITHUB_API_METADATA_CONSISTENT"),
 "archive":("AETHER-227/archive-inventory-v1","DOCUMENTARY_ARCHIVE_BYTES_CONSISTENT_ONLY"),
 "browser_parity":("AETHER-228/hosted-browser-parity-v1","DOCUMENTARY_HOSTED_BROWSER_BYTES_MATCH_ONLY"),
 "ancestry":("AETHER-229/ancestry-assessment-v1","DOCUMENTARY_DISTINCT_CONTROL_CLAIMS_ONLY"),
 "challenge":("AETHER-230/challenge-assessment-v1","DOCUMENTARY_CHALLENGE_LEDGER_CONSISTENT_ONLY")
}
HOLD={"independent_ci_execution_authenticated":False,
      "independent_external_custodians_authenticated":0,
      "external_challenge_consumption_authenticated":False,
      "original_physical_captures_authenticated":0,
      "physical_qualification_percent":0,
      "operational_authority":"HOLD","physical_act_allowed":False,
      "may_repair":False,"may_recover":False,"may_reclaim_lock":False,
      "may_choose_history":False}

def sha(raw:bytes)->str:
 return hashlib.sha256(raw).hexdigest()

def assess(bundle:dict)->dict:
 reasons:set[str]=set()
 if not isinstance(bundle,dict):bundle={}
 if bundle.get("schema")!=SCHEMA or bundle.get("phase")!="XIX" or bundle.get("bound")!="AETHER-231":
  reasons.add("INTEGRATED_REVIEW_SCHEMA_OR_PHASE_INVALID")
 if bundle.get("previous_phase_freeze")!="../224/decision.json":
  reasons.add("SEALED_PHASE_XVIII_ANCESTRY_MISSING")
 if bundle.get("previous_bound")!="../230/protocol.json":
  reasons.add("PRIOR_BOUND_LINK_INVALID")
 commit=bundle.get("source_commit")
 if not isinstance(commit,str) or HEX40.fullmatch(commit) is None:
  reasons.add("SOURCE_REVISION_UNPINNED")
 run_id=bundle.get("run_id")
 if type(run_id) is not int or run_id<1:
  reasons.add("RUN_ID_UNPINNED")
 observations=bundle.get("assessments")
 if not isinstance(observations,dict):observations={}
 for key,(schema,verdict) in EXPECTED.items():
  item=observations.get(key)
  if not isinstance(item,dict):
   reasons.add("REQUIRED_ASSESSMENT_ABSENT:"+key)
   continue
  if item.get("schema")!=schema:
   reasons.add("ASSESSMENT_SCHEMA_CONFLICT:"+key)
  if item.get("verdict")!=verdict:
   reasons.add("ASSESSMENT_UNQUALIFIED:"+key)
  if item.get("operational_authority")!="HOLD" or item.get("physical_act_allowed") is not False or item.get("physical_qualification_percent")!=0:
   reasons.add("ASSESSMENT_AUTHORITY_PROMOTION:"+key)
 for key,field in (("ci_provenance","expected_source_sha"),("archive","source_commit"),
                   ("browser_parity","source_commit")):
  item=observations.get(key,{})
  if not isinstance(item,dict) or item.get(field)!=commit:
   reasons.add("SOURCE_REVISION_CONFLICT:"+key)
 ci=observations.get("ci_provenance",{})
 parity=observations.get("browser_parity",{})
 if not isinstance(ci,dict) or ci.get("run_id")!=run_id:
  reasons.add("CI_RUN_ID_CONFLICT")
 if not isinstance(parity,dict) or parity.get("run_id")!=run_id:
  reasons.add("BROWSER_PARITY_RUN_ID_CONFLICT")
 if not isinstance(parity,dict) or not isinstance(parity.get("hosted_sha256"),str) or HEX64.fullmatch(parity["hosted_sha256"]) is None or parity.get("hosted_sha256")!=parity.get("browser_sha256"):
  reasons.add("HOSTED_BROWSER_DIGEST_PARITY_UNPROVEN")
 ancestry=observations.get("ancestry",{})
 if not isinstance(ancestry,dict) or ancestry.get("witness_records_received")!=3 or ancestry.get("declared_witness_roots")!=3:
  reasons.add("THREE_DECLARED_ANCESTRIES_MISSING")
 challenge=observations.get("challenge",{})
 if not isinstance(challenge,dict) or not isinstance(challenge.get("receipt_observed_sha256"),str) or not HEX64.fullmatch(challenge["receipt_observed_sha256"]):
  reasons.add("ORIGINAL_RECEIPT_BYTES_UNOBSERVED")
 if not isinstance(challenge,dict) or not isinstance(challenge.get("ledger_observed_sha256"),str) or not HEX64.fullmatch(challenge["ledger_observed_sha256"]):
  reasons.add("REPLAY_LEDGER_BYTES_UNOBSERVED")
 if bundle.get("operational_authority")!="HOLD" or bundle.get("physical_act_allowed") is not False:
  reasons.add("REQUESTED_AUTHORITY_PROMOTION")
 physical=bundle.get("original_physical_evidence")
 if physical is not None and physical!="UNVERIFIED":
  reasons.add("ORIGINAL_HARDWARE_AUTHENTICATION_UNSUPPORTED")
 # This tool cannot authenticate the roots of supplied records; even perfect
 # synthetic self-attestations remain documentary, never qualification.
 return {"schema":"AETHER-231/integrated-review-assessment-v1",
  "verdict":"DOCUMENTARY_ENSEMBLE_CONSISTENT_UNAUTHENTICATED" if not reasons else "REJECT_OR_UNVERIFIED",
  "reasons":sorted(reasons) if reasons else ["INDEPENDENT_SOURCE_AND_DEVICE_ORIGIN_NOT_AUTHENTICATED_BY_DOCUMENTARY_REVIEW"],
  "received_assessment_count":sum(isinstance(v,dict) for v in observations.values()),
  "source_commit":commit,"run_id":run_id,**HOLD}

def main()->int:
 p=argparse.ArgumentParser()
 p.add_argument("--bundle",type=Path,required=True)
 p.add_argument("--out",type=Path)
 args=p.parse_args()
 try: bundle=json.loads(args.bundle.read_text(encoding="utf-8"))
 except (OSError,UnicodeError,ValueError):bundle={}
 result=assess(bundle)
 output=json.dumps(result,indent=2,sort_keys=True)+"\n"
 if args.out:
  args.out.parent.mkdir(parents=True,exist_ok=True)
  args.out.write_text(output,encoding="utf-8")
 print(output,end="")
 return 0 if result["verdict"]=="DOCUMENTARY_ENSEMBLE_CONSISTENT_UNAUTHENTICATED" else 1

if __name__=="__main__":
 sys.exit(main())
