#!/usr/bin/env python3
"""AETHER-263-RS: compare externally claimed checkpoint readbacks, fail closed."""
import argparse,base64,hashlib,json,re
from pathlib import Path

SCHEMA="AETHER-263/readback-v1"
HOLD={"verdict":"REJECT_OR_UNVERIFIED","operational_authority":"HOLD",
      "physical_act_allowed":False,"physical_qualification_percent":0,
      "external_custody_authenticated":False,"independent_ancestry_authenticated":False}
HEX64=re.compile(r"^[0-9a-f]{64}$")
def canonical(x):
    return json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=True,allow_nan=False).encode()
def sha(x):return hashlib.sha256(canonical(x)).hexdigest()
def verify(pem,message,sig):
    try:
        from cryptography.exceptions import InvalidSignature
        from cryptography.hazmat.primitives import serialization
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
        key=serialization.load_pem_public_key(pem.encode("ascii"))
        if not isinstance(key,Ed25519PublicKey) or len(sig)!=64:return False
        key.verify(sig,message);return True
    except (ImportError,InvalidSignature,ValueError,TypeError,UnicodeError):return False
def ancestry(start,graph):
    visited=set();active=set()
    def walk(node):
        if not isinstance(node,str) or not node or len(node)>128:raise ValueError("ANCESTRY_ID_INVALID")
        if node in active:raise ValueError("ANCESTRY_CYCLE")
        if node in visited:return
        if node not in graph:raise ValueError("ANCESTRY_MISSING")
        parents=graph[node]
        if not isinstance(parents,list) or len(parents)>16:raise ValueError("ANCESTRY_PARENTS_INVALID")
        visited.add(node);active.add(node)
        if len(visited)>256:raise ValueError("ANCESTRY_TOO_LARGE")
        for p in parents:walk(p)
        active.remove(node)
    walk(start)
    return visited
def valid_checkpoint(c):
    if not isinstance(c,dict) or set(c)!={"sequence","previous_sha256","nonce_sha256","nonce_count","checkpoint_sha256"}:return False
    if any(type(c[k]) is not int or c[k]<0 for k in ("sequence","nonce_count")):return False
    if any(not isinstance(c[k],str) or not HEX64.fullmatch(c[k]) for k in ("previous_sha256","nonce_sha256","checkpoint_sha256")):return False
    return c["checkpoint_sha256"]==sha({k:v for k,v in c.items() if k!="checkpoint_sha256"})
def assess(bundle,signature_verify=verify):
    reasons=[];observed={"readbacks":[]}
    if not isinstance(bundle,dict):return {**HOLD,"reasons":["BUNDLE_INVALID"],"observed":observed}
    anchor=bundle.get("externally_claimed_anchor")
    readings=bundle.get("readbacks")
    keys=bundle.get("public_key_pins")
    graph=bundle.get("controller_ancestry")
    if not valid_checkpoint(anchor):
        reasons.append("ANCHOR_INVALID");anchor=None
    if not isinstance(readings,list) or len(readings)!=3:
        reasons.append("THREE_READBACKS_REQUIRED");readings=[]
    if not isinstance(keys,dict):reasons.append("PUBLIC_KEYS_INVALID");keys={}
    if not isinstance(graph,dict):reasons.append("CONTROLLER_GRAPH_INVALID");graph={}
    key_ids=set();sources=set();families=[];checkpoints=[]
    for item in readings:
        if not isinstance(item,dict) or set(item)!={"source_id","key_id","controller_id","checkpoint","claimed_history","signature_b64"}:
            reasons.append("READBACK_SCHEMA_INVALID");continue
        source=item["source_id"];kid=item["key_id"];controller=item["controller_id"]
        if not isinstance(source,str) or not source or source in sources:
            reasons.append("SOURCE_DUPLICATE_OR_INVALID")
        if isinstance(source,str):sources.add(source)
        if not isinstance(kid,str) or not kid or kid in key_ids:
            reasons.append("KEY_DUPLICATE_OR_INVALID")
        if isinstance(kid,str):key_ids.add(kid)
        try:families.append(ancestry(controller,graph))
        except ValueError as err:reasons.append(str(err))
        checkpoint=item["checkpoint"]
        if not valid_checkpoint(checkpoint):
            reasons.append("READBACK_CHECKPOINT_INVALID")
        else:
            checkpoints.append(checkpoint)
            if anchor is not None and checkpoint["sequence"]<anchor["sequence"]:
                reasons.append("EXTERNAL_ROLLBACK_CLAIM")
            if anchor is not None and checkpoint["sequence"]==anchor["sequence"] and checkpoint["checkpoint_sha256"]!=anchor["checkpoint_sha256"]:
                reasons.append("ANCHOR_FORK")
        history=item["claimed_history"]
        if not isinstance(history,list) or len(history)>128 or not history:
            reasons.append("HISTORY_INVALID")
        else:
            if any(not valid_checkpoint(h) for h in history):reasons.append("HISTORY_CHECKPOINT_INVALID")
            for i in range(1,len(history)):
                old,new=history[i-1],history[i]
                if not isinstance(old,dict) or not isinstance(new,dict):continue
                if new.get("sequence")!=old.get("sequence",-1)+1 or new.get("previous_sha256")!=old.get("checkpoint_sha256"):
                    reasons.append("HISTORY_CHAIN_BROKEN")
            if anchor is not None:
                matches=[x for x in history if isinstance(x,dict) and x.get("sequence")==anchor["sequence"]]
                if not matches or matches[0]!=anchor:reasons.append("ANCHOR_NOT_IN_HISTORY")
            if isinstance(checkpoint,dict) and history[-1]!=checkpoint:reasons.append("READBACK_TIP_NOT_HISTORY_TIP")
        signed={"schema":SCHEMA,"source_id":source,"controller_id":controller,
                "checkpoint_sha256":checkpoint.get("checkpoint_sha256") if isinstance(checkpoint,dict) else None,
                "history_sha256":sha(history)}
        pin=keys.get(kid)
        if not isinstance(pin,dict) or pin.get("controller_id")!=controller or not isinstance(pin.get("public_key_pem"),str):
            reasons.append("PIN_MISSING_OR_SUBSTITUTED");verified=False
        else:
            try:
                signature=base64.b64decode(item["signature_b64"],validate=True)
                verified=bool(signature_verify(pin["public_key_pem"],canonical(signed),signature))
            except (TypeError,ValueError,UnicodeError):verified=False
            if not verified:reasons.append("SIGNATURE_INVALID")
        observed["readbacks"].append({"source_id":source,"signature_valid":verified,
                                      "checkpoint_sha256":signed["checkpoint_sha256"]})
    for i,c in enumerate(checkpoints):
        for d in checkpoints[i+1:]:
            if c["sequence"]==d["sequence"] and c["checkpoint_sha256"]!=d["checkpoint_sha256"]:
                reasons.append("SAME_SEQUENCE_SPLIT_BRAIN")
    for i,f in enumerate(families):
        for other in families[i+1:]:
            if f&other:reasons.append("SHARED_CONTROLLER_ANCESTRY")
    if len(families)!=3:reasons.append("THREE_VALID_ANCESTRIES_MISSING")
    reasons+=["NO_INDEPENDENT_READBACK_ACQUISITION_PROOF",
              "NO_EXTERNALLY_AUTHENTICATED_CONTROLLER_LINEAGE",
              "NO_EXTERNAL_ROLLBACK_RESISTANT_STORAGE_PROOF"]
    return {**HOLD,"reasons":sorted(set(reasons)),"observed":observed}
def main():
    p=argparse.ArgumentParser();p.add_argument("--bundle",type=Path,required=True);p.add_argument("--out",type=Path)
    args=p.parse_args()
    try:
        raw=args.bundle.read_bytes()
        if len(raw)>2*1024*1024:raise ValueError("INPUT_TOO_LARGE")
        report=assess(json.loads(raw))
    except (OSError,ValueError,TypeError,UnicodeError) as e:report={**HOLD,"reasons":["INPUT_INVALID:"+type(e).__name__]}
    output=json.dumps(report,indent=2,sort_keys=True)+"\n"
    if args.out:args.out.write_text(output,encoding="utf-8")
    print(output,end="");return 1
if __name__=="__main__":raise SystemExit(main())
