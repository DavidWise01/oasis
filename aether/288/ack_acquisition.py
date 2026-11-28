#!/usr/bin/env python3
"""AETHER-288: opt-in HTTPS acknowledgment acquisition, SQLite nonce fencing, HOLD."""
import argparse,base64,hashlib,json,sqlite3,sys
from pathlib import Path
from urllib.parse import urlsplit
root=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(root/"264"),str(root/"287"),str(root/"286")]
from acquisition import acquire,validate_url
from export_audit import audit as audit287,verify_export,sha,canonical
from atomic_manifest import readback
ZERO="0"*64
SCHEMA="AETHER-288/ack-acquisition-v1"
CORE=("schema","requested_url","host","pinned_ip","dns_address_count","tls_hostname_validation",
      "status","elapsed_ms","raw_length","raw_sha256","raw_b64")
GAPS={"CUSTODIAN_KEYS_AND_GRAPH_SELF_DECLARED","EXTERNAL_RAW_ACK_RETRIEVAL_NOT_PERFORMED",
      "EXTERNAL_RETENTION_NOT_OBSERVED","NONCE_HISTORY_NOT_EXTERNALLY_SEALED"}
HOLD={"verdict":"REJECT_OR_UNVERIFIED","operational_authority":"HOLD","physical_act_allowed":False,
      "physical_qualification_percent":0,"independent_custody_verified":False}
def hex64(x):return isinstance(x,str) and len(x)==64 and all(c in "0123456789abcdef" for c in x)
def raw_body(obs,url):
    host,_=validate_url(url,[urlsplit(url).hostname])
    if not isinstance(obs,dict) or any(k not in obs for k in CORE):raise ValueError("OBSERVATION_INCOMPLETE")
    fields={k:obs[k] for k in CORE}
    if (fields["schema"]!="AETHER-264/https-acquisition-v1" or fields["requested_url"]!=url or
        fields["host"]!=host or fields["tls_hostname_validation"] is not True or
        type(fields["status"]) is not int or fields["status"] not in (200,206)):
        raise ValueError("TRANSPORT_CLAIM_INVALID")
    raw=base64.b64decode(fields["raw_b64"],validate=True)
    if (len(raw)>65536 or type(fields["raw_length"]) is not int or
        len(raw)!=fields["raw_length"] or hashlib.sha256(raw).hexdigest()!=fields["raw_sha256"]):
        raise ValueError("RAW_BODY_INVALID")
    if obs.get("observation_sha256")!=sha(fields):raise ValueError("OBSERVATION_SHA_INVALID")
    return raw,{**fields,"observation_sha256":obs["observation_sha256"]}
def connect(path):
    db=sqlite3.connect(str(path),timeout=10,isolation_level=None)
    db.execute("PRAGMA busy_timeout=10000");db.execute("PRAGMA journal_mode=WAL")
    db.execute("PRAGMA synchronous=FULL");db.execute("PRAGMA foreign_keys=ON")
    return db
def init(path):
    db=connect(path)
    try:
        db.execute("BEGIN IMMEDIATE")
        db.execute("CREATE TABLE IF NOT EXISTS batch(id INTEGER PRIMARY KEY AUTOINCREMENT,nonce TEXT UNIQUE NOT NULL,previous TEXT NOT NULL,head TEXT UNIQUE NOT NULL,manifest TEXT NOT NULL)")
        db.execute("CREATE TABLE IF NOT EXISTS receipt(nonce TEXT PRIMARY KEY,batch INTEGER NOT NULL REFERENCES batch(id),custodian TEXT NOT NULL,UNIQUE(batch,custodian))")
        db.commit()
    except Exception:db.rollback();raise
    finally:db.close()
def capture(path,journal,artifact,trust,pin,urls,challenge,collector=acquire):
    if not hex64(pin) or sha(trust)!=pin:raise ValueError("TRUST_PIN_INVALID")
    if not isinstance(challenge,str) or not 16<=len(challenge)<=128:raise ValueError("CHALLENGE_INVALID")
    if (not isinstance(trust,dict) or set(trust)!={"journal_controller","controllers","custodians"}
        or not isinstance(trust["custodians"],dict) or len(trust["custodians"])!=3
        or not isinstance(urls,dict) or set(urls)!=set(trust["custodians"])):
        raise ValueError("THREE_PINNED_CUSTODIANS_REQUIRED")
    hosts=set()
    for url in urls.values():
        host,_=validate_url(url,[urlsplit(url).hostname])
        if host in hosts:raise ValueError("DUPLICATE_HOST")
        hosts.add(host)
    if verify_export(artifact,*readback(journal)):raise ValueError("EXPORT_PREIMAGE_INVALID")
    init(path);db=connect(path)
    try:
        db.execute("BEGIN IMMEDIATE")
        if db.execute("SELECT 1 FROM batch WHERE nonce=?",(challenge,)).fetchone():
            raise ValueError("CHALLENGE_REPLAY")
        last=db.execute("SELECT head FROM batch ORDER BY id DESC LIMIT 1").fetchone()
        prev=last[0] if last else ZERO
        claims=[];records=[];new_nonces=set()
        for kid in sorted(urls):
            url=urls[kid];host,_=validate_url(url,[urlsplit(url).hostname])
            raw,obs=raw_body(collector(url,[host]),url)
            claim=json.loads(raw)
            if canonical(claim)!=raw or claim.get("custodian_id")!=kid:
                raise ValueError("ACK_CANONICAL_OR_SOURCE_INVALID")
            nonce=claim.get("nonce")
            if (not isinstance(nonce,str) or not nonce or nonce==challenge or
                nonce in new_nonces or len(nonce)>128):
                raise ValueError("DUPLICATE_ACK_NONCE")
            if db.execute("SELECT 1 FROM receipt WHERE nonce=?",(nonce,)).fetchone():
                raise ValueError("PERSISTED_NONCE_REPLAY")
            new_nonces.add(nonce);claims.append(claim)
            records.append({"custodian_id":kid,"url":url,"observation":obs})
        consumed=[r[0] for r in db.execute("SELECT nonce FROM receipt ORDER BY nonce")]
        review=audit287(journal,artifact,{"trust":trust,"acknowledgments":claims,
                                         "consumed_nonces":consumed},pin)
        invalid=set(review["reasons"])-GAPS
        if invalid:raise ValueError("ACK_VALIDATION_FAILED:"+",".join(sorted(invalid))[:120])
        manifest={"schema":SCHEMA,"challenge_nonce":challenge,"previous_head_sha256":prev,
                  "trust_sha256":pin,"artifact_sha256":artifact["artifact_sha256"],
                  "acquisitions":records}
        head=sha(manifest)
        db.execute("INSERT INTO batch(nonce,previous,head,manifest) VALUES (?,?,?,?)",
                   (challenge,prev,head,canonical(manifest).decode()))
        bid=db.execute("SELECT last_insert_rowid()").fetchone()[0]
        for claim in claims:db.execute("INSERT INTO receipt VALUES (?,?,?)",
                                      (claim["nonce"],bid,claim["custodian_id"]))
        db.commit()
        return {**HOLD,"batch_id":bid,"head_sha256":head,"receipt_count":3,
                "reasons":sorted(GAPS)}
    except Exception:db.rollback();raise
    finally:db.close()
def audit(path,seq=None,pin=None):
    db=sqlite3.connect(Path(path).resolve().as_uri()+"?mode=ro",uri=True,isolation_level=None)
    try:
        db.execute("BEGIN")
        batches=[dict(zip(("id","nonce","previous","head","manifest"),r)) for r in db.execute("SELECT id,nonce,previous,head,manifest FROM batch ORDER BY id")]
        receipts=[dict(zip(("nonce","batch","custodian"),r)) for r in db.execute("SELECT nonce,batch,custodian FROM receipt ORDER BY batch,custodian")]
        db.commit()
    finally:db.close()
    errors=[];prev=ZERO
    for index,b in enumerate(batches,1):
        if b["id"]!=index or b["previous"]!=prev:errors.append("CHAIN_GAP")
        try:
            manifest=json.loads(b["manifest"])
            if canonical(manifest).decode()!=b["manifest"] or sha(manifest)!=b["head"]:
                errors.append("MANIFEST_HEAD_MISMATCH")
            if manifest["previous_head_sha256"]!=b["previous"] or manifest["challenge_nonce"]!=b["nonce"]:
                errors.append("MANIFEST_HEADER_MISMATCH")
            claims=set()
            for entry in manifest["acquisitions"]:
                raw,_=raw_body(entry["observation"],entry["url"])
                claim=json.loads(raw)
                if claim["custodian_id"]!=entry["custodian_id"]:errors.append("RETAINED_CUSTODIAN_INVALID")
                claims.add((claim["nonce"],claim["custodian_id"]))
            stored={(r["nonce"],r["custodian"]) for r in receipts if r["batch"]==index}
            if len(claims)!=3 or stored!=claims:errors.append("RECEIPT_MANIFEST_DIVERGENCE")
        except (ValueError,TypeError,KeyError,UnicodeError):
            errors.append("MANIFEST_INVALID")
        prev=b["head"]
    if len(receipts)!=3*len(batches):errors.append("NONCE_CONSERVATION_INVALID")
    if seq is not None or pin is not None:
        if type(seq) is not int or seq<1 or not hex64(pin):errors.append("PREFIX_PIN_INVALID")
        elif len(batches)<seq:errors.append("PREFIX_REMOVED")
        elif batches[seq-1]["head"]!=pin:errors.append("PREFIX_REPLACED")
    return {**HOLD,"batches":len(batches),"nonces":len(receipts),"latest_head_sha256":prev,
            "reasons":sorted(set(errors+["EXTERNAL_CUSTODY_NOT_AUTHENTICATED",
                                        "LOCAL_DATABASE_ROLLBACK_POSSIBLE"]))}
def main():
    p=argparse.ArgumentParser();sub=p.add_subparsers(dest="action",required=True)
    c=sub.add_parser("capture")
    for opt in ("db","journal","export","trust","endpoints"):c.add_argument("--"+opt,type=Path,required=True)
    c.add_argument("--pin",required=True);c.add_argument("--challenge",required=True)
    a=sub.add_parser("audit");a.add_argument("--db",type=Path,required=True)
    a.add_argument("--prefix-seq",type=int);a.add_argument("--prefix-sha")
    args=p.parse_args()
    try:
        if args.action=="capture":
            result=capture(args.db,args.journal,json.loads(args.export.read_bytes()),
                           json.loads(args.trust.read_bytes()),args.pin,
                           json.loads(args.endpoints.read_bytes()),args.challenge)
        else:result=audit(args.db,args.prefix_seq,args.prefix_sha)
    except (OSError,ValueError,TypeError,KeyError,sqlite3.Error) as e:
        result={**HOLD,"reasons":["REJECTED:"+type(e).__name__+":"+str(e)[:100]]}
    print(json.dumps(result,sort_keys=True,indent=2))
    return 1
if __name__=="__main__":raise SystemExit(main())
