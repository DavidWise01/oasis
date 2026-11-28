#!/usr/bin/env python3
"""AETHER-281-RS: read-only SQLite recovery audit with pinned full-row digest.

No custody provenance, trusted time, or physical ACT is conferred.
"""
import argparse,hashlib,json,sqlite3
from pathlib import Path

SCHEMA="AETHER-281/recovery-snapshot-v1"
ZERO="0"*64
HOLD={"verdict":"REJECT_OR_UNVERIFIED","operational_authority":"HOLD",
      "physical_act_allowed":False,"physical_qualification_percent":0,
      "external_checkpoint_custody_verified":False,
      "crash_consistency_physically_qualified":False}

def canonical(v):
    return json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=True,allow_nan=False).encode()
def sha(v):return hashlib.sha256(canonical(v)).hexdigest()
def hex64(x):return isinstance(x,str) and len(x)==64 and all(c in "0123456789abcdef" for c in x)

def readback(path):
    """Open a real journal read-only; one BEGIN snapshot across its tables."""
    db=sqlite3.connect(Path(path).resolve().as_uri()+"?mode=ro",uri=True,timeout=5,isolation_level=None)
    try:
        db.execute("PRAGMA query_only=ON")
        db.execute("BEGIN")
        registry=[dict(zip(("source_id","controller","public_key_pem"),r))
                  for r in db.execute("SELECT source_id,controller,public_key_pem FROM signer ORDER BY source_id")]
        seal=db.execute("SELECT sha256 FROM registry_seal WHERE id=1").fetchone()
        challenges=[dict(zip(("nonce","content_sha256","registry_sha256"),r))
                    for r in db.execute("SELECT nonce,content_sha256,registry_sha256 FROM challenge ORDER BY nonce")]
        receipts=[dict(zip(("session_nonce","session_id","challenge_nonce","source_id","payload_sha256","signature_b64"),r))
                  for r in db.execute("SELECT session_nonce,session_id,challenge_nonce,source_id,payload_sha256,signature_b64 FROM receipt ORDER BY session_nonce")]
        highwater=[dict(zip(("seq","previous_sha256","head_sha256","registry_sha256","challenge_count","receipt_count","run_id","challenge_nonce"),r))
                   for r in db.execute("SELECT seq,previous_sha256,head_sha256,registry_sha256,challenge_count,receipt_count,run_id,challenge_nonce FROM highwater ORDER BY seq")]
        db.commit()
    except Exception:
        if db.in_transaction:db.rollback()
        raise
    finally:db.close()
    return {"registry":registry,"seal_sha256":seal[0] if seal else None,
            "challenges":challenges,"receipts":receipts,"highwater":highwater}

def validate(view):
    issues=[]
    if not isinstance(view,dict) or set(view)!={"registry","seal_sha256","challenges","receipts","highwater"}:
        return ["SNAPSHOT_SCHEMA_INVALID"]
    reg=view["registry"];chs=view["challenges"];rs=view["receipts"];hs=view["highwater"]
    if not all(isinstance(x,list) and len(x)<=65536 for x in (reg,chs,rs,hs)):
        return ["SNAPSHOT_COLLECTION_INVALID"]
    if sha(reg)!=view["seal_sha256"]:issues.append("REGISTRY_SEAL_MISMATCH")
    if len(reg)!=3 or len({x["source_id"] for x in reg})!=3:issues.append("THREE_SIGNERS_REQUIRED")
    owners={x["source_id"] for x in reg}
    chset={c["nonce"] for c in chs}
    nonce_set=set();session_set=set();per_challenge={}
    for r in rs:
        if r["session_nonce"] in nonce_set or r["session_id"] in session_set:
            issues.append("DUPLICATE_RECEIPT")
        nonce_set.add(r["session_nonce"]);session_set.add(r["session_id"])
        if r["challenge_nonce"] not in chset:issues.append("ORPHAN_RECEIPT")
        if r["source_id"] not in owners:issues.append("UNPINNED_SOURCE")
        if not hex64(r["payload_sha256"]):issues.append("PAYLOAD_HASH_INVALID")
        per_challenge.setdefault(r["challenge_nonce"],[]).append(r["source_id"])
    for ch in chs:
        if ch["registry_sha256"]!=view["seal_sha256"]:issues.append("CHALLENGE_REGISTRY_PIN_INVALID")
        if not hex64(ch["content_sha256"]):issues.append("CHALLENGE_DIGEST_INVALID")
        sources=per_challenge.get(ch["nonce"],[])
        if len(sources)!=3 or len(set(sources))!=3:issues.append("SOURCE_TRIPLE_INVALID")
    if len(rs)!=3*len(chs) or len(hs)!=len(chs):
        issues.append("JOURNAL_CONSERVATION_INVALID")
    prev=ZERO;last_run=0
    for i,h in enumerate(hs):
        if h["seq"]!=i+1 or h["previous_sha256"]!=prev:issues.append("CHECKPOINT_CHAIN_BROKEN")
        stmt={"schema":"AETHER-280/atomic-journal-v1","seq":h["seq"],
              "previous_sha256":h["previous_sha256"],"registry_sha256":h["registry_sha256"],
              "challenge_count":h["challenge_count"],"receipt_count":h["receipt_count"],
              "run_id":h["run_id"],"challenge_nonce":h["challenge_nonce"]}
        if sha(stmt)!=h["head_sha256"]:issues.append("HIGHWATER_DIGEST_MISMATCH")
        if h["challenge_count"]!=i+1 or h["receipt_count"]!=3*(i+1):
            issues.append("HIGHWATER_COUNTER_INVALID")
        if h["run_id"]<last_run:issues.append("RUN_ID_ROLLBACK")
        if h["registry_sha256"]!=view["seal_sha256"]:issues.append("HIGHWATER_REGISTRY_MISMATCH")
        if h["challenge_nonce"] not in chset:issues.append("CHECKPOINT_CHALLENGE_MISSING")
        prev=h["head_sha256"];last_run=h["run_id"]
    return sorted(set(issues))

def snapshot(view):
    """Canonical forensic content snapshot; not a self-authenticating anchor."""
    return {"schema":SCHEMA,"registry_sha256":sha(view["registry"]),
            "challenge_count":len(view["challenges"]),
            "receipt_count":len(view["receipts"]),
            "highwater_count":len(view["highwater"]),
            "last_head_sha256":view["highwater"][-1]["head_sha256"] if view["highwater"] else ZERO,
            "full_journal_sha256":sha(view)}

def assess(view,anchored=None,anchor_pin=None):
    issues=validate(view)
    current=snapshot(view)
    if not hex64(anchor_pin):issues.append("OUT_OF_BAND_ANCHOR_PIN_REQUIRED")
    elif not isinstance(anchored,dict) or set(anchored)!=set(current):
        issues.append("EXTERNAL_ANCHOR_SCHEMA_INVALID")
    else:
        if sha(anchored)!=anchor_pin:issues.append("EXTERNAL_ANCHOR_PIN_MISMATCH")
        if anchored["schema"]!=SCHEMA:issues.append("EXTERNAL_ANCHOR_SCHEMA_VERSION")
        for k in ("challenge_count","receipt_count","highwater_count"):
            if type(anchored[k]) is not int or anchored[k]<0:issues.append("EXTERNAL_COUNT_INVALID")
            elif current[k]<anchored[k]:issues.append("RECOVERY_"+k.upper()+"_ROLLBACK")
        if current["highwater_count"]==anchored["highwater_count"]:
            if current["last_head_sha256"]!=anchored["last_head_sha256"]:
                issues.append("ANCHORED_HEAD_SUBSTITUTED")
            if current["full_journal_sha256"]!=anchored["full_journal_sha256"]:
                issues.append("ANCHORED_JOURNAL_CONTENT_CHANGED")
        elif current["highwater_count"]>anchored["highwater_count"]:
            # Exact historical head cannot be derived from a last-head-only pin:
            issues.append("HISTORICAL_PREFIX_NOT_PROVEN_BY_LATEST_HEAD_ONLY")
    issues+=["EXTERNAL_ANCHOR_NOT_INDEPENDENTLY_ACQUIRED",
             "STORED_RECEIPT_SIGNATURES_NOT_REVERIFIED_WITHOUT_ORIGINAL_CHALLENGE",
             "WHOLE_DATABASE_AND_ANCHOR_ROLLBACK_POSSIBLE"]
    return {**HOLD,"reasons":sorted(set(issues)),"observed":current}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--db",type=Path,required=True)
    parser.add_argument("--anchor",type=Path)
    parser.add_argument("--trusted-anchor-sha256")
    parser.add_argument("--out",type=Path)
    a=parser.parse_args()
    try:
        v=readback(a.db)
        raw=a.anchor.read_bytes() if a.anchor else None
        if raw is not None and len(raw)>100000:raise ValueError("ANCHOR_TOO_LARGE")
        result=assess(v,json.loads(raw) if raw else None,a.trusted_anchor_sha256)
    except (OSError,ValueError,TypeError,KeyError,sqlite3.Error) as exc:
        result={**HOLD,"reasons":["INPUT_REJECTED:"+type(exc).__name__]}
    output=json.dumps(result,indent=2,sort_keys=True)+"\n"
    if a.out:
        a.out.parent.mkdir(parents=True,exist_ok=True)
        a.out.write_text(output,encoding="utf-8")
    print(output,end="")
    return 1

if __name__=="__main__":raise SystemExit(main())
