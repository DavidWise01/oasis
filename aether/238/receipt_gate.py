#!/usr/bin/env python3
"""AETHER-238: independently pinned Ed25519 receipt gate, read-only.

Input trust roots must arrive out of band. A successful signature check only
validates a receipt statement; custody ancestry and physical ACT stay HOLD.
"""
import argparse
import base64
import hashlib
import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

SCHEMA="AETHER-238/receipt-challenge-v1"
HEX64=re.compile(r"^[a-f0-9]{64}$")
HEX40=re.compile(r"^[a-f0-9]{40}$")
HOLD={"operational_authority":"HOLD","physical_qualification_percent":0,
      "physical_act_allowed":False,"independent_custody_authenticated":False}

def canonical(value):
    return json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=True,allow_nan=False).encode("utf-8")

def check(receipts,trust,consumed,verify_signature):
    failures=[]
    observed=[]
    if not isinstance(receipts,list) or not (1<=len(receipts)<=16):
        failures.append("RECEIPT_SET_INVALID")
        receipts=[]
    if not isinstance(trust,dict) or not trust:
        failures.append("EXTERNAL_TRUST_ROOTS_MISSING")
        trust={}
    if not isinstance(consumed,list):
        failures.append("NONCE_LEDGER_MISSING")
        consumed=[]
    if len(consumed)!=len(set(str(x) for x in consumed)):
        failures.append("NONCE_LEDGER_INVALID")
    seen_nonce=set()
    seen_root=set()
    pin=None
    for i,r in enumerate(receipts):
        if not isinstance(r,dict) or set(r)!={"statement","signature_b64","key_id"}:
            failures.append("RECEIPT_ENVELOPE_INVALID")
            continue
        s=r["statement"]
        key=r["key_id"]
        if not isinstance(s,dict) or not isinstance(key,str):
            failures.append("RECEIPT_STATEMENT_INVALID")
            continue
        expected={"schema","repository","pin_commit","source_sha256","challenge_id","nonce",
                  "issued_at","run_id","run_head","witness_root"}
        if set(s)!=expected or s.get("schema")!="AETHER-238/receipt-statement-v1":
            failures.append("RECEIPT_STATEMENT_SCHEMA_MISMATCH")
            continue
        required_sha=[s.get("source_sha256")]
        if any(not isinstance(v,str) or not HEX64.fullmatch(v) for v in required_sha) or any(
            not isinstance(s.get(k),str) or not HEX40.fullmatch(s[k])
            for k in ("pin_commit","run_head")):
            failures.append("RECEIPT_DIGEST_OR_COMMIT_INVALID")
        if s.get("repository")!="DavidWise01/oasis" or type(s.get("run_id")) is not int or s["run_id"]<=0:
            failures.append("RECEIPT_RUN_BINDING_INVALID")
        if not all(isinstance(s.get(k),str) and s[k] and len(s[k])<=128 for k in ("challenge_id","nonce","issued_at","witness_root")):
            failures.append("RECEIPT_CHALLENGE_INVALID")
        nonce=s.get("nonce")
        if nonce in seen_nonce or nonce in consumed:
            failures.append("NONCE_REPLAY_OR_DUPLICATION")
        seen_nonce.add(nonce)
        root=s.get("witness_root")
        if root in seen_root:
            failures.append("WITNESS_ROOT_DUPLICATE")
        seen_root.add(root)
        if pin is None:
            pin=tuple(s.get(k) for k in ("pin_commit","source_sha256","challenge_id","run_id","run_head"))
        elif tuple(s.get(k) for k in ("pin_commit","source_sha256","challenge_id","run_id","run_head"))!=pin:
            failures.append("CROSS_RECEIPT_BINDING_MISMATCH")
        record=trust.get(key)
        if not isinstance(record,dict) or record.get("witness_root")!=root or not isinstance(record.get("public_key_pem"),str):
            failures.append("UNTRUSTED_KEY_OR_ROOT")
            continue
        try:
            signature=base64.b64decode(r["signature_b64"],validate=True)
            if len(signature)!=64:raise ValueError("SIGNATURE_LENGTH")
            ok=verify_signature(record["public_key_pem"],canonical(s),signature)
        except (ValueError,TypeError,KeyError):
            ok=False
        if not ok:failures.append("SIGNATURE_INVALID")
        observed.append({"key_id":key,"witness_root":root,"statement_sha256":hashlib.sha256(canonical(s)).hexdigest(),
                         "signature_valid":bool(ok)})
    if len(seen_root)<3:failures.append("THREE_DISTINCT_WITNESS_ROOTS_NOT_OBSERVED")
    # Even three key identifiers may be under one controller; no custody promoted.
    if not failures:failures.append("INDEPENDENT_CONTROLLER_CUSTODY_AND_PRERUN_TIME_UNVERIFIED")
    return {"schema":SCHEMA,"verdict":"REJECT_OR_UNVERIFIED",
            "reasons":sorted(set(failures)),"observed":observed,**HOLD}

def openssl_verify(pem,message,signature):
    if not shutil.which("openssl"):return False
    with tempfile.TemporaryDirectory() as td:
        td=Path(td)
        (td/"pub.pem").write_text(pem,encoding="utf-8")
        (td/"msg").write_bytes(message)
        (td/"sig").write_bytes(signature)
        cmd=["openssl","pkeyutl","-verify","-pubin","-inkey",str(td/"pub.pem"),
             "-rawin","-in",str(td/"msg"),"-sigfile",str(td/"sig")]
        return subprocess.run(cmd,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,
                              timeout=5,check=False).returncode==0

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--receipts",type=Path,required=True)
    ap.add_argument("--trust-roots",type=Path,required=True)
    ap.add_argument("--consumed-nonces",type=Path,required=True)
    ap.add_argument("--out",type=Path)
    a=ap.parse_args()
    try:
        data=[]
        for p in (a.receipts,a.trust_roots,a.consumed_nonces):
            raw=p.read_bytes()
            if len(raw)>256*1024:raise ValueError("INPUT_TOO_LARGE")
            data.append(json.loads(raw))
        output=check(*data,openssl_verify)
    except (OSError,ValueError,TypeError) as e:
        output={"schema":SCHEMA,"verdict":"REJECT_OR_UNVERIFIED",
                "reasons":["INPUT_UNAVAILABLE_OR_INVALID:"+type(e).__name__],
                "observed":[],**HOLD}
    rendered=json.dumps(output,indent=2,sort_keys=True)+"\n"
    if a.out:
        a.out.parent.mkdir(parents=True,exist_ok=True)
        a.out.write_text(rendered,encoding="utf-8")
    print(rendered,end="")
    return 1  # No physical authority, even when statement signatures verify.

if __name__=="__main__":
    raise SystemExit(main())
