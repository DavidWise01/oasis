#!/usr/bin/env python3
"""AETHER-262-RS: signed nonce checkpoint continuity and ancestry HOLD gate."""
import argparse
import base64
import hashlib
import json
import re
from pathlib import Path

SCHEMA="AETHER-262/checkpoint-v1"
HOLD={"verdict":"REJECT_OR_UNVERIFIED","operational_authority":"HOLD",
      "physical_act_allowed":False,"physical_qualification_percent":0,
      "external_custody_authenticated":False,"independent_ancestry_authenticated":False}
HEX64=re.compile(r"^[0-9a-f]{64}$")

def canonical(x):
    return json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=True,allow_nan=False).encode()

def digest(x):
    return hashlib.sha256(canonical(x)).hexdigest()

def signature_ok(pem,msg,sig):
    try:
        from cryptography.exceptions import InvalidSignature
        from cryptography.hazmat.primitives import serialization
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
        key=serialization.load_pem_public_key(pem.encode("ascii"))
        if not isinstance(key,Ed25519PublicKey) or len(sig)!=64:return False
        key.verify(sig,msg)
        return True
    except (ImportError,InvalidSignature,ValueError,TypeError,UnicodeError):
        return False

def roots(start,graph):
    visited=set();stack=set()
    def visit(node):
        if not isinstance(node,str) or not node or len(node)>128:raise ValueError("ANCESTRY_NODE_INVALID")
        if node in stack:raise ValueError("ANCESTRY_CYCLE")
        if node in visited:return
        if node not in graph:raise ValueError("ANCESTRY_MISSING")
        parents=graph[node]
        if not isinstance(parents,list) or len(parents)>16:raise ValueError("ANCESTRY_PARENTS_INVALID")
        visited.add(node);stack.add(node)
        if len(visited)>256:raise ValueError("ANCESTRY_TOO_LARGE")
        for parent in parents:visit(parent)
        stack.remove(node)
    visit(start)
    return visited

def assess(bundle,verify=signature_ok):
    reasons=[];observed={"signatures":[]}
    if not isinstance(bundle,dict):
        return {**HOLD,"reasons":["BUNDLE_INVALID"],"observed":observed}
    before=bundle.get("previous_checkpoint")
    after=bundle.get("next_checkpoint")
    witnesses=bundle.get("witnesses")
    pins=bundle.get("public_key_pins")
    graph=bundle.get("controller_ancestry")
    required={"sequence","previous_sha256","nonce_sha256","nonce_count","checkpoint_sha256"}
    for label,checkpoint in (("BEFORE",before),("AFTER",after)):
        if not isinstance(checkpoint,dict) or set(checkpoint)!=required:
            reasons.append(label+"_CHECKPOINT_SCHEMA_INVALID");continue
        if (type(checkpoint["sequence"]) is not int or checkpoint["sequence"]<0 or
            type(checkpoint["nonce_count"]) is not int or checkpoint["nonce_count"]<0):
            reasons.append(label+"_COUNTER_INVALID")
        if any(not isinstance(checkpoint[k],str) or not HEX64.fullmatch(checkpoint[k]) for k in
               ("previous_sha256","nonce_sha256","checkpoint_sha256")):
            reasons.append(label+"_HASH_FORMAT_INVALID")
        computed=digest({k:v for k,v in checkpoint.items() if k!="checkpoint_sha256"})
        if checkpoint["checkpoint_sha256"]!=computed:
            reasons.append(label+"_CHECKPOINT_TAMPER")
    consumption=bundle.get("new_consumptions")
    if not isinstance(consumption,list) or len(consumption)>128:
        reasons.append("CONSUMPTIONS_INVALID");consumption=[]
    seen=set()
    previous_nonce=before.get("nonce_sha256") if isinstance(before,dict) else None
    for index,item in enumerate(consumption):
        if not isinstance(item,dict) or set(item)!={"nonce","run_id","challenge_id","previous_nonce_sha256","nonce_sha256"}:
            reasons.append("CONSUMPTION_SCHEMA_INVALID");break
        nonce=item["nonce"]
        if not isinstance(nonce,str) or not nonce or len(nonce)>128 or nonce in seen:
            reasons.append("NONCE_REPLAY")
        if isinstance(nonce,str):seen.add(nonce)
        if type(item["run_id"]) is not int or item["run_id"]<=0 or not isinstance(item["challenge_id"],str) or not item["challenge_id"]:
            reasons.append("CONSUMPTION_BINDING_INVALID")
        if item["previous_nonce_sha256"]!=previous_nonce:
            reasons.append("NONCE_HASH_CHAIN_BROKEN")
        computed=digest({k:v for k,v in item.items() if k!="nonce_sha256"})
        if item["nonce_sha256"]!=computed:
            reasons.append("CONSUMPTION_HASH_TAMPER")
        previous_nonce=computed
    if isinstance(before,dict) and isinstance(after,dict) and set(before)==required and set(after)==required:
        if after["previous_sha256"]!=before["checkpoint_sha256"]:
            reasons.append("CHECKPOINT_PARENT_MISMATCH")
        if after["sequence"]!=before["sequence"]+1:
            reasons.append("CHECKPOINT_SEQUENCE_NOT_MONOTONIC")
        if after["nonce_count"]!=before["nonce_count"]+len(consumption):
            reasons.append("NONCE_COUNTER_MISMATCH")
        if after["nonce_sha256"]!=previous_nonce:
            reasons.append("NONCE_CHECKPOINT_MISMATCH")
    statement={"schema":SCHEMA,"before_sha256":before.get("checkpoint_sha256") if isinstance(before,dict) else None,
               "after_sha256":after.get("checkpoint_sha256") if isinstance(after,dict) else None}
    observed["statement_sha256"]=digest(statement)
    if not isinstance(witnesses,list) or len(witnesses)!=3:
        reasons.append("THREE_WITNESSES_REQUIRED");witnesses=[]
    if not isinstance(pins,dict):reasons.append("KEY_PINS_MISSING");pins={}
    if not isinstance(graph,dict):reasons.append("ANCESTRY_GRAPH_MISSING");graph={}
    keys=set();family=[]
    for receipt in witnesses:
        if not isinstance(receipt,dict) or set(receipt)!={"key_id","controller_id","signature_b64"}:
            reasons.append("RECEIPT_SCHEMA_INVALID");continue
        kid=receipt["key_id"];controller=receipt["controller_id"]
        if not isinstance(kid,str) or not kid or kid in keys:
            reasons.append("WITNESS_KEY_DUPLICATE");continue
        keys.add(kid)
        try:
            ancestry=roots(controller,graph)
            family.append(ancestry)
        except ValueError as exc:reasons.append(str(exc))
        pin=pins.get(kid)
        if not isinstance(pin,dict) or pin.get("controller_id")!=controller or not isinstance(pin.get("public_key_pem"),str):
            reasons.append("PIN_MISSING_OR_MISMATCHED");continue
        signed={**statement,"controller_id":controller}
        try:
            signature=base64.b64decode(receipt["signature_b64"],validate=True)
            valid=bool(verify(pin["public_key_pem"],canonical(signed),signature))
        except (TypeError,ValueError,UnicodeError):valid=False
        if not valid:reasons.append("SIGNATURE_INVALID")
        observed["signatures"].append({"key_id":kid,"controller_id":controller,"signature_valid":valid})
    for index,first in enumerate(family):
        for second in family[index+1:]:
            if first & second:reasons.append("SHARED_WITNESS_ANCESTRY")
    if len(family)!=3:reasons.append("THREE_ANCESTRIES_MISSING")
    reasons+=["EXTERNAL_CHECKPOINT_CUSTODY_UNVERIFIED",
              "PUBLIC_KEY_AND_CONTROLLER_ANCESTRY_UNAUTHENTICATED",
              "NONCE_CONSUMPTION_NOT_EXTERNALLY_ATOMIC"]
    return {**HOLD,"reasons":sorted(set(reasons)),"observed":observed}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--bundle",type=Path,required=True)
    p.add_argument("--out",type=Path)
    args=p.parse_args()
    try:
        raw=args.bundle.read_bytes()
        if len(raw)>1024*1024:raise ValueError("INPUT_TOO_LARGE")
        result=assess(json.loads(raw))
    except (OSError,ValueError,TypeError,UnicodeError) as exc:
        result={**HOLD,"reasons":["INPUT_REJECTED:"+type(exc).__name__]}
    rendered=json.dumps(result,indent=2,sort_keys=True)+"\n"
    if args.out:
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(rendered,encoding="utf-8")
    print(rendered,end="")
    return 1
if __name__=="__main__":
    raise SystemExit(main())
