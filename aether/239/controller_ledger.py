#!/usr/bin/env python3
"""AETHER-239-RS: read-only witness ancestry and nonce-ledger review.

Hashes are reconstructed, never authority. Evidence supplied by one caller is
not independent custody. No repair, physical action or mutable nonce consumption.
"""
import argparse
import hashlib
import json
import re
from pathlib import Path

SCHEMA="AETHER-239/controller-ledger-v1"
HEX64=re.compile(r"^[a-f0-9]{64}$")
HOLD={"operational_authority":"HOLD","physical_qualification_percent":0,
      "physical_act_allowed":False,"independent_custody_authenticated":False}

def canonical(o):
    return json.dumps(o,sort_keys=True,separators=(",",":"),ensure_ascii=True,allow_nan=False).encode()

def digest(o):
    return hashlib.sha256(canonical(o)).hexdigest()

def ancestry(key,graph):
    seen=set()
    active=set()
    def visit(node):
        if node in active:raise ValueError("ANCESTRY_CYCLE")
        if node in seen:return
        if node not in graph:raise ValueError("ANCESTRY_NODE_MISSING")
        parents=graph[node]
        if not isinstance(parents,list) or len(parents)>16:raise ValueError("ANCESTRY_PARENTS_INVALID")
        active.add(node)
        seen.add(node)
        for parent in parents:
            if not isinstance(parent,str) or not parent or len(parent)>128:raise ValueError("ANCESTRY_PARENT_INVALID")
            visit(parent)
        active.remove(node)
        if len(seen)>256:raise ValueError("ANCESTRY_LIMIT")
    visit(key)
    return seen

def check(document):
    reasons=[]
    observed={"chain":[],"witnesses":[]}
    if not isinstance(document,dict):
        return {"schema":SCHEMA,"verdict":"REJECT_OR_UNVERIFIED",
                "reasons":["DOCUMENT_INVALID"],"observed":observed,**HOLD}
    graph=document.get("controller_graph")
    witnesses=document.get("witnesses")
    ledger=document.get("ledger")
    expected_head=document.get("externally_pinned_head")
    if not isinstance(graph,dict) or not isinstance(witnesses,list) or not isinstance(ledger,list):
        return {"schema":SCHEMA,"verdict":"REJECT_OR_UNVERIFIED",
                "reasons":["REQUIRED_STRUCTURE_MISSING"],"observed":observed,**HOLD}
    if len(witnesses)!=3:reasons.append("EXACT_THREE_WITNESSES_REQUIRED")
    if len(ledger)>256:reasons.append("LEDGER_TOO_LONG")
    roots=[]
    keys=set()
    for w in witnesses[:16]:
        if not isinstance(w,dict) or set(w)!={"key_id","root_id","receipt_digest"}:
            reasons.append("WITNESS_RECORD_INVALID")
            continue
        key=w["key_id"]
        root=w["root_id"]
        if not isinstance(key,str) or not isinstance(root,str) or not key or not root:
            reasons.append("WITNESS_ID_INVALID")
            continue
        if key in keys:reasons.append("DUPLICATE_WITNESS_KEY")
        keys.add(key)
        if not isinstance(w["receipt_digest"],str) or not HEX64.fullmatch(w["receipt_digest"]):
            reasons.append("RECEIPT_DIGEST_INVALID")
        try:
            ancestors=ancestry(key,graph)
            if root not in ancestors:reasons.append("DECLARED_ROOT_NOT_IN_ANCESTRY")
            roots.append(ancestors)
            observed["witnesses"].append({"key_id":key,"declared_root":root,"ancestry_size":len(ancestors)})
        except ValueError as e:
            reasons.append(str(e))
    for i in range(len(roots)):
        for j in range(i+1,len(roots)):
            if roots[i]&roots[j]:reasons.append("WITNESS_SHARED_CONTROLLER_ANCESTRY")
    nonce_set=set()
    previous="0"*64
    for index,event in enumerate(ledger[:256]):
        if not isinstance(event,dict) or set(event)!={"sequence","nonce","challenge_id","run_id","previous_sha256","entry_sha256"}:
            reasons.append("LEDGER_EVENT_SCHEMA_INVALID")
            break
        if type(event["sequence"]) is not int or event["sequence"]!=index:
            reasons.append("LEDGER_SEQUENCE_GAP")
        if event["previous_sha256"]!=previous:
            reasons.append("LEDGER_PREVIOUS_HASH_MISMATCH")
        nonce=event["nonce"]
        if not isinstance(nonce,str) or not nonce or len(nonce)>128:
            reasons.append("LEDGER_NONCE_INVALID")
        elif nonce in nonce_set:reasons.append("LEDGER_NONCE_REPLAY")
        nonce_set.add(nonce)
        if not isinstance(event["challenge_id"],str) or not event["challenge_id"]:
            reasons.append("LEDGER_CHALLENGE_INVALID")
        if type(event["run_id"]) is not int or event["run_id"]<=0:
            reasons.append("LEDGER_RUN_INVALID")
        claimed=event["entry_sha256"]
        content={k:v for k,v in event.items() if k!="entry_sha256"}
        computed=digest(content)
        if claimed!=computed:reasons.append("LEDGER_ENTRY_DIGEST_MISMATCH")
        previous=computed
        observed["chain"].append({"sequence":index,"sha256":computed})
    observed["reconstructed_head"]=previous
    if not ledger:reasons.append("LEDGER_EMPTY")
    if not isinstance(expected_head,str) or not HEX64.fullmatch(expected_head):
        reasons.append("PINNED_HEAD_INVALID")
    elif previous!=expected_head:
        reasons.append("EXTERNAL_HEAD_MISMATCH")
    # Identifiers and a hash chain alone cannot authenticate independent controllers or custody.
    reasons.append("EXTERNAL_CONTROLLER_AND_LEDGER_CUSTODY_UNAUTHENTICATED")
    return {"schema":SCHEMA,"verdict":"REJECT_OR_UNVERIFIED",
            "reasons":sorted(set(reasons)),"observed":observed,**HOLD}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--input",required=True,type=Path)
    parser.add_argument("--out",type=Path)
    args=parser.parse_args()
    try:
        raw=args.input.read_bytes()
        if len(raw)>256*1024:raise ValueError("INPUT_TOO_LARGE")
        result=check(json.loads(raw))
    except (ValueError,OSError,TypeError) as e:
        result={"schema":SCHEMA,"verdict":"REJECT_OR_UNVERIFIED",
                "reasons":["INPUT_UNAVAILABLE:"+type(e).__name__],
                "observed":{},**HOLD}
    output=json.dumps(result,indent=2,sort_keys=True)+"\n"
    if args.out:
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(output,encoding="utf-8")
    print(output,end="")
    return 1

if __name__=="__main__":
    raise SystemExit(main())
