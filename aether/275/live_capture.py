#!/usr/bin/env python3
"""AETHER-275-RS — opt-in live pinned HTTPS collection of keyring and signed records.

Pinned TLS shows what endpoint responded, not independent controller ancestry.
"""
import argparse,base64,hashlib,json,sys
from pathlib import Path
from urllib.parse import urlsplit

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"264"))
from acquisition import acquire

SCHEMA="AETHER-275/live-keyring-capture-v1"
HOLD={"verdict":"REJECT_OR_UNVERIFIED","operational_authority":"HOLD",
      "physical_act_allowed":False,"physical_qualification_percent":0,
      "independent_external_custody_proven":False}
MAX_BYTES=65536

def canon(x):
    return json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=True,allow_nan=False).encode()
def sha_bytes(data):return hashlib.sha256(data).hexdigest()
def sha(x):return sha_bytes(canon(x))
def valid_hex(x):
    return isinstance(x,str) and len(x)==64 and all(c in "0123456789abcdef" for c in x)
def host_of(url):
    p=urlsplit(url)
    if p.scheme!="https" or not p.hostname or p.username or p.password or p.fragment or p.port not in (None,443):
        raise ValueError("HTTPS_URL_INVALID")
    return p.hostname.lower().rstrip(".")
def body(obs):
    if not isinstance(obs,dict) or not isinstance(obs.get("raw_b64"),str):
        raise ValueError("OBSERVATION_INVALID")
    raw=base64.b64decode(obs["raw_b64"],validate=True)
    if len(raw)>MAX_BYTES or obs.get("raw_length")!=len(raw) or obs.get("raw_sha256")!=sha_bytes(raw):
        raise ValueError("RAW_BODY_TAMPER")
    return raw
def verify(pem,message,sig):
    try:
        from cryptography.exceptions import InvalidSignature
        from cryptography.hazmat.primitives import serialization
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
        key=serialization.load_pem_public_key(pem.encode("ascii"))
        if not isinstance(key,Ed25519PublicKey) or len(sig)!=64:return False
        key.verify(sig,message);return True
    except (ImportError,InvalidSignature,TypeError,ValueError,UnicodeError):
        return False
def keyring(raw,expected_digest):
    if not valid_hex(expected_digest) or sha_bytes(raw)!=expected_digest:
        raise ValueError("OUT_OF_BAND_KEYRING_PIN_MISMATCH")
    ring=json.loads(raw)
    if not isinstance(ring,dict) or set(ring)!={"schema","sources"} or ring["schema"]!="AETHER-275/keyring-v1":
        raise ValueError("KEYRING_SCHEMA_INVALID")
    sources=ring["sources"]
    if not isinstance(sources,list) or len(sources)!=3:raise ValueError("THREE_SOURCES_REQUIRED")
    ids=set();controllers=set();hosts=set()
    for s in sources:
        if not isinstance(s,dict) or set(s)!={"source_id","controller_claim","url","public_key_pem"}:
            raise ValueError("SOURCE_ENTRY_INVALID")
        for field in ("source_id","controller_claim","public_key_pem"):
            if not isinstance(s[field],str) or not s[field] or len(s[field])>4096:
                raise ValueError("SOURCE_FIELD_INVALID")
        host=host_of(s["url"])
        if s["source_id"] in ids or s["controller_claim"] in controllers or host in hosts:
            raise ValueError("SOURCE_LABEL_OR_HOST_REUSE")
        ids.add(s["source_id"]);controllers.add(s["controller_claim"]);hosts.add(host)
    return ring
def check_record(raw,s,challenge,validator=verify):
    try:
        data=json.loads(raw)
        if not isinstance(data,dict) or set(data)!={"schema","challenge_nonce","payload_b64","signature_b64"}:
            raise ValueError("RECORD_SCHEMA_INVALID")
        if data["schema"]!="AETHER-275/signed-record-v1" or data["challenge_nonce"]!=challenge:
            raise ValueError("CHALLENGE_BINDING_MISMATCH")
        blob=base64.b64decode(data["payload_b64"],validate=True)
        if len(blob)>MAX_BYTES:raise ValueError("PAYLOAD_TOO_LARGE")
        statement={"schema":"AETHER-275/signature-v1","source_id":s["source_id"],
                   "challenge_nonce":challenge,"payload_sha256":sha_bytes(blob)}
        sig=base64.b64decode(data["signature_b64"],validate=True)
        if not validator(s["public_key_pem"],canon(statement),sig):
            raise ValueError("SIGNATURE_INVALID")
        return {"source_id":s["source_id"],"payload_sha256":sha_bytes(blob),
                "record_sha256":sha_bytes(raw),"signature_verified_against_pin":True}
    except (KeyError,TypeError,UnicodeError,ValueError,json.JSONDecodeError) as error:
        raise ValueError("SIGNED_RECORD_REJECTED:"+str(error)[:80]) from error

def collect(keyring_url,expected_keyring_sha256,challenge,allowed_hosts,collector=acquire):
    """Live HTTPS only with explicit CLI opt-in; all network calls use 264 guard."""
    if not isinstance(challenge,str) or len(challenge)<16 or len(challenge)>128:
        raise ValueError("FRESH_CHALLENGE_REQUIRED")
    if not isinstance(allowed_hosts,list) or not allowed_hosts:
        raise ValueError("ALLOWLIST_REQUIRED")
    key_host=host_of(keyring_url)
    if key_host not in allowed_hosts:raise ValueError("KEYRING_HOST_NOT_ALLOWED")
    ring_obs=collector(keyring_url,[key_host])
    if ring_obs.get("requested_url")!=keyring_url:raise ValueError("KEYRING_URL_MISMATCH")
    ring=keyring(body(ring_obs),expected_keyring_sha256)
    observations=[];receipts=[]
    for source in ring["sources"]:
        host=host_of(source["url"])
        if host not in allowed_hosts:raise ValueError("SOURCE_HOST_NOT_ALLOWED")
        obs=collector(source["url"],[host])
        if obs.get("requested_url")!=source["url"]:raise ValueError("SOURCE_URL_MISMATCH")
        raw=body(obs)
        receipt=check_record(raw,source,challenge)
        observations.append(obs)
        receipts.append(receipt)
    hashes=[r["payload_sha256"] for r in receipts]
    return {**HOLD,"schema":SCHEMA,"challenge_nonce":challenge,
            "keyring_sha256":expected_keyring_sha256,
            "keyring_observation":ring_obs,"source_observations":observations,
            "signed_receipts":receipts,
            "payload_agreement":len(set(hashes))==1,
            "reasons":["AUTHENTICATED_TLS_NOT_INDEPENDENT_SOURCE_ANCESTRY",
                       "NO_INDEPENDENT_KEYRING_CUSTODY",
                       "CHALLENGE_REPLAY_LEDGER_NOT_EXTERNALLY_SEALED"]}
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--keyring-url",required=True)
    p.add_argument("--keyring-sha256",required=True)
    p.add_argument("--challenge",required=True)
    p.add_argument("--allow-host",action="append",required=True)
    p.add_argument("--out",type=Path)
    a=p.parse_args()
    try:
        result=collect(a.keyring_url,a.keyring_sha256,a.challenge,a.allow_host)
    except (OSError,ValueError,TypeError,UnicodeError) as error:
        result={**HOLD,"reasons":["ACQUISITION_REJECTED:"+type(error).__name__+":"+str(error)[:100]]}
    output=json.dumps(result,sort_keys=True,indent=2)+"\n"
    if a.out:
        a.out.parent.mkdir(parents=True,exist_ok=True)
        a.out.write_text(output,encoding="utf-8")
    print(output,end="")
    return 1
if __name__=="__main__":raise SystemExit(main())
