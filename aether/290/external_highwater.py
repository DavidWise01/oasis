#!/usr/bin/env python3
"""AETHER-290-RS: external high-water record acquisition and ancestry evidence.

Network authentication, pinned signatures and retained bytes do not establish
independent immutable custody or trusted remote time. Always authority HOLD.
"""
import argparse,base64,hashlib,json,sqlite3,sys
from pathlib import Path
from urllib.parse import urlsplit
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"264"),str(ROOT/"289")]
from acquisition import acquire,validate_url
from remote_readback import ack_state,observation,canon,sha,digest
SCHEMA="AETHER-290/external-highwater-v1"
RECORD_SCHEMA="AETHER-290/retention-record-v1"
ZERO="0"*64
HOLD={"verdict":"REJECT_OR_UNVERIFIED","operational_authority":"HOLD",
      "physical_act_allowed":False,"physical_qualification_percent":0,
      "independent_external_custody_verified":False,
      "immutable_remote_retention_verified":False}
FIELDS={"schema","endpoint_id","controller_id","challenge_nonce",
        "ack_batch_id","ack_head_sha256","ack_nonce_count",
        "source_artifact_sha256","retained_until_claim","signature_b64"}
def hex64(x):return isinstance(x,str) and len(x)==64 and all(k in "0123456789abcdef" for k in x)
def verify(pem,obj,signature):
    try:
        from cryptography.exceptions import InvalidSignature
        from cryptography.hazmat.primitives import serialization
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
        key=serialization.load_pem_public_key(pem.encode("ascii"))
        sig=base64.b64decode(signature,validate=True)
        if not isinstance(key,Ed25519PublicKey) or len(sig)!=64:return False
        key.verify(sig,canon(obj))
        return True
    except (ImportError,InvalidSignature,ValueError,TypeError,UnicodeError):
        return False
def family(name,graph):
    seen=set();active=set()
    def visit(n):
        if not isinstance(n,str) or not n or n not in graph:raise ValueError("ANCESTRY_MISSING")
        if n in active:raise ValueError("ANCESTRY_CYCLE")
        if n in seen:return
        active.add(n);seen.add(n)
        if len(seen)>256:raise ValueError("ANCESTRY_LIMIT")
        parents=graph[n]
        if not isinstance(parents,list) or len(parents)>16:raise ValueError("ANCESTRY_INVALID")
        for p in parents:visit(p)
        active.remove(n)
    visit(name)
    return seen
def open_db(path):
    db=sqlite3.connect(str(path),timeout=10,isolation_level=None)
    db.execute("PRAGMA journal_mode=WAL")
    db.execute("PRAGMA synchronous=FULL")
    db.execute("PRAGMA foreign_keys=ON")
    db.execute("PRAGMA busy_timeout=10000")
    return db
def initialize(path):
    db=open_db(path)
    try:
        db.execute("BEGIN IMMEDIATE")
        db.execute("CREATE TABLE IF NOT EXISTS batch (seq INTEGER PRIMARY KEY,challenge_nonce TEXT NOT NULL UNIQUE,previous_head TEXT NOT NULL,head TEXT NOT NULL UNIQUE,trust_sha TEXT NOT NULL,ack_seq INTEGER NOT NULL,ack_head TEXT NOT NULL,ack_nonces INTEGER NOT NULL,artifact_sha TEXT NOT NULL,manifest_json TEXT NOT NULL)")
        db.execute("CREATE TABLE IF NOT EXISTS record_nonce (nonce TEXT PRIMARY KEY,batch_seq INTEGER NOT NULL REFERENCES batch(seq),endpoint_id TEXT NOT NULL,UNIQUE(batch_seq,endpoint_id))")
        db.commit()
    except Exception:db.rollback();raise
    finally:db.close()
def expected_ack(db):
    entries,nonces=ack_state(db)
    if not entries or len(nonces)!=3*len(entries):
        raise ValueError("ACK_HISTORY_INCOMPLETE")
    prev=ZERO
    for i,entry in enumerate(entries,1):
        if entry["id"]!=i or entry["previous"]!=prev:raise ValueError("ACK_CHAIN_LINK_INVALID")
        try:
            data=json.loads(entry["manifest"])
        except ValueError as e:raise ValueError("ACK_MANIFEST_INVALID") from e
        if sha(data)!=entry["head"]:raise ValueError("ACK_HEAD_DIGEST_INVALID")
        prev=entry["head"]
    return entries[-1]["id"],entries[-1]["head"],len(nonces)
def verify_claim(claim,key_id,trust,challenge,ack_tuple,artifact_sha):
    if not isinstance(claim,dict) or set(claim)!=FIELDS:raise ValueError("RECORD_SCHEMA_INVALID")
    if claim["schema"]!=RECORD_SCHEMA or claim["endpoint_id"]!=key_id or claim["challenge_nonce"]!=challenge:
        raise ValueError("RECORD_BINDING_INVALID")
    seq,head,count=ack_tuple
    if (type(claim["ack_batch_id"]) is not int or claim["ack_batch_id"]!=seq or
        claim["ack_head_sha256"]!=head or type(claim["ack_nonce_count"]) is not int
        or claim["ack_nonce_count"]!=count or claim["source_artifact_sha256"]!=artifact_sha):
        raise ValueError("RECORD_HIGHWATER_CONFLICT")
    if not isinstance(claim["retained_until_claim"],str) or not claim["retained_until_claim"] or len(claim["retained_until_claim"])>128:
        raise ValueError("RETENTION_CLAIM_INVALID")
    pinned=trust["endpoints"].get(key_id)
    if not isinstance(pinned,dict) or set(pinned)!={"controller_id","public_key_pem"} or pinned["controller_id"]!=claim["controller_id"]:
        raise ValueError("SIGNER_KEY_PIN_MISMATCH")
    signed={k:v for k,v in claim.items() if k!="signature_b64"}
    if not verify(pinned["public_key_pem"],signed,claim["signature_b64"]):
        raise ValueError("RETENTION_SIGNATURE_INVALID")
    return claim["challenge_nonce"]+":"+claim["endpoint_id"]
def check_ancestry(trust):
    graph=trust["controller_ancestry"]
    journal=family(trust["journal_controller"],graph)
    families=[]
    for info in trust["endpoints"].values():
        f=family(info["controller_id"],graph)
        if f & journal:raise ValueError("SHARED_JOURNAL_ANCESTRY")
        for other in families:
            if f & other:raise ValueError("SHARED_ENDPOINT_ANCESTRY")
        families.append(f)
def capture(path,ack_db,trust,pin,urls,challenge,artifact_sha,collector=acquire):
    if not hex64(pin) or sha(trust)!=pin:raise ValueError("TRUST_ROOT_PIN_INVALID")
    if not hex64(artifact_sha):raise ValueError("ARTIFACT_DIGEST_INVALID")
    if not isinstance(challenge,str) or not 16<=len(challenge)<=128:
        raise ValueError("CHALLENGE_INVALID")
    if (not isinstance(trust,dict) or set(trust)!={"endpoints","controller_ancestry","journal_controller"} or
        not isinstance(trust["endpoints"],dict) or len(trust["endpoints"])!=3 or
        not isinstance(urls,dict) or set(urls)!=set(trust["endpoints"])):
        raise ValueError("THREE_ENDPOINTS_REQUIRED")
    hosts=set()
    for url in urls.values():
        host,_=validate_url(url,[urlsplit(url).hostname])
        if host in hosts:raise ValueError("REUSED_HOST")
        hosts.add(host)
    check_ancestry(trust)
    target=expected_ack(ack_db)
    initialize(path)
    db=open_db(path)
    try:
        db.execute("BEGIN IMMEDIATE")
        if db.execute("SELECT 1 FROM batch WHERE challenge_nonce=?",(challenge,)).fetchone():
            raise ValueError("CHALLENGE_REPLAY")
        prior=db.execute("SELECT seq,head FROM batch ORDER BY seq DESC LIMIT 1").fetchone()
        previous=prior[1] if prior else ZERO
        seq=prior[0]+1 if prior else 1
        claims=[];observations=[]
        for kid in sorted(urls):
            url=urls[kid];host,_=validate_url(url,[urlsplit(url).hostname])
            obs=collector(url,[host])
            raw,normalized=observation(obs,url)
            if len(raw)>65536:raise ValueError("RECORD_TOO_LARGE")
            try:claim=json.loads(raw)
            except (UnicodeError,ValueError) as e:raise ValueError("RECORD_JSON_INVALID") from e
            if canon(claim)!=raw:raise ValueError("RAW_NOT_CANONICAL")
            verify_claim(claim,kid,trust,challenge,target,artifact_sha)
            nonce=claim["challenge_nonce"]+":"+kid
            if db.execute("SELECT 1 FROM record_nonce WHERE nonce=?",(nonce,)).fetchone():
                raise ValueError("RECORD_NONCE_REPLAY")
            claims.append(claim)
            observations.append({"endpoint_id":kid,"url":url,"observation":normalized})
        manifest={"schema":SCHEMA,"challenge_nonce":challenge,
                  "previous_head_sha256":previous,"trust_sha256":pin,
                  "ack_batch_id":target[0],"ack_head_sha256":target[1],
                  "ack_nonce_count":target[2],"artifact_sha256":artifact_sha,
                  "acquisitions":observations}
        head=sha(manifest)
        db.execute("INSERT INTO batch VALUES (?,?,?,?,?,?,?,?,?,?)",
                   (seq,challenge,previous,head,pin,target[0],target[1],target[2],artifact_sha,canon(manifest).decode()))
        for claim in claims:
            db.execute("INSERT INTO record_nonce VALUES (?,?,?)",
                       (challenge+":"+claim["endpoint_id"],seq,claim["endpoint_id"]))
        db.commit()
        return {**HOLD,"batch_sequence":seq,"head_sha256":head,
                "retention_signatures_verified":3,
                "reasons":["CLAIMED_CUSTODIAN_ANCESTRY_NOT_INDEPENDENTLY_ATTESTED",
                           "RETENTION_METADATA_IS_SIGNED_CLAIM_NOT_OBSERVED_STORAGE",
                           "REMOTE_IMMUTABILITY_UNVERIFIED"]}
    except Exception:db.rollback();raise
    finally:db.close()
def audit(path,ack_db,prefix_seq=None,prefix_hash=None):
    target=expected_ack(ack_db)
    db=sqlite3.connect(Path(path).resolve().as_uri()+"?mode=ro",uri=True,isolation_level=None)
    try:
        db.execute("PRAGMA query_only=ON");db.execute("BEGIN")
        batches=[dict(zip(("seq","challenge_nonce","previous_head","head","trust_sha","ack_seq","ack_head","ack_nonces","artifact_sha","manifest_json"),r))
                 for r in db.execute("SELECT seq,challenge_nonce,previous_head,head,trust_sha,ack_seq,ack_head,ack_nonces,artifact_sha,manifest_json FROM batch ORDER BY seq")]
        nonces=[dict(zip(("nonce","batch_seq","endpoint_id"),r))
                for r in db.execute("SELECT nonce,batch_seq,endpoint_id FROM record_nonce ORDER BY batch_seq,endpoint_id")]
        db.commit()
    finally:db.close()
    reasons=[];prev=ZERO
    for i,row in enumerate(batches,1):
        if row["seq"]!=i or row["previous_head"]!=prev:reasons.append("CHAIN_SEQUENCE_INVALID")
        try:
            manifest=json.loads(row["manifest_json"])
            if canon(manifest).decode()!=row["manifest_json"] or sha(manifest)!=row["head"]:
                reasons.append("MANIFEST_HEAD_INVALID")
            if (manifest["previous_head_sha256"]!=row["previous_head"] or
                manifest["ack_head_sha256"]!=row["ack_head"] or
                manifest["ack_nonce_count"]!=row["ack_nonces"] or
                manifest["trust_sha256"]!=row["trust_sha"] or
                manifest["artifact_sha256"]!=row["artifact_sha"]):
                reasons.append("MANIFEST_ROW_DIVERGENCE")
            observed=set()
            for entry in manifest["acquisitions"]:
                raw,_=observation(entry["observation"],entry["url"])
                claim=json.loads(raw)
                if claim["endpoint_id"]!=entry["endpoint_id"]:reasons.append("CLAIM_ENDPOINT_DIVERGENCE")
                observed.add((claim["challenge_nonce"]+":"+claim["endpoint_id"],claim["endpoint_id"]))
            actual={(r["nonce"],r["endpoint_id"]) for r in nonces if r["batch_seq"]==i}
            if len(observed)!=3 or observed!=actual:reasons.append("NONCE_MANIFEST_DIVERGENCE")
        except (KeyError,TypeError,ValueError,UnicodeError):
            reasons.append("MANIFEST_PREIMAGE_INVALID")
        if row["ack_seq"]>target[0] or row["ack_nonces"]>target[2]:
            reasons.append("ACK_HIGHWATER_ROLLBACK")
        prev=row["head"]
    if len(nonces)!=3*len(batches):reasons.append("NONCE_COUNT_INVALID")
    if prefix_seq is not None or prefix_hash is not None:
        if type(prefix_seq) is not int or prefix_seq<1 or not hex64(prefix_hash):
            reasons.append("PIN_FORMAT_INVALID")
        elif len(batches)<prefix_seq:reasons.append("ANCHORED_BATCH_REMOVED")
        elif batches[prefix_seq-1]["head"]!=prefix_hash:reasons.append("ANCHORED_BATCH_REWRITTEN")
    reasons.extend(["EXTERNAL_RETENTION_NOT_INDEPENDENTLY_OBSERVED",
                    "REMOTE_OBJECT_IMMUTABILITY_UNVERIFIED",
                    "WHOLE_DATABASE_ROLLBACK_POSSIBLE"])
    return {**HOLD,"batches":len(batches),"record_nonces":len(nonces),
            "latest_head_sha256":prev,"reasons":sorted(set(reasons))}
def main():
    p=argparse.ArgumentParser();s=p.add_subparsers(dest="operation",required=True)
    c=s.add_parser("capture")
    for name in ("db","ack-db","trust","endpoints"):c.add_argument("--"+name,type=Path,required=True)
    c.add_argument("--pin",required=True);c.add_argument("--challenge",required=True)
    c.add_argument("--artifact-sha256",required=True)
    a=s.add_parser("audit");a.add_argument("--db",type=Path,required=True)
    a.add_argument("--ack-db",type=Path,required=True);a.add_argument("--prefix-seq",type=int)
    a.add_argument("--prefix-sha256")
    args=p.parse_args()
    try:
        if args.operation=="capture":
            r=capture(args.db,args.ack_db,json.loads(args.trust.read_bytes()),args.pin,
                      json.loads(args.endpoints.read_bytes()),args.challenge,args.artifact_sha256)
        else:r=audit(args.db,args.ack_db,args.prefix_seq,args.prefix_sha256)
    except (OSError,ValueError,TypeError,KeyError,sqlite3.Error) as e:
        r={**HOLD,"reasons":["REJECTED:"+type(e).__name__+":"+str(e)[:96]]}
    print(json.dumps(r,sort_keys=True,indent=2))
    return 1
if __name__=="__main__":raise SystemExit(main())
