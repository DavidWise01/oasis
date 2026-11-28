#!/usr/bin/env python3
"""AETHER-279-RS: read-only cross-DB reconciliation and independently claimed anchor.

SQLite ATTACH is NOT evidence of atomic commit across independently managed files.
"""
import argparse,hashlib,json,sqlite3,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"278"))
from highwater import validate

SCHEMA="AETHER-279/cross-db-reconciliation-v1"
HOLD={"verdict":"REJECT_OR_UNVERIFIED","operational_authority":"HOLD",
      "physical_act_allowed":False,"physical_qualification_percent":0,
      "atomic_cross_database_commit_verified":False,
      "external_custody_verified":False}
def canonical(x):
    return json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=True,allow_nan=False).encode()
def sha(x):
    return hashlib.sha256(canonical(x)).hexdigest()
def hex64(x):
    return isinstance(x,str) and len(x)==64 and all(ch in "0123456789abcdef" for ch in x)
def path_uri(path):
    return Path(path).resolve().as_uri()+"?mode=ro"

def capture(receipt_db,highwater_db):
    """Read both attached files in a read transaction; not a distributed atomic barrier."""
    if Path(receipt_db).resolve()==Path(highwater_db).resolve():
        raise ValueError("IDENTICAL_DATABASE_PATHS")
    db=sqlite3.connect(":memory:",isolation_level=None,timeout=5)
    try:
        db.execute("ATTACH DATABASE ? AS receipts",(path_uri(receipt_db),))
        db.execute("ATTACH DATABASE ? AS highwater",(path_uri(highwater_db),))
        db.execute("BEGIN")
        registry=[dict(zip(("source_id","controller","key_pem","version"),r)) for r in
                  db.execute("SELECT source_id,controller,key_pem,version FROM receipts.signer ORDER BY source_id")]
        challenges=[dict(zip(("nonce","digest","registry"),r)) for r in
                    db.execute("SELECT challenge_nonce,challenge_sha,registry_sha FROM receipts.challenge ORDER BY challenge_nonce")]
        sessions=[dict(zip(("nonce","session","challenge","source","payload","signature"),r)) for r in
                  db.execute("SELECT session_nonce,session_id,challenge_nonce,source_id,payload_sha,signature_b64 FROM receipts.receipt ORDER BY session_nonce")]
        rotations=[dict(zip(("source","old","new","previous","next"),r)) for r in
                   db.execute("SELECT source_id,old_key_sha,new_key_sha,previous_registry_sha,next_registry_sha FROM receipts.rotation ORDER BY id")]
        hw=[dict(zip(("seq","previous_sha","head_sha","registry_sha","challenges","receipts","rotations","run_id"),r)) for r in
            db.execute("SELECT seq,previous_sha,head_sha,registry_sha,challenges,receipts,rotations,run_id FROM highwater.checkpoint ORDER BY seq")]
        db.commit()
    except Exception:
        if db.in_transaction:db.rollback()
        raise
    finally:db.close()
    return {"registry":registry,"challenges":challenges,"receipts":sessions,
            "rotations":rotations,"highwater":hw}

def reconcile(data,anchor=None,expected_anchor_sha=None):
    errors=[]
    if not isinstance(data,dict) or set(data)!={"registry","challenges","receipts","rotations","highwater"}:
        return {**HOLD,"reasons":["CAPTURE_SCHEMA_INVALID"]}
    for label in ("registry","challenges","receipts","rotations","highwater"):
        if not isinstance(data[label],list) or len(data[label])>65536:
            return {**HOLD,"reasons":["CAPTURE_LIST_INVALID:"+label]}
    registry=data["registry"];challenges=data["challenges"]
    receipts=data["receipts"];rotations=data["rotations"];hw=data["highwater"]
    registry_hash=sha(registry)
    for reason in validate(hw):errors.append("HIGHWATER_"+reason)
    if len(registry)!=3 or len({x.get("source_id") for x in registry if isinstance(x,dict)})!=3:
        errors.append("THREE_REGISTERED_SOURCES_REQUIRED")
    if len(receipts)!=3*len(challenges):
        errors.append("THREE_RECEIPTS_PER_CHALLENGE_VIOLATED")
    challenge_ids=set()
    for c in challenges:
        if not isinstance(c,dict):
            errors.append("CHALLENGE_ENTRY_INVALID");continue
        if c.get("nonce") in challenge_ids:errors.append("DUPLICATED_CHALLENGE")
        challenge_ids.add(c.get("nonce"))
    session_nonces=set();session_ids=set();group={}
    for r in receipts:
        if not isinstance(r,dict):errors.append("RECEIPT_ENTRY_INVALID");continue
        if r.get("nonce") in session_nonces or r.get("session") in session_ids:
            errors.append("DUPLICATED_SESSION")
        session_nonces.add(r.get("nonce"));session_ids.add(r.get("session"))
        key=r.get("challenge")
        if key not in challenge_ids:errors.append("ORPHAN_RECEIPT")
        group.setdefault(key,set()).add(r.get("source"))
    for c in challenges:
        if isinstance(c,dict):
            if len(group.get(c.get("nonce"),set()))!=3:
                errors.append("INCOMPLETE_SOURCE_TRIPLE")
    if hw:
        tip=hw[-1]
        if tip["registry_sha"]!=registry_hash:errors.append("REGISTRY_HIGHWATER_DIVERGENCE")
        for name,count in (("challenges",len(challenges)),("receipts",len(receipts)),("rotations",len(rotations))):
            if tip[name]>count:errors.append("RECOVERED_"+name.upper()+"_BELOW_HIGHWATER")
            if tip[name]<count:errors.append("HIGHWATER_"+name.upper()+"_LAGGING")
        if rotations and rotations[-1].get("next")!=registry_hash:
            errors.append("ROTATION_HEAD_REGISTRY_DIVERGENCE")
    else:errors.append("HIGHWATER_EMPTY")
    if not hex64(expected_anchor_sha):
        errors.append("EXTERNAL_ANCHOR_DIGEST_REQUIRED")
    elif not isinstance(anchor,dict) or set(anchor)!={"schema","minimum_seq","head_sha256","minimum_run_id","custodian_claim"}:
        errors.append("EXTERNAL_ANCHOR_SCHEMA_INVALID")
    else:
        if sha(anchor)!=expected_anchor_sha:errors.append("EXTERNAL_ANCHOR_PIN_CONFLICT")
        if anchor["schema"]!=SCHEMA:errors.append("EXTERNAL_ANCHOR_VERSION_INVALID")
        if type(anchor["minimum_seq"]) is not int or type(anchor["minimum_run_id"]) is not int or anchor["minimum_seq"]<1:
            errors.append("EXTERNAL_ANCHOR_COUNTER_INVALID")
        elif len(hw)<anchor["minimum_seq"]:
            errors.append("EXTERNAL_HIGHWATER_ROLLBACK")
        elif hw[anchor["minimum_seq"]-1]["head_sha"]!=anchor["head_sha256"]:
            errors.append("ANCHORED_HISTORY_REWRITTEN")
        if hw and type(anchor["minimum_run_id"]) is int and hw[-1]["run_id"]<anchor["minimum_run_id"]:
            errors.append("RUN_ID_ROLLBACK")
    errors+=["CROSS_DATABASE_COMMIT_ATOMICITY_UNPROVEN",
             "EXTERNAL_ANCHOR_CUSTODY_UNVERIFIED",
             "SIGNER_ANCESTRY_UNVERIFIED"]
    return {**HOLD,"reasons":sorted(set(errors)),
            "observed":{"registry_sha256":registry_hash,"challenge_count":len(challenges),
                        "receipt_count":len(receipts),"rotation_count":len(rotations),
                        "highwater_entries":len(hw),"capture_sha256":sha(data)}}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--receipt-db",type=Path,required=True)
    p.add_argument("--highwater-db",type=Path,required=True)
    p.add_argument("--anchor",type=Path)
    p.add_argument("--trusted-anchor-sha256")
    p.add_argument("--out",type=Path)
    a=p.parse_args()
    try:
        snap=capture(a.receipt_db,a.highwater_db)
        anchor=json.loads(a.anchor.read_bytes()) if a.anchor else None
        result=reconcile(snap,anchor,a.trusted_anchor_sha256)
    except (OSError,ValueError,TypeError,KeyError,sqlite3.Error) as exc:
        result={**HOLD,"reasons":["INPUT_REJECTED:"+type(exc).__name__]}
    output=json.dumps(result,sort_keys=True,indent=2)+"\n"
    if a.out:
        a.out.parent.mkdir(parents=True,exist_ok=True)
        a.out.write_text(output,encoding="utf-8")
    print(output,end="")
    return 1
if __name__=="__main__":raise SystemExit(main())
