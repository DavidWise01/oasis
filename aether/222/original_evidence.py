#!/usr/bin/env python3
"""AETHER-222: independent-origin challenge evidence, file-backed verification.

No network calls or guessed authority. Exact receipt/capture bytes must be
supplied from outside the owned source. This checks byte integrity and replay;
controller independence, actual device origin, and signatures are NOT proved.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

SCHEMA="AETHER-222/original-evidence-challenge-v1"
HEX64=re.compile(r"^[a-f0-9]{64}$")
HOLD={"physical_qualification_percent":0,"operational_authority":"HOLD",
      "physical_act_allowed":False,"may_recover":False,"may_repair":False,
      "may_reclaim_lock":False,"independently_authenticated_external_custodians":0,
      "original_physical_captures_authenticated":0}
FIELDS=("source_root","source_operator","source_administrator",
        "holder_root","holder_operator","holder_administrator",
        "issuer_root","issuer_operator","issuer_administrator")

def sha256(v:bytes)->str:
 return hashlib.sha256(v).hexdigest()

def valid_hash(value:object)->bool:
 return isinstance(value,str) and HEX64.fullmatch(value) is not None

def evaluate(record:dict,receipt_bytes:bytes|None,capture_bytes:bytes|None,
             prior_nonces:set[str]|None=None)->dict:
 issues:set[str]=set()
 if record.get("schema")!=SCHEMA:issues.add("CHALLENGE_SCHEMA_INVALID")
 for k in FIELDS:
  if not isinstance(record.get(k),str) or not record[k].strip():
   issues.add("CONTROL_ANCESTRY_MISSING")
 for a,b in (("source_root","holder_root"),("source_root","issuer_root"),("holder_root","issuer_root"),
             ("source_operator","holder_operator"),("source_operator","issuer_operator"),("holder_operator","issuer_operator"),
             ("source_administrator","holder_administrator"),("source_administrator","issuer_administrator"),
             ("holder_administrator","issuer_administrator")):
  if record.get(a) and record.get(a)==record.get(b):
   issues.add("SHARED_CONTROL_ANCESTRY")
 nonce=record.get("nonce")
 if not isinstance(nonce,str) or len(nonce)<16:
  issues.add("CHALLENGE_NONCE_INVALID")
 if isinstance(nonce,str) and prior_nonces is not None and nonce in prior_nonces:
  issues.add("CHALLENGE_NONCE_REPLAY")
 if not isinstance(record.get("enrollment_id"),str) or not record["enrollment_id"].strip():
  issues.add("ENROLLMENT_BINDING_MISSING")
 if not isinstance(record.get("receipt_id"),str) or not record["receipt_id"].strip():
  issues.add("RECEIPT_ID_MISSING")
 if not valid_hash(record.get("holder_key_sha256")):
  issues.add("HOLDER_KEY_PIN_INVALID")
 if not valid_hash(record.get("receipt_sha256")):
  issues.add("RECEIPT_DIGEST_INVALID")
 if not valid_hash(record.get("capture_sha256")):
  issues.add("CAPTURE_DIGEST_INVALID")
 if receipt_bytes is None:
  issues.add("EXTERNAL_RECEIPT_BYTES_UNAVAILABLE")
 elif sha256(receipt_bytes)!=record.get("receipt_sha256"):
  issues.add("EXTERNAL_RECEIPT_DIGEST_MISMATCH")
 if capture_bytes is None:
  issues.add("ORIGINAL_CAPTURE_BYTES_UNAVAILABLE")
 elif sha256(capture_bytes)!=record.get("capture_sha256"):
  issues.add("ORIGINAL_CAPTURE_DIGEST_MISMATCH")
 if isinstance(receipt_bytes,bytes):
  try:
   receipt=json.loads(receipt_bytes)
   if not isinstance(receipt,dict):raise ValueError("receipt must be object")
   bindings=("enrollment_id","receipt_id","nonce","holder_key_sha256","capture_sha256")
   if any(receipt.get(k)!=record.get(k) for k in bindings):
    issues.add("RECEIPT_CHALLENGE_BINDING_MISMATCH")
   if receipt.get("operational_authority")!="HOLD" or receipt.get("physical_act_allowed") is not False:
    issues.add("RECEIPT_AUTHORITY_PROMOTION")
  except (ValueError,UnicodeError):
   issues.add("RECEIPT_JSON_INVALID")
 # A signature string is not a verification. A remote locator is not a retrieval.
 if record.get("signature_verification")!="NOT_PERFORMED":
  issues.add("SIGNATURE_VERIFICATION_MISREPRESENTED")
 if record.get("custodian_authentication")!="NOT_PERFORMED":
  issues.add("CUSTODIAN_AUTHENTICATION_MISREPRESENTED")
 if record.get("original_device_authentication")!="NOT_PERFORMED":
  issues.add("DEVICE_ORIGIN_AUTHENTICATION_MISREPRESENTED")
 if any(record.get(x) is not False for x in ("may_recover","may_repair","physical_act_allowed")) or record.get("operational_authority")!="HOLD":
  issues.add("OPERATIONAL_AUTHORITY_PROMOTION")
 reasons=sorted(issues)
 return {"schema":"AETHER-222/verification-result-v1",
  "verdict":"REJECT" if reasons else "DOCUMENTARY_BYTES_AND_BINDINGS_CONSISTENT_ONLY",
  "reasons":reasons if reasons else ["INDEPENDENT_CUSTODY_AND_ORIGINAL_DEVICE_ORIGIN_UNVERIFIED"],
  "receipt_observed_sha256":sha256(receipt_bytes) if receipt_bytes is not None else None,
  "capture_observed_sha256":sha256(capture_bytes) if capture_bytes is not None else None,
  "signature_verified":False,"remote_controller_authenticated":False,
  "original_device_authenticated":False,**HOLD}

def safe_read(path:Path|None,max_size:int=4*1024*1024)->bytes|None:
 if path is None:return None
 try:
  if not path.is_file() or path.stat().st_size>max_size:return None
  return path.read_bytes()
 except OSError:return None

def main()->int:
 parser=argparse.ArgumentParser(description="AETHER-222 file-backed documentary challenge verification")
 parser.add_argument("--record",required=True,type=Path)
 parser.add_argument("--receipt",type=Path)
 parser.add_argument("--capture",type=Path)
 parser.add_argument("--prior-nonces",type=Path)
 parser.add_argument("--out",type=Path)
 args=parser.parse_args()
 try:
  record=json.loads(args.record.read_text(encoding="utf-8"))
  if not isinstance(record,dict):raise ValueError("record must be object")
 except (OSError,ValueError,UnicodeError):
  record={}
 priors=None
 if args.prior_nonces is not None:
  try:
   ledger=json.loads(args.prior_nonces.read_text(encoding="utf-8"))
   if not isinstance(ledger,list) or not all(isinstance(x,str) for x in ledger):
    raise ValueError("invalid prior nonce list")
   priors=set(ledger)
  except (OSError,ValueError,UnicodeError):
   priors={record.get("nonce")} # fail closed: forcibly mark request as replay
 result=evaluate(record,safe_read(args.receipt),safe_read(args.capture),priors)
 output=json.dumps(result,sort_keys=True,indent=2)+"\n"
 if args.out is not None:
  args.out.parent.mkdir(parents=True,exist_ok=True)
  args.out.write_text(output,encoding="utf-8")
 print(output,end="")
 return 0 if result["verdict"]=="DOCUMENTARY_BYTES_AND_BINDINGS_CONSISTENT_ONLY" else 1

if __name__=="__main__":
 sys.exit(main())
