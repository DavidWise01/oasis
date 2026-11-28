#!/usr/bin/env python3
"""AETHER-278-RS — local monotonic high-water and multi-restart forensic replay.

No local SQLite history constitutes an external custodian or physical authority.
"""
import argparse,base64,hashlib,json,sqlite3
from pathlib import Path

SCHEMA="AETHER-278/highwater-v1"
HOLD={"verdict":"REJECT_OR_UNVERIFIED","operational_authority":"HOLD",
      "physical_act_allowed":False,"physical_qualification_percent":0,
      "external_highwater_authenticated":False,"independent_custody_verified":False}

def canon(x):return json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=True,allow_nan=False).encode()
def sha(x):return hashlib.sha256(canon(x)).hexdigest()
def hex64(s):return isinstance(s,str) and len(s)==64 and all(c in "0123456789abcdef" for c in s)
def verify(pem,statement,signature):
    try:
        from cryptography.hazmat.primitives import serialization
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
        from cryptography.exceptions import InvalidSignature
        key=serialization.load_pem_public_key(pem.encode("ascii"))
        if not isinstance(key,Ed25519PublicKey):return False
        sig=base64.b64decode(signature,validate=True)
        if len(sig)!=64:return False
        key.verify(sig,canon(statement));return True
    except (ImportError,InvalidSignature,TypeError,ValueError,UnicodeError):return False

def connect(path):
    db=sqlite3.connect(str(path),timeout=10,isolation_level=None)
    db.execute("PRAGMA busy_timeout=10000")
    db.execute("PRAGMA journal_mode=WAL")
    db.execute("PRAGMA synchronous=FULL")
    db.execute("CREATE TABLE IF NOT EXISTS checkpoint (seq INTEGER PRIMARY KEY, previous_sha TEXT NOT NULL, head_sha TEXT NOT NULL, registry_sha TEXT NOT NULL, challenges INTEGER NOT NULL, receipts INTEGER NOT NULL, rotations INTEGER NOT NULL, run_id INTEGER NOT NULL)")
    return db

def statement(seq,previous_sha,registry_sha,challenges,receipts,rotations,run_id):
    return {"schema":SCHEMA,"seq":seq,"previous_sha256":previous_sha,
            "registry_sha256":registry_sha,"challenges":challenges,"receipts":receipts,
            "rotations":rotations,"run_id":run_id}

def rows(db):
    return [dict(zip(("seq","previous_sha","head_sha","registry_sha","challenges","receipts","rotations","run_id"),row)) for row in
            db.execute("SELECT seq,previous_sha,head_sha,registry_sha,challenges,receipts,rotations,run_id FROM checkpoint ORDER BY seq")]

def validate(entries):
    failures=[];previous="0"*64;last=None
    for idx,r in enumerate(entries):
        required={"seq","previous_sha","head_sha","registry_sha","challenges","receipts","rotations","run_id"}
        if not isinstance(r,dict) or set(r)!=required:
            failures.append("ROW_SCHEMA_INVALID");continue
        if type(r["seq"]) is not int or r["seq"]!=idx+1:
            failures.append("SEQUENCE_GAP")
        if r["previous_sha"]!=previous:failures.append("PREVIOUS_CHAIN_DIGEST_MISMATCH")
        fields=("challenges","receipts","rotations","run_id")
        if any(type(r[k]) is not int or r[k]<0 for k in fields):
            failures.append("INVALID_COUNTERS")
            continue
        if not hex64(r["registry_sha"]):failures.append("REGISTRY_HASH_INVALID")
        expected=sha(statement(r["seq"],r["previous_sha"],r["registry_sha"],
                              r["challenges"],r["receipts"],r["rotations"],r["run_id"]))
        if r["head_sha"]!=expected:failures.append("CHECKPOINT_HASH_MISMATCH")
        if r["receipts"]!=3*r["challenges"]:
            failures.append("THREE_RECEIPTS_PER_CHALLENGE_VIOLATED")
        if last:
            if any(r[k]<last[k] for k in ("challenges","receipts","rotations","run_id")):
                failures.append("MONOTONIC_COUNTER_ROLLBACK")
            if r["registry_sha"]!=last["registry_sha"] and r["rotations"]==last["rotations"]:
                failures.append("REGISTRY_CHANGE_WITHOUT_ROTATION")
        previous=r["head_sha"];last=r
    return sorted(set(failures))

def append(path,registry_sha,challenges,receipts,rotations,run_id,expected_head):
    if not hex64(registry_sha):raise ValueError("REGISTRY_SHA_INVALID")
    if not hex64(expected_head):raise ValueError("EXPECTED_HEAD_PIN_REQUIRED")
    if any(type(x) is not int or x<0 for x in (challenges,receipts,rotations,run_id)):
        raise ValueError("COUNTERS_INVALID")
    db=connect(path)
    try:
        db.execute("BEGIN IMMEDIATE")
        prior=rows(db)
        problems=validate(prior)
        if problems:raise ValueError("PREEXISTING_CHAIN_INVALID:"+",".join(problems))
        head=prior[-1]["head_sha"] if prior else "0"*64
        if head!=expected_head:raise ValueError("STALE_OR_SUBSTITUTED_HEAD")
        seq=len(prior)+1
        new=statement(seq,head,registry_sha,challenges,receipts,rotations,run_id)
        constructed={"seq":seq,"previous_sha":head,"head_sha":sha(new),
                     "registry_sha":registry_sha,"challenges":challenges,
                     "receipts":receipts,"rotations":rotations,"run_id":run_id}
        failures=validate(prior+[constructed])
        if failures:raise ValueError("MONOTONIC_INSERT_REJECTED:"+",".join(failures))
        db.execute("INSERT INTO checkpoint VALUES (?,?,?,?,?,?,?,?)",
                   (seq,head,constructed["head_sha"],registry_sha,challenges,receipts,rotations,run_id))
        db.commit()
        return {**HOLD,"sequence":seq,"head_sha256":constructed["head_sha"],
                "reasons":["LOCAL_HIGHWATER_NOT_EXTERNALLY_SEALED"]}
    except Exception:
        db.rollback();raise
    finally:db.close()

def inspect(path):
    db=connect(path)
    try:
        db.execute("BEGIN")
        entries=rows(db)
        db.commit()
    finally:db.close()
    return {"entries":entries,"validation_errors":validate(entries),
            "last_head_sha256":entries[-1]["head_sha"] if entries else "0"*64}

def audit(path,external_anchor,expected_anchor_sha):
    observed=inspect(path)
    problems=list(observed["validation_errors"])
    if not hex64(expected_anchor_sha):
        return {**HOLD,"reasons":["OUT_OF_BAND_ANCHOR_DIGEST_REQUIRED"],"observed":observed}
    if not isinstance(external_anchor,dict) or set(external_anchor)!={"statement","public_key_pem","signature_b64"}:
        return {**HOLD,"reasons":["EXTERNAL_ANCHOR_SCHEMA_INVALID"],"observed":observed}
    signed=external_anchor["statement"]
    if not isinstance(signed,dict) or set(signed)!={"schema","min_seq","min_challenges",
        "min_receipts","min_rotations","min_run_id","anchored_head_sha256","controller_claim"}:
        return {**HOLD,"reasons":["ANCHOR_STATEMENT_INVALID"],"observed":observed}
    if sha(signed)!=expected_anchor_sha:problems.append("EXTERNAL_ANCHOR_DIGEST_MISMATCH")
    if signed["schema"]!=SCHEMA:problems.append("ANCHOR_VERSION_INVALID")
    if not verify(external_anchor["public_key_pem"],signed,external_anchor["signature_b64"]):
        problems.append("EXTERNAL_ANCHOR_SIGNATURE_INVALID")
    if any(type(signed[k]) is not int or signed[k]<0 for k in
           ("min_seq","min_challenges","min_receipts","min_rotations","min_run_id")):
        problems.append("ANCHOR_COUNTER_SCHEMA_INVALID")
    entries=observed["entries"]
    if not entries:
        problems.append("LOCAL_HISTORY_EMPTY")
    else:
        last=entries[-1]
        targets=(("min_seq","seq"),("min_challenges","challenges"),
                 ("min_receipts","receipts"),("min_rotations","rotations"),("min_run_id","run_id"))
        for k,m in targets:
            if type(signed[k]) is int and last[m]<signed[k]:
                problems.append("RECOVERED_"+m.upper()+"_BELOW_ANCHOR")
        if signed["min_seq"]>0 and signed["min_seq"]<=len(entries):
            if entries[signed["min_seq"]-1]["head_sha"]!=signed["anchored_head_sha256"]:
                problems.append("ANCHORED_HISTORICAL_HEAD_REWRITTEN")
        elif signed["min_seq"]>len(entries):
            problems.append("ANCHORED_HEAD_MISSING")
    problems.extend(["EXTERNAL_ANCHOR_KEY_OWNERSHIP_UNVERIFIED",
                     "REMOTE_CUSTODIAN_HIGHWATER_NOT_OBSERVED",
                     "SQLITE_DATABASE_IMAGE_REPLACEMENT_POSSIBLE"])
    return {**HOLD,"reasons":sorted(set(problems)),"observed":observed}

def main():
    p=argparse.ArgumentParser()
    sub=p.add_subparsers(dest="cmd",required=True)
    a=sub.add_parser("append");a.add_argument("--db",type=Path,required=True)
    for name in ("registry-sha","challenges","receipts","rotations","run-id","expected-head"):
        a.add_argument("--"+name,required=True)
    b=sub.add_parser("audit");b.add_argument("--db",type=Path,required=True)
    b.add_argument("--anchor",type=Path,required=True);b.add_argument("--trusted-anchor-sha",required=True)
    c=sub.add_parser("inspect");c.add_argument("--db",type=Path,required=True)
    p.add_argument("--out",type=Path)
    x=p.parse_args()
    try:
        if x.cmd=="append":
            result=append(x.db,x.registry_sha,int(x.challenges),int(x.receipts),
                          int(x.rotations),int(x.run_id),x.expected_head)
        elif x.cmd=="audit":
            raw=x.anchor.read_bytes()
            if len(raw)>1024*1024:raise ValueError("ANCHOR_OVERSIZE")
            result=audit(x.db,json.loads(raw),x.trusted_anchor_sha)
        else:result={**HOLD,**inspect(x.db)}
    except (OSError,ValueError,TypeError,sqlite3.Error) as err:
        result={**HOLD,"reasons":["INPUT_REJECTED:"+type(err).__name__+":"+str(err)[:100]]}
    output=json.dumps(result,indent=2,sort_keys=True)+"\n"
    if x.out:x.out.write_text(output,encoding="utf-8")
    print(output,end="")
    return 1
if __name__=="__main__":raise SystemExit(main())
