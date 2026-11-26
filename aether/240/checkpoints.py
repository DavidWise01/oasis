#!/usr/bin/env python3
"""AETHER-240-RS: read-only multi-witness append-only checkpoint consistency."""
from __future__ import annotations
import argparse,hashlib,json,re
from pathlib import Path
SCHEMA="AETHER-240/checkpoint-consistency-v1"
HOLD={"operational_authority":"HOLD","physical_qualification_percent":0,
"physical_act_allowed":False,"independent_custody_authenticated":False}
def digest(x):
    return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=True,allow_nan=False).encode()).hexdigest()
def inspect_chain(entries):
    issues=[]; heads=[]; seen=set(); prev="0"*64
    if not isinstance(entries,list) or not 1<=len(entries)<=256:return [],["CHAIN_LENGTH_INVALID"]
    for i,e in enumerate(entries):
        if not isinstance(e,dict) or set(e)!={"sequence","previous_sha256","nonce","challenge_id","run_id","entry_sha256"}:
            issues.append("ENTRY_SCHEMA_INVALID");break
        if type(e["sequence"]) is not int or e["sequence"]!=i:issues.append("SEQUENCE_GAP")
        if e["previous_sha256"]!=prev:issues.append("PREVIOUS_HASH_MISMATCH")
        nonce=e["nonce"]
        if not isinstance(nonce,str) or not nonce or len(nonce)>128:issues.append("NONCE_INVALID")
        elif nonce in seen:issues.append("NONCE_REPLAY")
        else:seen.add(nonce)
        if not isinstance(e["challenge_id"],str) or not e["challenge_id"]:issues.append("CHALLENGE_INVALID")
        if type(e["run_id"]) is not int or e["run_id"]<=0:issues.append("RUN_ID_INVALID")
        computed=digest({k:v for k,v in e.items() if k!="entry_sha256"})
        if e["entry_sha256"]!=computed:issues.append("ENTRY_DIGEST_MISMATCH")
        prev=computed;heads.append(computed)
    return heads,issues
def assess(bundle):
    obs={"witnesses":[]}
    if not isinstance(bundle,dict):return {"schema":SCHEMA,"verdict":"REJECT_OR_UNVERIFIED","reasons":["BUNDLE_INVALID"],"observed":obs,**HOLD}
    ws=bundle.get("witnesses")
    if not isinstance(ws,list) or not 3<=len(ws)<=16:
        return {"schema":SCHEMA,"verdict":"REJECT_OR_UNVERIFIED","reasons":["WITNESS_SET_INVALID"],"observed":obs,**HOLD}
    issues=[];roots=set();identifiers=set();chains=[]
    source=bundle.get("source_commit");challenge=bundle.get("challenge_id");run=bundle.get("run_id")
    if not isinstance(source,str) or not re.fullmatch("[0-9a-f]{40}",source):issues.append("SOURCE_COMMIT_INVALID")
    if not isinstance(challenge,str) or not challenge:issues.append("CHALLENGE_INVALID")
    if type(run) is not int or run<=0:issues.append("BUNDLE_RUN_ID_INVALID")
    for w in ws:
        if not isinstance(w,dict) or set(w)!={"root","checkpoint_id","length","head_sha256","entries","source_commit","challenge_id","run_id"}:
            issues.append("WITNESS_SCHEMA_INVALID");continue
        root=w["root"];ident=w["checkpoint_id"]
        if not isinstance(root,str) or not root:issues.append("ROOT_INVALID")
        elif root in roots:issues.append("DUPLICATE_ROOT")
        else:roots.add(root)
        if not isinstance(ident,str) or not ident:issues.append("CHECKPOINT_ID_INVALID")
        elif ident in identifiers:issues.append("CHECKPOINT_REPLAY")
        else:identifiers.add(ident)
        if (w["source_commit"],w["challenge_id"],w["run_id"])!=(source,challenge,run):
            issues.append("CROSS_WITNESS_BINDING_MISMATCH")
        heads,problems=inspect_chain(w["entries"]);issues.extend(problems)
        if type(w["length"]) is not int or w["length"]!=len(heads):issues.append("CHECKPOINT_LENGTH_MISMATCH")
        if not heads or w["head_sha256"]!=heads[-1]:issues.append("CHECKPOINT_HEAD_MISMATCH")
        if isinstance(w["entries"],list) and any(e.get("challenge_id")!=challenge or e.get("run_id")!=run
           for e in w["entries"] if isinstance(e,dict)):issues.append("LEDGER_EVENT_BINDING_MISMATCH")
        chains.append(heads)
        obs["witnesses"].append({"root":root,"checkpoint_id":ident,"length":len(heads),
                                 "computed_head":heads[-1] if heads else None})
    if len(roots)<3:issues.append("THREE_DISTINCT_ROOTS_NOT_PRESENT")
    for i,left in enumerate(chains):
        for right in chains[i+1:]:
            n=min(len(left),len(right))
            if left[:n]!=right[:n]:issues.append("DIVERGENT_LEDGER_HISTORY")
    obs["consistent_prefixes"]="DIVERGENT_LEDGER_HISTORY" not in issues and not any(
        code in issues for code in ("ENTRY_DIGEST_MISMATCH","PREVIOUS_HASH_MISMATCH","SEQUENCE_GAP"))
    issues.append("EXTERNAL_WITNESS_CUSTODY_AND_SIGNATURES_UNAUTHENTICATED")
    return {"schema":SCHEMA,"verdict":"REJECT_OR_UNVERIFIED","reasons":sorted(set(issues)),"observed":obs,**HOLD}
def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--bundle",type=Path,required=True);parser.add_argument("--out",type=Path)
    args=parser.parse_args()
    try:
        raw=args.bundle.read_bytes()
        if len(raw)>1024*1024:raise ValueError("INPUT_TOO_LARGE")
        result=assess(json.loads(raw))
    except (ValueError,OSError,TypeError,UnicodeError) as error:
        result={"schema":SCHEMA,"verdict":"REJECT_OR_UNVERIFIED",
                "reasons":["INPUT_INVALID:"+type(error).__name__],"observed":{},**HOLD}
    output=json.dumps(result,sort_keys=True,indent=2)+"\n"
    if args.out:
        args.out.parent.mkdir(parents=True,exist_ok=True);args.out.write_text(output,encoding="utf-8")
    print(output,end="");return 1
if __name__=="__main__":raise SystemExit(main())
