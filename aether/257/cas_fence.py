#!/usr/bin/env python3
"""AETHER-257-RS: read-only CAS transition consistency and split-brain fence.

Caller-provided records cannot establish external atomicity or independent custody.
"""
import argparse
import hashlib
import json
import re
from pathlib import Path

SCHEMA="AETHER-257/cas-split-brain-v1"
HOLD={"operational_authority":"HOLD","physical_qualification_percent":0,
      "physical_act_allowed":False,"external_atomicity_authenticated":False,
      "independent_witness_custody_authenticated":False}
SHA=re.compile(r"^[0-9a-f]{64}$")

def canonical(obj):
    return json.dumps(obj,sort_keys=True,separators=(",",":"),ensure_ascii=True,allow_nan=False).encode()

def sha(obj):
    return hashlib.sha256(canonical(obj)).hexdigest()

def assess(bundle):
    errors=[]
    observed={"transitions":[]}
    if not isinstance(bundle,dict):
        return {"schema":SCHEMA,"verdict":"REJECT_OR_UNVERIFIED",
                "reasons":["BUNDLE_INVALID"],"observed":observed,**HOLD}
    anchor=bundle.get("externally_claimed_anchor")
    transitions=bundle.get("transitions")
    witnesses=bundle.get("witnesses")
    if not isinstance(anchor,dict) or set(anchor)!={"sequence","head_sha256"} or (
        type(anchor.get("sequence")) is not int or anchor["sequence"]<0 or
        not isinstance(anchor.get("head_sha256"),str) or not SHA.fullmatch(anchor["head_sha256"])):
        errors.append("ANCHOR_INVALID")
        anchor={"sequence":0,"head_sha256":"0"*64}
    if not isinstance(transitions,list) or not 1<=len(transitions)<=128:
        errors.append("TRANSITIONS_INVALID")
        transitions=[]
    expected={"attempt_id","host_id","challenge_id","nonce","expected_sequence",
              "expected_head_sha256","decision","new_sequence","new_head_sha256",
              "decision_record_sha256"}
    current_seq=anchor["sequence"]
    current_head=anchor["head_sha256"]
    accepted_nonces=set()
    accepted_challenges=set()
    attempts=set()
    for t in transitions:
        if not isinstance(t,dict) or set(t)!=expected:
            errors.append("TRANSITION_SCHEMA_INVALID")
            continue
        ids=("attempt_id","host_id","challenge_id","nonce")
        if any(not isinstance(t[k],str) or not t[k] or len(t[k])>128 for k in ids):
            errors.append("TRANSITION_ID_INVALID")
        if t["attempt_id"] in attempts:
            errors.append("DUPLICATE_ATTEMPT_ID")
        attempts.add(t["attempt_id"])
        if type(t["expected_sequence"]) is not int or type(t["new_sequence"]) is not int:
            errors.append("SEQUENCE_TYPE_INVALID")
        if any(not isinstance(t[k],str) or not SHA.fullmatch(t[k]) for k in ("expected_head_sha256","new_head_sha256")):
            errors.append("TRANSITION_HEAD_INVALID")
        if t["decision"] not in ("ACCEPTED","STALE_REJECTED"):
            errors.append("DECISION_INVALID")
        record_hash=sha({k:v for k,v in t.items() if k!="decision_record_sha256"})
        if record_hash!=t["decision_record_sha256"]:
            errors.append("DECISION_RECORD_TAMPERED")
        if t["decision"]=="ACCEPTED":
            if (t["expected_sequence"]!=current_seq or t["expected_head_sha256"]!=current_head):
                errors.append("ACCEPTED_STALE_HEAD_OR_SPLIT_BRAIN")
            if t["new_sequence"]!=current_seq+1:
                errors.append("ACCEPTED_SEQUENCE_NOT_MONOTONIC")
            if t["new_head_sha256"]==current_head:
                errors.append("ACCEPTED_HEAD_NOT_ADVANCED")
            if t["nonce"] in accepted_nonces:
                errors.append("DOUBLE_CONSUMED_NONCE")
            if t["challenge_id"] in accepted_challenges:
                errors.append("DOUBLE_CONSUMED_CHALLENGE")
            accepted_nonces.add(t["nonce"])
            accepted_challenges.add(t["challenge_id"])
            current_seq=t["new_sequence"] if type(t["new_sequence"]) is int else current_seq
            current_head=t["new_head_sha256"] if isinstance(t["new_head_sha256"],str) else current_head
        elif t["decision"]=="STALE_REJECTED":
            if (t["expected_sequence"]==current_seq and t["expected_head_sha256"]==current_head):
                errors.append("UNJUSTIFIED_STALE_REJECTION")
            if t["new_sequence"]!=current_seq or t["new_head_sha256"]!=current_head:
                errors.append("REJECTED_ATTEMPT_MUTATED_HEAD")
        observed["transitions"].append({"attempt_id":t["attempt_id"],"decision":t["decision"],
                                        "record_sha256":record_hash})
    observed["computed_sequence"]=current_seq
    observed["computed_head_sha256"]=current_head
    if not isinstance(witnesses,list) or len(witnesses)!=3:
        errors.append("THREE_WITNESSES_REQUIRED")
        witnesses=[]
    roots=set()
    expected_digest=sha({"anchor":anchor,"transitions":transitions})
    for witness in witnesses:
        if not isinstance(witness,dict) or set(witness)!={"controller_claim","journal_sha256","observed_head_sha256"}:
            errors.append("WITNESS_SCHEMA_INVALID")
            continue
        root=witness["controller_claim"]
        if not isinstance(root,str) or not root or root in roots:
            errors.append("WITNESS_CONTROLLER_DUPLICATE_OR_INVALID")
        if isinstance(root,str):roots.add(root)
        if witness["journal_sha256"]!=expected_digest:
            errors.append("WITNESS_JOURNAL_MISMATCH")
        if witness["observed_head_sha256"]!=current_head:
            errors.append("WITNESS_FINAL_HEAD_MISMATCH")
    if len(roots)<3:errors.append("THREE_CONTROLLER_LABELS_MISSING")
    errors+=["NO_EXTERNAL_COMPARE_AND_SWAP_ATOMICITY_PROOF",
             "NO_INDEPENDENT_WITNESS_ANCESTRY_OR_SIGNATURE_PROOF",
             "NO_EXTERNALLY_RETAINED_NONCE_CONSUMPTION"]
    return {"schema":SCHEMA,"verdict":"REJECT_OR_UNVERIFIED",
            "reasons":sorted(set(errors)),"observed":observed,**HOLD}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--bundle",type=Path,required=True)
    parser.add_argument("--out",type=Path)
    args=parser.parse_args()
    try:
        raw=args.bundle.read_bytes()
        if len(raw)>512*1024:raise ValueError("INPUT_TOO_LARGE")
        result=assess(json.loads(raw))
    except (OSError,ValueError,TypeError,UnicodeError) as error:
        result={"schema":SCHEMA,"verdict":"REJECT_OR_UNVERIFIED",
                "reasons":["INPUT_REJECTED:"+type(error).__name__],**HOLD}
    rendered=json.dumps(result,sort_keys=True,indent=2)+"\n"
    if args.out:
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(rendered,encoding="utf-8")
    print(rendered,end="")
    return 1

if __name__=="__main__":
    raise SystemExit(main())
