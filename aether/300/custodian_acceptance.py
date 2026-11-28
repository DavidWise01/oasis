#!/usr/bin/env python3
"""AETHER-300-RS: signed custodian handoff acknowledgments, local reconciliation.

Valid signatures from caller-pinned keys DO NOT certify independent key custody
or remote object retention. Every result remains operational HOLD.
"""
import argparse,base64,hashlib,json,sqlite3,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"299"),str(ROOT/"292")]
from handoff_qualification import audit_packet
from attestation_audit import verify as ed25519_verify
SCHEMA="AETHER-300/external-acceptance-v1"
ZERO="0"*64
HOLD={"verdict":"REJECT_OR_UNVERIFIED","operational_authority":"HOLD",
      "physical_act_allowed":False,"physical_qualification_percent":0,
      "independent_external_custody_verified":False,
      "remote_retention_verified":False,"custodian_key_ownership_independently_verified":False}
RECEIPT_FIELDS={"schema","custodian_id","handoff_sha256","source_head_sha256",
                "source_sequence","previous_receipt_sha256","receipt_nonce",
                "remote_object_id_claim","retained_until_claim","signature_b64"}
def canon(v):return json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=True,allow_nan=False).encode()
def digest(raw):return hashlib.sha256(raw).hexdigest()
def sha(v):return digest(canon(v))
def hex64(v):return isinstance(v,str) and len(v)==64 and all(c in "0123456789abcdef" for c in v)
def validate_pins(keys,keys_sha,ancestry,ancestry_sha,custodian):
    if (not isinstance(keys,dict) or set(keys)!={"custodian_id","public_key_pem"}
        or keys.get("custodian_id")!=custodian or not hex64(keys_sha) or sha(keys)!=keys_sha):
        raise ValueError("CUSTODIAN_KEY_PIN_MISMATCH")
    if (not isinstance(ancestry,dict) or set(ancestry)!={"journal_root","custodian_root","ancestors"}
        or not hex64(ancestry_sha) or sha(ancestry)!=ancestry_sha):
        raise ValueError("ANCESTRY_PIN_MISMATCH")
    graph=ancestry["ancestors"]
    if not isinstance(graph,dict):raise ValueError("ANCESTRY_GRAPH_INVALID")
    def visit(root):
        seen=set();active=set()
        def walk(node):
            if not isinstance(node,str) or not node or node not in graph:
                raise ValueError("ANCESTRY_NODE_UNKNOWN")
            if node in active:raise ValueError("ANCESTRY_CYCLE")
            if node in seen:return
            seen.add(node);active.add(node)
            parents=graph[node]
            if not isinstance(parents,list) or len(parents)>16 or len(seen)>256:
                raise ValueError("ANCESTRY_EDGES_INVALID")
            for parent in parents:walk(parent)
            active.remove(node)
        walk(root)
        return seen
    if visit(ancestry["journal_root"]) & visit(ancestry["custodian_root"]):
        raise ValueError("DECLARED_SHARED_SOURCE_ANCESTRY")
def verify_receipt(receipt,keys,expected):
    if not isinstance(receipt,dict) or set(receipt)!=RECEIPT_FIELDS:
        raise ValueError("RECEIPT_SCHEMA_INVALID")
    if receipt["schema"]!=SCHEMA or receipt["custodian_id"]!=keys["custodian_id"]:
        raise ValueError("RECEIPT_SIGNER_INVALID")
    for field,value in expected.items():
        if receipt.get(field)!=value:raise ValueError("RECEIPT_BINDING_INVALID:"+field)
    for field in ("receipt_nonce","remote_object_id_claim","retained_until_claim"):
        if not isinstance(receipt[field],str) or not 1<=len(receipt[field])<=256:
            raise ValueError("RECEIPT_CLAIM_INVALID")
    statement={k:v for k,v in receipt.items() if k!="signature_b64"}
    if not ed25519_verify(keys["public_key_pem"],statement,receipt["signature_b64"]):
        raise ValueError("RECEIPT_SIGNATURE_INVALID")
def read(path):
    db=sqlite3.connect(Path(path).resolve().as_uri()+"?mode=ro",uri=True,isolation_level=None)
    try:
        db.execute("PRAGMA query_only=ON");db.execute("BEGIN")
        rows=list(db.execute("SELECT seq,nonce,previous_head,head,manifest FROM acceptance ORDER BY seq"))
        db.commit()
        return rows
    finally:db.close()
def init(path):
    db=sqlite3.connect(str(path),timeout=10,isolation_level=None)
    try:
        db.execute("PRAGMA journal_mode=WAL");db.execute("PRAGMA synchronous=FULL")
        db.execute("BEGIN IMMEDIATE")
        db.execute("CREATE TABLE IF NOT EXISTS acceptance(seq INTEGER PRIMARY KEY,nonce TEXT NOT NULL UNIQUE,previous_head TEXT NOT NULL,head TEXT NOT NULL UNIQUE,manifest TEXT NOT NULL)")
        db.commit()
    except Exception:db.rollback();raise
    finally:db.close()
def record(path,handoff_path,source_db,receipt,keys,keys_sha,ancestry,ancestry_sha):
    packet=audit_packet(handoff_path,source_db)
    raw=Path(handoff_path).read_bytes()
    packet_obj=json.loads(raw)
    validate_pins(keys,keys_sha,ancestry,ancestry_sha,keys["custodian_id"])
    if packet_obj["recipient_claim"]!=keys["custodian_id"]:
        raise ValueError("HANDOFF_RECIPIENT_DIFFERENT")
    if packet_obj["declared_source_ancestry_sha256"]!=ancestry_sha:
        raise ValueError("HANDOFF_ANCESTRY_PIN_CONFLICT")
    init(path)
    db=sqlite3.connect(str(path),timeout=10,isolation_level=None)
    try:
        db.execute("PRAGMA busy_timeout=10000");db.execute("BEGIN IMMEDIATE")
        previous=db.execute("SELECT seq,head,manifest FROM acceptance ORDER BY seq DESC LIMIT 1").fetchone()
        seq=previous[0]+1 if previous else 1
        prior_head=previous[1] if previous else ZERO
        prior_receipt=sha(json.loads(previous[2])["receipt"]) if previous else ZERO
        expected={"handoff_sha256":digest(raw),
                  "source_head_sha256":packet_obj["source_head_sha256"],
                  "source_sequence":packet_obj["source_sequence"],
                  "previous_receipt_sha256":prior_receipt}
        verify_receipt(receipt,keys,expected)
        if db.execute("SELECT 1 FROM acceptance WHERE nonce=?",(receipt["receipt_nonce"],)).fetchone():
            raise ValueError("RECEIPT_NONCE_REPLAY")
        manifest={"schema":SCHEMA,"sequence":seq,"previous_head_sha256":prior_head,
                  "handoff_sha256":digest(raw),"custodian_key_pin_sha256":keys_sha,
                  "source_ancestry_pin_sha256":ancestry_sha,"receipt":receipt}
        head=sha(manifest)
        db.execute("INSERT INTO acceptance VALUES (?,?,?,?,?)",
                   (seq,receipt["receipt_nonce"],prior_head,head,canon(manifest).decode()))
        db.commit()
        return {**HOLD,"acceptance_sequence":seq,"ledger_head_sha256":head,
                "receipt_signature_verified":True,
                "reasons":["PUBLIC_KEY_OWNERSHIP_NOT_INDEPENDENTLY_ESTABLISHED",
                           "SIGNED_ACCEPTANCE_NOT_REMOTE_RETRIEVAL_PROOF",
                           "EXTERNAL_RETENTION_NOT_WITNESSED"]}
    except Exception:db.rollback();raise
    finally:db.close()
def audit(path,handoff_path=None,source_db=None,keys=None,keys_sha=None,
          ancestry=None,ancestry_sha=None,external_seq=None,external_head=None):
    rows=read(path);errors=[];previous=ZERO;prior_receipt=ZERO;nonces=set()
    packet=None
    if handoff_path is not None:
        audit_packet(handoff_path,source_db)
        packet=json.loads(Path(handoff_path).read_bytes())
        packet_sha=digest(Path(handoff_path).read_bytes())
    if keys is not None:
        validate_pins(keys,keys_sha,ancestry,ancestry_sha,keys["custodian_id"])
    for index,(seq,nonce,parent,head,text) in enumerate(rows,1):
        if seq!=index or parent!=previous:errors.append("ACCEPTANCE_CHAIN_INVALID")
        try:
            manifest=json.loads(text);receipt=manifest["receipt"]
            if canon(manifest).decode()!=text or sha(manifest)!=head:
                errors.append("ACCEPTANCE_HEAD_INVALID")
            if (manifest["schema"]!=SCHEMA or manifest["sequence"]!=seq or
                manifest["previous_head_sha256"]!=parent or receipt["receipt_nonce"]!=nonce):
                errors.append("ACCEPTANCE_ROW_MISMATCH")
            if nonce in nonces:errors.append("RECEIPT_NONCE_REPLAY")
            nonces.add(nonce)
            if receipt["previous_receipt_sha256"]!=prior_receipt:
                errors.append("RECEIPT_PREDECESSOR_INVALID")
            if receipt["handoff_sha256"]!=manifest["handoff_sha256"]:
                errors.append("RECEIPT_HANDOFF_HASH_CONFLICT")
            if keys is not None:
                if manifest["custodian_key_pin_sha256"]!=keys_sha or manifest["source_ancestry_pin_sha256"]!=ancestry_sha:
                    errors.append("HISTORICAL_TRUST_PIN_CHANGED")
                try:verify_receipt(receipt,keys,{"handoff_sha256":manifest["handoff_sha256"],
                    "previous_receipt_sha256":prior_receipt})
                except (KeyError,ValueError,TypeError):errors.append("RETAINED_RECEIPT_SIGNATURE_INVALID")
            if packet is not None:
                if (receipt["handoff_sha256"]!=packet_sha or
                    receipt["source_head_sha256"]!=packet["source_head_sha256"] or
                    receipt["source_sequence"]!=packet["source_sequence"]):
                    errors.append("HANDOFF_ANCESTRY_DIVERGENCE")
            prior_receipt=sha(receipt)
        except (KeyError,ValueError,TypeError,UnicodeError):
            errors.append("RETAINED_ACCEPTANCE_INVALID")
        previous=head
    if external_seq is not None or external_head is not None:
        if type(external_seq) is not int or external_seq<1 or not hex64(external_head):
            errors.append("EXTERNAL_HIGHWATER_PIN_INVALID")
        elif len(rows)<external_seq:errors.append("EXTERNAL_HIGHWATER_ROLLBACK")
        elif rows[external_seq-1][3]!=external_head:errors.append("EXTERNAL_HIGHWATER_REWRITE")
    errors.extend(["INDEPENDENT_CUSTODIAN_OWNERSHIP_UNVERIFIED",
                   "REMOTE_RETENTION_READBACK_UNVERIFIED",
                   "LOCAL_LEDGER_AND_LOCAL_PIN_CAN_ROLL_BACK"])
    return {**HOLD,"acceptances":len(rows),"latest_head_sha256":previous,
            "reasons":sorted(set(errors))}
def main():
    p=argparse.ArgumentParser();subs=p.add_subparsers(dest="op",required=True)
    c=subs.add_parser("record")
    for arg in ("db","handoff","source-db","receipt","keys","ancestry"):
        c.add_argument("--"+arg,type=Path,required=True)
    c.add_argument("--keys-sha256",required=True);c.add_argument("--ancestry-sha256",required=True)
    a=subs.add_parser("audit")
    a.add_argument("--db",type=Path,required=True);a.add_argument("--handoff",type=Path)
    a.add_argument("--source-db",type=Path);a.add_argument("--keys",type=Path)
    a.add_argument("--keys-sha256");a.add_argument("--ancestry",type=Path)
    a.add_argument("--ancestry-sha256");a.add_argument("--external-seq",type=int)
    a.add_argument("--external-head")
    o=p.parse_args()
    try:
        if o.op=="record":
            result=record(o.db,o.handoff,o.source_db,json.loads(o.receipt.read_bytes()),
                          json.loads(o.keys.read_bytes()),o.keys_sha256,
                          json.loads(o.ancestry.read_bytes()),o.ancestry_sha256)
        else:result=audit(o.db,o.handoff,o.source_db,
                          json.loads(o.keys.read_bytes()) if o.keys else None,o.keys_sha256,
                          json.loads(o.ancestry.read_bytes()) if o.ancestry else None,
                          o.ancestry_sha256,o.external_seq,o.external_head)
    except (ValueError,OSError,KeyError,TypeError,sqlite3.Error) as exc:
        result={**HOLD,"reasons":["REJECTED:"+type(exc).__name__+":"+str(exc)[:100]]}
    print(json.dumps(result,sort_keys=True,indent=2))
    return 1
if __name__=="__main__":raise SystemExit(main())
