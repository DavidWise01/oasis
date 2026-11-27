#!/usr/bin/env python3
"""AETHER-253-RS: monotone externally claimed ledger heads and process-exit fencing.

No process signaling, process killing, lock reclamation or authority promotion.
"""
import argparse
import base64
import hashlib
import json
import re
from pathlib import Path

SCHEMA="AETHER-253/exit-ledger-v1"
HOLD={"operational_authority":"HOLD","physical_qualification_percent":0,
      "physical_act_allowed":False,"exit_authority":False,
      "external_ledger_anchor_authenticated":False}
HEX64=re.compile("^[0-9a-f]{64}$")
def canonical(obj):
    return json.dumps(obj,sort_keys=True,separators=(",",":"),ensure_ascii=True,allow_nan=False).encode()
def digest(obj):
    return hashlib.sha256(canonical(obj)).hexdigest()
def verify_ed25519(pem,data,signature):
    try:
        from cryptography.exceptions import InvalidSignature
        from cryptography.hazmat.primitives import serialization
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
        key=serialization.load_pem_public_key(pem.encode("ascii"))
        if not isinstance(key,Ed25519PublicKey) or len(signature)!=64:return False
        key.verify(signature,data)
        return True
    except (ImportError,InvalidSignature,ValueError,TypeError,UnicodeError):return False
def identity_ok(i):
    return (isinstance(i,dict) and set(i)=={"pid","start_ticks","boot_id","netns_inode"}
            and type(i["pid"]) is int and i["pid"]>0 and type(i["start_ticks"]) is int
            and i["start_ticks"]>=0 and type(i["netns_inode"]) is int and i["netns_inode"]>0
            and isinstance(i["boot_id"],str) and re.fullmatch("[0-9a-f-]{36}",i["boot_id"]) is not None)
def assess(bundle):
    reasons=[];observed={"signed_receipts":[],"transition_heads":[]}
    if not isinstance(bundle,dict):
        return {"schema":SCHEMA,"verdict":"REJECT_OR_UNVERIFIED","reasons":["BUNDLE_INVALID"],"observed":observed,**HOLD}
    initial=bundle.get("externally_claimed_anchor")
    events=bundle.get("ledger_events")
    process=bundle.get("process_evidence")
    receipts=bundle.get("witness_receipts")
    pins=bundle.get("public_key_pins")
    if not isinstance(initial,dict) or set(initial)!={"sequence","head_sha256"} or type(initial.get("sequence")) is not int or initial["sequence"]<0 or not isinstance(initial.get("head_sha256"),str) or not HEX64.fullmatch(initial["head_sha256"]):
        reasons.append("ANCHOR_INVALID")
        initial={"sequence":0,"head_sha256":"0"*64}
    if not isinstance(events,list) or not 1<=len(events)<=128:
        reasons.append("EVENT_SET_INVALID");events=[]
    last_seq=initial["sequence"]
    head=initial["head_sha256"]
    consumed=set()
    for event in events:
        if not isinstance(event,dict) or set(event)!={"sequence","previous_sha256","challenge_id","nonce","run_id","identity_sha256","state","event_sha256"}:
            reasons.append("EVENT_SCHEMA_INVALID");break
        if type(event["sequence"]) is not int or event["sequence"]!=last_seq+1:
            reasons.append("NON_MONOTONIC_SEQUENCE")
        last_seq=event["sequence"] if type(event["sequence"]) is int else last_seq
        if event["previous_sha256"]!=head:reasons.append("ANCHOR_OR_PREVIOUS_HEAD_MISMATCH")
        if event["state"] not in ("OBSERVED","EXIT_UNCERTAIN","EXIT_CORROBORATED"):
            reasons.append("STATE_INVALID")
        nonce=event["nonce"]
        if not isinstance(nonce,str) or not nonce or len(nonce)>128 or nonce in consumed:
            reasons.append("NONCE_REPLAY")
        if isinstance(nonce,str):consumed.add(nonce)
        if type(event["run_id"]) is not int or event["run_id"]<=0 or not isinstance(event["challenge_id"],str) or not event["challenge_id"]:
            reasons.append("CHALLENGE_OR_RUN_INVALID")
        if not isinstance(event["identity_sha256"],str) or not HEX64.fullmatch(event["identity_sha256"]):
            reasons.append("IDENTITY_HASH_INVALID")
        computed=digest({k:v for k,v in event.items() if k!="event_sha256"})
        if event["event_sha256"]!=computed:reasons.append("EVENT_DIGEST_MISMATCH")
        head=computed
        observed["transition_heads"].append(head)
    if not isinstance(process,dict) or set(process)!={"identity","samples","wait_status"}:
        reasons.append("PROCESS_EVIDENCE_MISSING");process={}
    identity=process.get("identity")
    if not identity_ok(identity):reasons.append("PROCESS_IDENTITY_INVALID")
    samples=process.get("samples")
    if not isinstance(samples,list) or len(samples)!=2:
        reasons.append("TWO_SAMPLES_REQUIRED");samples=[]
    else:
        for sample in samples:
            if not isinstance(sample,dict) or set(sample)!={"state","observed_identity"}:
                reasons.append("PROCESS_SAMPLE_INVALID");continue
            if sample["state"] not in ("MATCHED","MISSING","DIFFERENT"):
                reasons.append("PROCESS_SAMPLE_STATE_INVALID")
            if sample["state"]=="MATCHED" and sample["observed_identity"]!=identity:
                reasons.append("PROCESS_IDENTITY_REUSED_OR_MISMATCHED")
            if sample["state"]=="DIFFERENT":
                reasons.append("PID_REUSE_OBSERVED")
        if samples[0].get("state")=="MISSING" or samples[1].get("state")=="MISSING":
            reasons.append("DISAPPEARANCE_NOT_PROOF_OF_EXIT")
    wait=process.get("wait_status")
    if not isinstance(wait,dict) or set(wait)!={"direct_child","pidfd_wait_confirmed","exit_code"}:
        reasons.append("WAIT_STATUS_INVALID")
    elif not (wait["direct_child"] is True and wait["pidfd_wait_confirmed"] is True and
              type(wait["exit_code"]) is int):
        reasons.append("PROCESS_EXIT_NOT_OS_CORROBORATED")
    if events and identity_ok(identity) and events[-1]["identity_sha256"]!=digest(identity):
        reasons.append("EVENT_PROCESS_IDENTITY_MISMATCH")
    if events and events[-1]["state"]=="EXIT_CORROBORATED" and (
        not isinstance(wait,dict) or wait.get("direct_child") is not True or
        wait.get("pidfd_wait_confirmed") is not True or type(wait.get("exit_code")) is not int):
        reasons.append("FALSE_CORROBORATED_EXIT_CLAIM")
    if not isinstance(receipts,list) or len(receipts)!=3:
        reasons.append("THREE_WITNESS_RECEIPTS_REQUIRED");receipts=[]
    if not isinstance(pins,dict):reasons.append("PUBLIC_KEY_PINS_MISSING");pins={}
    statement={"schema":SCHEMA,"anchor_sha256":initial["head_sha256"],
               "final_head_sha256":head,"process_evidence_sha256":digest(process)}
    roots=set();keys=set()
    for r in receipts:
        if not isinstance(r,dict) or set(r)!={"key_id","controller_root","signature_b64"}:
            reasons.append("RECEIPT_INVALID");continue
        kid=r["key_id"];root=r["controller_root"]
        if not isinstance(kid,str) or not kid or kid in keys:
            reasons.append("DUPLICATE_OR_INVALID_KEY");continue
        keys.add(kid)
        if not isinstance(root,str) or not root or root in roots:reasons.append("DUPLICATE_OR_INVALID_ROOT")
        if isinstance(root,str):roots.add(root)
        pin=pins.get(kid)
        if not isinstance(pin,dict) or pin.get("controller_root")!=root or not isinstance(pin.get("public_key_pem"),str):
            reasons.append("KEY_PIN_UNAVAILABLE");continue
        try:
            signature=base64.b64decode(r["signature_b64"],validate=True)
            valid=verify_ed25519(pin["public_key_pem"],canonical(statement),signature)
        except (ValueError,TypeError):valid=False
        if not valid:reasons.append("SIGNATURE_INVALID")
        observed["signed_receipts"].append({"key_id":kid,"root_claim":root,"signature_valid":valid})
    if len(roots)!=3:reasons.append("THREE_DISTINCT_ROOT_LABELS_REQUIRED")
    reasons.extend(["EXTERNAL_ANCHOR_CUSTODY_UNAUTHENTICATED",
                    "PIDFD_AND_PROCESS_EXIT_NOT_LIVE_ATTESTED",
                    "WITNESS_CONTROLLER_ANCESTRY_NOT_INDEPENDENTLY_PROVEN"])
    return {"schema":SCHEMA,"verdict":"REJECT_OR_UNVERIFIED",
            "reasons":sorted(set(reasons)),"observed":observed,**HOLD}
def main():
    parser=argparse.ArgumentParser();parser.add_argument("--bundle",type=Path,required=True)
    parser.add_argument("--out",type=Path);args=parser.parse_args()
    try:
        data=args.bundle.read_bytes()
        if len(data)>512*1024:raise ValueError("INPUT_TOO_LARGE")
        result=assess(json.loads(data))
    except (OSError,ValueError,TypeError) as error:
        result={"schema":SCHEMA,"verdict":"REJECT_OR_UNVERIFIED",
                "reasons":["INPUT_INVALID:"+type(error).__name__],**HOLD}
    output=json.dumps(result,sort_keys=True,indent=2)+"\n"
    if args.out:args.out.write_text(output,encoding="utf-8")
    print(output,end="");return 1
if __name__=="__main__":raise SystemExit(main())
