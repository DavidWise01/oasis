#!/usr/bin/env python3
"""AETHER-270-RS — compare signed, separately claimed checkpoint anchor readbacks.

Transport/source independence and key ownership are NOT authenticated by input labels.
No network access, no physical ACT, no externally authorized quorum.
"""
import argparse
import base64
import hashlib
import json
from pathlib import Path

SCHEMA="AETHER-270/anchor-readback-v1"
HOLD={"verdict":"REJECT_OR_UNVERIFIED","operational_authority":"HOLD",
      "physical_act_allowed":False,"physical_qualification_percent":0,
      "external_custody_authenticated":False,"independent_key_ownership_verified":False}

def canon(value):
    return json.dumps(value,sort_keys=True,separators=(",",":"),
                      allow_nan=False,ensure_ascii=True).encode("ascii")

def sha(value):
    return hashlib.sha256(canon(value)).hexdigest()

def is_hash(value):
    return isinstance(value,str) and len(value)==64 and all(x in "0123456789abcdef" for x in value)

def verify_key(pem,message,signature):
    try:
        from cryptography.hazmat.primitives import serialization
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
        from cryptography.exceptions import InvalidSignature
        key=serialization.load_pem_public_key(pem.encode("ascii"))
        if not isinstance(key,Ed25519PublicKey) or len(signature)!=64:return False
        key.verify(signature,message)
        return True
    except (ImportError,TypeError,ValueError,UnicodeError,InvalidSignature):
        return False

def parents_for(node,graph):
    visited=set()
    active=set()
    def visit(current):
        if not isinstance(current,str) or not current or len(current)>128:
            raise ValueError("ANCESTRY_NODE_INVALID")
        if current in active:raise ValueError("ANCESTRY_CYCLE")
        if current in visited:return
        if current not in graph:raise ValueError("ANCESTRY_NODE_MISSING")
        parents=graph[current]
        if not isinstance(parents,list) or len(parents)>16:
            raise ValueError("ANCESTRY_PARENTS_INVALID")
        active.add(current)
        visited.add(current)
        if len(visited)>256:raise ValueError("ANCESTRY_BOUNDS_EXCEEDED")
        for parent in parents:visit(parent)
        active.remove(current)
    visit(node)
    return visited

def checkpoint_ok(c):
    if not isinstance(c,dict) or set(c)!={"schema","count","receipts","snapshot_sha256"}:
        return False
    if c["schema"]!="AETHER-269/nonce-anchor-v1" or not isinstance(c["receipts"],list) or len(c["receipts"])>4096:
        return False
    if type(c["count"]) is not int or c["count"]!=len(c["receipts"]):
        return False
    if not is_hash(c["snapshot_sha256"]) or c["snapshot_sha256"]!=sha({k:v for k,v in c.items() if k!="snapshot_sha256"}):
        return False
    previous=None
    for r in c["receipts"]:
        if not isinstance(r,dict) or set(r)!={"nonce","challenge_sha256","issuance_sha256","receipt_sha256"}:
            return False
        nonce=r["nonce"]
        if not isinstance(nonce,str) or not nonce or len(nonce)>128 or (previous is not None and nonce<=previous):
            return False
        if not all(is_hash(r[k]) for k in ("challenge_sha256","issuance_sha256","receipt_sha256")):
            return False
        claim={"schema":"AETHER-268/pinned-issuance-nonce-v1","nonce":nonce,
               "challenge_sha256":r["challenge_sha256"],"issuance_sha256":r["issuance_sha256"]}
        if sha(claim)!=r["receipt_sha256"]:return False
        previous=nonce
    return True

def check(bundle,signature_verify=verify_key):
    reasons=[];observed={"readbacks":[]}
    if not isinstance(bundle,dict):
        return {**HOLD,"reasons":["BUNDLE_INVALID"],"observed":observed}
    pinned=bundle.get("prior_checkpoint")
    reads=bundle.get("readbacks")
    pins=bundle.get("public_key_pins")
    graph=bundle.get("controller_ancestry")
    if not checkpoint_ok(pinned):reasons.append("PRIOR_CHECKPOINT_INVALID")
    if not isinstance(reads,list) or len(reads)!=3:
        reasons.append("THREE_READBACKS_REQUIRED");reads=[]
    if not isinstance(pins,dict):reasons.append("PUBLIC_KEY_PINS_MISSING");pins={}
    if not isinstance(graph,dict):reasons.append("ANCESTRY_GRAPH_MISSING");graph={}
    source_ids=set();key_ids=set();readback_nonces=set();families=[];tips=[]
    for row in reads:
        expected={"source_id","controller_id","key_id","readback_nonce","checkpoint",
                  "retrieval_sha256","signed_receipt_b64"}
        if not isinstance(row,dict) or set(row)!=expected:
            reasons.append("READBACK_SCHEMA_INVALID");continue
        sid=row["source_id"];controller=row["controller_id"]
        key_id=row["key_id"];nonce=row["readback_nonce"]
        if not isinstance(sid,str) or not sid or sid in source_ids:
            reasons.append("SOURCE_ID_REPLAY")
        if isinstance(sid,str):source_ids.add(sid)
        if not isinstance(key_id,str) or not key_id or key_id in key_ids:
            reasons.append("SIGNER_KEY_REUSE")
        if isinstance(key_id,str):key_ids.add(key_id)
        if not isinstance(nonce,str) or not nonce or nonce in readback_nonces:
            reasons.append("READBACK_NONCE_REPLAY")
        if isinstance(nonce,str):readback_nonces.add(nonce)
        snap=row["checkpoint"]
        if not checkpoint_ok(snap):
            reasons.append("READBACK_CHECKPOINT_INVALID")
        else:
            tips.append(snap)
            if checkpoint_ok(pinned):
                if snap["count"]<pinned["count"]:
                    reasons.append("CHECKPOINT_ROLLBACK")
                prior_map={r["nonce"]:r for r in pinned["receipts"]}
                current_map={r["nonce"]:r for r in snap["receipts"]}
                for k,v in prior_map.items():
                    if k not in current_map:reasons.append("PINNED_NONCE_MISSING")
                    elif current_map[k]!=v:reasons.append("PINNED_NONCE_REWRITTEN")
        if not is_hash(row["retrieval_sha256"]):
            reasons.append("RETRIEVAL_DIGEST_INVALID")
        try:
            families.append(parents_for(controller,graph))
        except ValueError as exc:
            reasons.append(str(exc))
        statement={"schema":SCHEMA,"source_id":sid,"controller_id":controller,
                   "readback_nonce":nonce,"checkpoint_sha256":snap.get("snapshot_sha256") if isinstance(snap,dict) else None,
                   "retrieval_sha256":row["retrieval_sha256"]}
        pin=pins.get(key_id)
        if not isinstance(pin,dict) or pin.get("controller_id")!=controller or not isinstance(pin.get("public_key_pem"),str):
            reasons.append("PUBLIC_KEY_PIN_MISMATCH")
            valid=False
        else:
            try:
                signature=base64.b64decode(row["signed_receipt_b64"],validate=True)
                valid=bool(signature_verify(pin["public_key_pem"],canon(statement),signature))
            except (TypeError,ValueError,UnicodeError):
                valid=False
            if not valid:reasons.append("SIGNATURE_INVALID")
        observed["readbacks"].append({"source_id":sid,"signature_valid":valid,
                                      "checkpoint_sha256":statement["checkpoint_sha256"]})
    for i,a in enumerate(tips):
        for b in tips[i+1:]:
            if a["count"]==b["count"] and a["snapshot_sha256"]!=b["snapshot_sha256"]:
                reasons.append("SAME_COUNT_CONFLICTING_CHECKPOINTS")
            a_map={r["nonce"]:r for r in a["receipts"]}
            b_map={r["nonce"]:r for r in b["receipts"]}
            for nonce in set(a_map)&set(b_map):
                if a_map[nonce]!=b_map[nonce]:
                    reasons.append("CROSS_SOURCE_NONCE_CONFLICT")
    for i,family in enumerate(families):
        for other in families[i+1:]:
            if family & other:reasons.append("SHARED_CONTROLLER_ANCESTRY")
    if len(families)!=3:reasons.append("THREE_ANCESTRIES_UNPROVEN")
    reasons+=["RETRIEVAL_BYTES_NOT_INDEPENDENTLY_OBSERVED",
              "PINNED_PUBLIC_KEYS_NOT_EXTERNALLY_AUTHENTICATED",
              "CONTROLLER_ANCESTRY_NOT_EXTERNALLY_AUTHENTICATED",
              "EXTERNAL_MONOTONIC_ANCHOR_CUSTODY_UNVERIFIED"]
    return {**HOLD,"reasons":sorted(set(reasons)),"observed":observed}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--bundle",type=Path,required=True)
    p.add_argument("--out",type=Path)
    args=p.parse_args()
    try:
        raw=args.bundle.read_bytes()
        if len(raw)>2*1024*1024:raise ValueError("INPUT_TOO_LARGE")
        report=check(json.loads(raw))
    except (OSError,ValueError,TypeError,UnicodeError) as exc:
        report={**HOLD,"reasons":["INPUT_REJECTED:"+type(exc).__name__]}
    output=json.dumps(report,sort_keys=True,indent=2)+"\n"
    if args.out:
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(output,encoding="utf-8")
    print(output,end="")
    return 1

if __name__=="__main__":
    raise SystemExit(main())
