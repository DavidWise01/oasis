#!/usr/bin/env python3
"""AETHER-285-RS: forensic acquisition-chain replay against preserved raw manifests.

The AETHER-284 database omits endpoint URLs, so it cannot alone reconstruct
its own batch-head digests. An independently supplied manifest is required;
matching manifests are not independently authenticated custody.
"""
import argparse
import hashlib
import json
import sqlite3
from pathlib import Path

SCHEMA="AETHER-284/acquired-prefix-v1"
ANCHOR_SCHEMA="AETHER-285/highwater-anchor-v1"
ZERO="0"*64
HOLD={"verdict":"REJECT_OR_UNVERIFIED","operational_authority":"HOLD",
      "physical_act_allowed":False,"physical_qualification_percent":0,
      "externally_sealed_nonce_history_verified":False,
      "independent_external_custody_verified":False}

def canon(obj):
    return json.dumps(obj,sort_keys=True,separators=(",",":"),allow_nan=False,ensure_ascii=True).encode()
def sha(obj):
    return hashlib.sha256(canon(obj)).hexdigest()
def valid_hex(value):
    return isinstance(value,str) and len(value)==64 and all(c in "0123456789abcdef" for c in value)

def read_local(path):
    db=sqlite3.connect(Path(path).resolve().as_uri()+"?mode=ro",uri=True,timeout=5,isolation_level=None)
    try:
        db.execute("PRAGMA query_only=ON")
        db.execute("BEGIN")
        batches=[dict(zip(("id","trust_sha","challenge_nonce","previous_head","head_sha"),row))
                 for row in db.execute("SELECT id,trust_sha,challenge_nonce,previous_head,head_sha FROM batch ORDER BY id")]
        nonces=[dict(zip(("nonce","batch_id","key_id","raw_sha","observation_sha"),row))
                for row in db.execute("SELECT nonce,batch_id,key_id,raw_sha,observation_sha FROM witness_nonce ORDER BY batch_id,key_id")]
        db.commit()
    except Exception:
        if db.in_transaction:db.rollback()
        raise
    finally:
        db.close()
    return {"batches":batches,"nonces":nonces}

def replay(view,manifests,anchor,anchor_digest):
    issues=[]
    if not isinstance(view,dict) or set(view)!={"batches","nonces"} or not isinstance(view["batches"],list) or not isinstance(view["nonces"],list):
        return {**HOLD,"reasons":["LOCAL_SNAPSHOT_SCHEMA_INVALID"]}
    batches=view["batches"];nonces=view["nonces"]
    if len(batches)>4096 or len(nonces)>12288:
        return {**HOLD,"reasons":["LEDGER_TOO_LARGE"]}
    if not isinstance(manifests,list):
        manifests=[];issues.append("PRESERVED_RAW_MANIFESTS_REQUIRED")
    if len(manifests)!=len(batches):issues.append("MANIFEST_COUNT_MISMATCH")
    if not valid_hex(anchor_digest):
        issues.append("OUT_OF_BAND_ANCHOR_DIGEST_REQUIRED")
    elif not isinstance(anchor,dict) or set(anchor)!={"schema","minimum_batch_id","head_sha256","minimum_nonce_count","custodian_claim"}:
        issues.append("ANCHOR_SCHEMA_INVALID")
    else:
        if sha(anchor)!=anchor_digest:issues.append("ANCHOR_DIGEST_CONFLICT")
        if anchor["schema"]!=ANCHOR_SCHEMA:issues.append("ANCHOR_VERSION_INVALID")
        if type(anchor["minimum_batch_id"]) is not int or anchor["minimum_batch_id"]<1:
            issues.append("ANCHOR_BATCH_INVALID")
        if type(anchor["minimum_nonce_count"]) is not int or anchor["minimum_nonce_count"]<0:
            issues.append("ANCHOR_NONCE_COUNT_INVALID")
        if not valid_hex(anchor["head_sha256"]):issues.append("ANCHOR_HEAD_INVALID")
    grouped={}
    seen_nonces=set()
    for n in nonces:
        if not isinstance(n,dict) or set(n)!={"nonce","batch_id","key_id","raw_sha","observation_sha"}:
            issues.append("NONCE_ROW_SCHEMA_INVALID");continue
        if not isinstance(n["nonce"],str) or not n["nonce"] or n["nonce"] in seen_nonces:
            issues.append("NONCE_REPLAY_OR_INVALID")
        seen_nonces.add(n["nonce"])
        if not valid_hex(n["raw_sha"]) or not valid_hex(n["observation_sha"]):
            issues.append("NONCE_RAW_DIGEST_INVALID")
        grouped.setdefault(n["batch_id"],[]).append(n)
    prev=ZERO;seen_challenges=set()
    for index,b in enumerate(batches):
        if not isinstance(b,dict) or set(b)!={"id","trust_sha","challenge_nonce","previous_head","head_sha"}:
            issues.append("BATCH_ROW_SCHEMA_INVALID");continue
        if type(b["id"]) is not int or b["id"]!=index+1:
            issues.append("BATCH_SEQUENCE_GAP")
        if b["previous_head"]!=prev:issues.append("BATCH_PARENT_MISMATCH")
        if not valid_hex(b["head_sha"]) or not valid_hex(b["trust_sha"]):
            issues.append("BATCH_DIGEST_SCHEMA_INVALID")
        if b["challenge_nonce"] in seen_challenges:
            issues.append("CHALLENGE_REPLAY")
        seen_challenges.add(b["challenge_nonce"])
        rows=grouped.get(b["id"],[])
        if len(rows)!=3 or len({r["key_id"] for r in rows})!=3:
            issues.append("BATCH_WITNESS_NONCE_TRIPLE_INVALID")
        if index<len(manifests):
            m=manifests[index]
            required={"batch_id","trust_sha256","challenge_nonce","previous_head_sha256","witnesses"}
            if not isinstance(m,dict) or set(m)!=required:
                issues.append("MANIFEST_SCHEMA_INVALID")
            else:
                if m["batch_id"]!=b["id"] or m["trust_sha256"]!=b["trust_sha"] or m["challenge_nonce"]!=b["challenge_nonce"] or m["previous_head_sha256"]!=b["previous_head"]:
                    issues.append("MANIFEST_HEADER_SUBSTITUTION")
                witnesses=m["witnesses"]
                if not isinstance(witnesses,list) or len(witnesses)!=3:
                    issues.append("MANIFEST_WITNESS_SET_INVALID")
                else:
                    expected={"key_id","raw_sha256","observation_sha256","requested_url"}
                    if any(not isinstance(w,dict) or set(w)!=expected for w in witnesses):
                        issues.append("MANIFEST_WITNESS_SCHEMA_INVALID")
                    else:
                        for w in witnesses:
                            if not all(isinstance(w[k],str) and w[k] for k in expected):
                                issues.append("MANIFEST_WITNESS_FIELD_INVALID")
                        ordered=sorted(witnesses,key=lambda w:w["key_id"])
                        local=[(r["key_id"],r["raw_sha"],r["observation_sha"]) for r in sorted(rows,key=lambda r:r["key_id"])]
                        original=[(w["key_id"],w["raw_sha256"],w["observation_sha256"]) for w in ordered]
                        if local!=original:issues.append("MANIFEST_STORED_NONCE_DIVERGENCE")
                        statement={"schema":SCHEMA,"trust_sha256":b["trust_sha"],"challenge_nonce":b["challenge_nonce"],
                                   "previous_head_sha256":b["previous_head"],"witnesses":ordered}
                        if sha(statement)!=b["head_sha"]:
                            issues.append("BATCH_HEAD_RECOMPUTATION_FAILED")
        prev=b["head_sha"]
    if len(nonces)!=len(batches)*3:issues.append("GLOBAL_NONCE_CONSERVATION_FAILED")
    if len(grouped)>len(batches) or any(i not in {b.get("id") for b in batches if isinstance(b,dict)} for i in grouped):
        issues.append("ORPHAN_NONCE_BATCH")
    if isinstance(anchor,dict) and set(anchor)=={"schema","minimum_batch_id","head_sha256","minimum_nonce_count","custodian_claim"}:
        sequence=anchor["minimum_batch_id"]
        if type(sequence) is int and sequence>0:
            if len(batches)<sequence:issues.append("ANCHORED_BATCH_REMOVED")
            elif isinstance(batches[sequence-1],dict) and batches[sequence-1].get("head_sha")!=anchor["head_sha256"]:
                issues.append("ANCHORED_HISTORICAL_BATCH_REWRITTEN")
        if type(anchor["minimum_nonce_count"]) is int and len(nonces)<anchor["minimum_nonce_count"]:
            issues.append("ANCHORED_NONCE_HIGHWATER_ROLLBACK")
    issues.extend(["PRESERVED_MANIFEST_CUSTODY_NOT_AUTHENTICATED",
                   "ANCHOR_SIGNER_AND_CONTROL_ANCESTRY_UNVERIFIED",
                   "LOCAL_SQLITE_AND_MANIFEST_ROLLBACK_POSSIBLE"])
    return {**HOLD,"reasons":sorted(set(issues)),
            "observed":{"batches":len(batches),"witness_nonces":len(nonces),
                        "latest_head_sha256":prev,
                        "all_batch_digests_recomputed":len(manifests)==len(batches) and
                          not any("MANIFEST_" in p or "BATCH_HEAD_RECOMPUTATION_FAILED"==p for p in issues)}}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--db",type=Path,required=True)
    p.add_argument("--manifests",type=Path,required=True)
    p.add_argument("--anchor",type=Path,required=True)
    p.add_argument("--trusted-anchor-sha256",required=True)
    p.add_argument("--out",type=Path)
    a=p.parse_args()
    try:
        raw=[a.manifests.read_bytes(),a.anchor.read_bytes()]
        if any(len(x)>1024*1024 for x in raw):raise ValueError("EVIDENCE_TOO_LARGE")
        result=replay(read_local(a.db),json.loads(raw[0]),json.loads(raw[1]),a.trusted_anchor_sha256)
    except (OSError,ValueError,TypeError,KeyError,sqlite3.Error) as error:
        result={**HOLD,"reasons":["INPUT_REJECTED:"+type(error).__name__]}
    output=json.dumps(result,sort_keys=True,indent=2)+"\n"
    if a.out:a.out.write_text(output,encoding="utf-8")
    print(output,end="")
    return 1
if __name__=="__main__":raise SystemExit(main())
