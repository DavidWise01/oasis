#!/usr/bin/env python3
"""AETHER-260-RS: bounded SQLite receipt export and offline replay verification.

Local consistency is not external immutable evidence or operational authority.
"""
import argparse
import hashlib
import json
import sqlite3
from pathlib import Path

SCHEMA="AETHER-260/receipt-export-v1"
CAS_SCHEMA="AETHER-258/sqlite-cas-v1"
GENESIS="0"*64
MAX_ROWS=4096
HOLD={"verdict":"REJECT_OR_UNVERIFIED","operational_authority":"HOLD",
      "physical_qualification_percent":0,"physical_act_allowed":False,
      "external_receipt_custody_verified":False}

def canonical(x):
    return json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=True,allow_nan=False).encode()

def digest(x):
    return hashlib.sha256(canonical(x)).hexdigest()

def export(dbpath):
    """Acquire one SQLite read transaction and serialize all bounded ledger rows."""
    db=sqlite3.connect(str(dbpath),timeout=5,isolation_level=None)
    try:
        db.execute("BEGIN")
        head=db.execute("SELECT seq,hash FROM head WHERE id=1").fetchone()
        events=db.execute("SELECT seq,previous_hash,head_hash,challenge,nonce,host,receipt_hash FROM events ORDER BY seq").fetchall()
        attempts=db.execute("SELECT id,host,decision,challenge,nonce,expected_seq,expected_head,actual_seq,actual_head,receipt_hash FROM attempts ORDER BY id").fetchall()
        db.commit()
    except Exception:
        db.rollback();raise
    finally:
        db.close()
    if head is None or len(events)>MAX_ROWS or len(attempts)>MAX_ROWS:
        raise ValueError("UNBOUNDED_OR_MISSING_LEDGER")
    bundle={"schema":SCHEMA,"head":{"sequence":head[0],"sha256":head[1]},
            "events":[dict(zip(("sequence","previous_hash","head_hash","challenge","nonce","host","receipt_sha256"),row)) for row in events],
            "attempts":[dict(zip(("attempt_id","host","decision","challenge","nonce","expected_sequence","expected_head","actual_sequence","actual_head","receipt_sha256"),row)) for row in attempts]}
    bundle["export_sha256"]=digest(bundle)
    return bundle

def review(bundle):
    problems=[]
    if not isinstance(bundle,dict) or set(bundle)!={"schema","head","events","attempts","export_sha256"}:
        return {**HOLD,"reasons":["EXPORT_SCHEMA_INVALID"]}
    if bundle["schema"]!=SCHEMA:problems.append("EXPORT_VERSION_INVALID")
    if not isinstance(bundle["events"],list) or len(bundle["events"])>MAX_ROWS or not isinstance(bundle["attempts"],list) or len(bundle["attempts"])>MAX_ROWS:
        return {**HOLD,"reasons":["ROW_LIMIT_OR_TYPE_INVALID"]}
    if bundle["export_sha256"]!=digest({k:v for k,v in bundle.items() if k!="export_sha256"}):
        problems.append("EXPORT_DIGEST_MISMATCH")
    attempts={}
    prior=GENESIS
    for attempt in bundle["attempts"]:
        if not isinstance(attempt,dict) or set(attempt)!={"attempt_id","host","decision","challenge","nonce","expected_sequence","expected_head","actual_sequence","actual_head","receipt_sha256"}:
            problems.append("ATTEMPT_SCHEMA_INVALID");continue
        ident=attempt["attempt_id"]
        if not isinstance(ident,str) or not ident or ident in attempts:
            problems.append("ATTEMPT_DUPLICATE_OR_INVALID")
        else:attempts[ident]=attempt
        fields={"schema":CAS_SCHEMA,**{k:v for k,v in attempt.items() if k!="receipt_sha256"}}
        if attempt["receipt_sha256"]!=digest(fields):problems.append("ATTEMPT_RECEIPT_TAMPER")
    accepted=[r for r in attempts.values() if r["decision"]=="ACCEPTED"]
    seen_nonce=set()
    seen_challenge=set()
    for i,event in enumerate(bundle["events"],1):
        if not isinstance(event,dict) or set(event)!={"sequence","previous_hash","head_hash","challenge","nonce","host","receipt_sha256"}:
            problems.append("EVENT_SCHEMA_INVALID");continue
        if type(event["sequence"]) is not int or event["sequence"]!=i:
            problems.append("MISSING_OR_REORDERED_EVENT")
        if event["previous_hash"]!=prior:problems.append("EVENT_CHAIN_BROKEN")
        if event["nonce"] in seen_nonce:problems.append("NONCE_REPLAY")
        if event["challenge"] in seen_challenge:problems.append("CHALLENGE_REPLAY")
        seen_nonce.add(event["nonce"]);seen_challenge.add(event["challenge"])
        matches=[a for a in accepted if a["actual_sequence"]==i and a["actual_head"]==event["head_hash"] and a["host"]==event["host"] and a["challenge"]==event["challenge"] and a["nonce"]==event["nonce"]]
        if len(matches)!=1:
            problems.append("ACCEPTED_ATTEMPT_MISSING_OR_DUPLICATE")
        else:
            candidate=digest({"sequence":i,"previous":prior,"host":event["host"],
                              "challenge":event["challenge"],"nonce":event["nonce"],
                              "attempt_id":matches[0]["attempt_id"]})
            if candidate!=event["head_hash"]:problems.append("EVENT_HASH_INVALID")
        expected_receipt=digest({"kind":"accepted_event","sequence":i,"head":event["head_hash"]})
        if event["receipt_sha256"]!=expected_receipt:problems.append("EVENT_RECEIPT_TAMPER")
        prior=event["head_hash"]
    if len(accepted)!=len(bundle["events"]):problems.append("ACCEPTED_COUNT_MISMATCH")
    head=bundle["head"]
    if not isinstance(head,dict) or set(head)!={"sequence","sha256"} or type(head["sequence"]) is not int or head["sequence"]!=len(bundle["events"]) or head["sha256"]!=prior:
        problems.append("FINAL_HEAD_MISMATCH")
    problems.extend(["EXTERNAL_CUSTODY_NOT_ATTESTED","RESTART_ORIGIN_NOT_ATTESTED"])
    return {**HOLD,"reasons":sorted(set(problems)),
            "checked_events":len(bundle["events"]),"checked_attempts":len(bundle["attempts"]),
            "export_sha256":bundle["export_sha256"]}

def main():
    parser=argparse.ArgumentParser()
    sub=parser.add_subparsers(dest="mode",required=True)
    e=sub.add_parser("export");e.add_argument("--db",type=Path,required=True)
    v=sub.add_parser("review");v.add_argument("--input",type=Path,required=True)
    parser.add_argument("--out",type=Path)
    args=parser.parse_args()
    try:
        if args.mode=="export":result=export(args.db)
        else:
            raw=args.input.read_bytes()
            if len(raw)>4*1024*1024:raise ValueError("EXPORT_TOO_LARGE")
            result=review(json.loads(raw))
    except (OSError,ValueError,TypeError,sqlite3.Error) as exc:
        result={**HOLD,"reasons":["INPUT_REJECTED:"+type(exc).__name__]}
    text=json.dumps(result,indent=2,sort_keys=True)+"\n"
    if args.out:
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(text,encoding="utf-8")
    print(text,end="")
    return 1
if __name__=="__main__":raise SystemExit(main())
