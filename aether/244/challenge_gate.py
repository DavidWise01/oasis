#!/usr/bin/env python3
"""AETHER-244-RS: offline signed challenge and controller-ancestry gate.

This tool never fetches network resources or grants operational authority.
"""
import argparse,base64,hashlib,ipaddress,json
from pathlib import Path
from urllib.parse import urlsplit
SCHEMA="AETHER-244/source-challenge-gate-v1"
HOLD={"operational_authority":"HOLD","physical_qualification_percent":0,
      "physical_act_allowed":False,"independent_custody_authenticated":False}
def canonical(x):
    return json.dumps(x,sort_keys=True,separators=(",",":"),allow_nan=False).encode("utf-8")
def report(reasons,seen):
    return {"schema":SCHEMA,"verdict":"REJECT_OR_UNVERIFIED",
            "reasons":sorted(set(reasons)),"observed":seen,**HOLD}
def network_policy(url,hosts,policy):
    if not isinstance(url,str) or len(url)>2048:raise ValueError("URL_INVALID")
    p=urlsplit(url);host=p.hostname
    if p.scheme!="https" or not host or p.username or p.password or p.fragment or p.port not in (None,443):
        raise ValueError("URL_SCHEME_AUTH_OR_PORT")
    if host not in hosts or host!=host.lower():raise ValueError("HOST_NOT_PINNED")
    try:ip=ipaddress.ip_address(host)
    except ValueError:ip=None
    if ip is not None and not ip.is_global:raise ValueError("NONPUBLIC_LITERAL_IP")
    expected={"external_egress_only":True,"block_private_ranges":True,
              "redirects_disabled":True,"dns_pinning":True}
    if policy!=expected:raise ValueError("ISOLATION_POLICY_UNPROVEN")
    return host
def ancestry(node,graph):
    seen=set();active=set()
    def visit(k):
        if not isinstance(k,str) or not k or len(k)>128:raise ValueError("BAD_CONTROLLER_ID")
        if k in active:raise ValueError("ANCESTRY_CYCLE")
        if k in seen:return
        if k not in graph:raise ValueError("ANCESTRY_MISSING_NODE")
        parents=graph[k]
        if not isinstance(parents,list) or len(parents)>12:raise ValueError("BAD_PARENTS")
        active.add(k);seen.add(k)
        if len(seen)>128:raise ValueError("ANCESTRY_BOUNDED")
        for p in parents:visit(p)
        active.remove(k)
    visit(node);return seen
def verify_ed25519(pem,msg,sig):
    try:
        from cryptography.hazmat.primitives import serialization
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
        key=serialization.load_pem_public_key(pem.encode("ascii"))
        if not isinstance(key,Ed25519PublicKey) or len(sig)!=64:return False
        key.verify(sig,msg);return True
    except Exception:return False
def assess(b,signature_check=verify_ed25519):
    seen=[];problems=[]
    if not isinstance(b,dict):return report(["INVALID_BUNDLE"],seen)
    receipts=b.get("receipts");graph=b.get("controller_graph");keys=b.get("externally_pinned_public_keys")
    used=b.get("previous_nonces");policy=b.get("declared_network_policy");hosts=b.get("allowed_hosts")
    challenge=b.get("challenge")
    if not isinstance(receipts,list) or len(receipts)!=3:
        problems.append("EXACTLY_THREE_RECEIPTS_REQUIRED");receipts=[]
    if not isinstance(graph,dict):problems.append("CONTROLLER_GRAPH_MISSING");graph={}
    if not isinstance(keys,dict):problems.append("KEY_PINS_MISSING");keys={}
    if not isinstance(used,list) or not all(isinstance(n,str) for n in used):
        problems.append("NONCE_LEDGER_INVALID");used=[]
    if len(used)!=len(set(used)):problems.append("NONCE_LEDGER_DUPLICATE")
    if not isinstance(hosts,list) or not all(isinstance(h,str) for h in hosts):
        problems.append("HOST_LIST_INVALID");hosts=[]
    if not isinstance(challenge,dict):problems.append("CHALLENGE_INVALID");challenge={}
    roots=set();nonces=set();key_ids=set();bindings=set();ancestors=[]
    required={"schema","source_sha256","run_head","run_id","challenge_id","nonce",
              "controller_id","source_url","receipt_id"}
    for r in receipts:
        if not isinstance(r,dict) or set(r)!={"key_id","statement","signature_b64"}:
            problems.append("RECEIPT_ENVELOPE_INVALID");continue
        s=r["statement"];kid=r["key_id"]
        if not isinstance(s,dict) or set(s)!=required or s.get("schema")!="AETHER-244/signed-challenge-v1":
            problems.append("STATEMENT_SCHEMA_INVALID");continue
        if not isinstance(kid,str) or not kid or kid in key_ids:problems.append("KEY_ID_DUPLICATE_OR_INVALID")
        key_ids.add(kid)
        controller=s["controller_id"];nonce=s["nonce"]
        if not isinstance(nonce,str) or not nonce or len(nonce)>128 or nonce in nonces or nonce in used:
            problems.append("NONCE_REPLAY_OR_INVALID")
        if isinstance(nonce,str):nonces.add(nonce)
        value=s["source_sha256"]
        if not isinstance(value,str) or len(value)!=64 or any(c not in "0123456789abcdef" for c in value):
            problems.append("SOURCE_DIGEST_INVALID")
        value=s["run_head"]
        if not isinstance(value,str) or len(value)!=40 or any(c not in "0123456789abcdef" for c in value):
            problems.append("RUN_HEAD_INVALID")
        if type(s["run_id"]) is not int or s["run_id"]<=0:problems.append("RUN_ID_INVALID")
        if not isinstance(s["receipt_id"],str) or not s["receipt_id"]:problems.append("RECEIPT_ID_INVALID")
        if any(s[k]!=challenge.get(k) for k in ("challenge_id","run_id","run_head")):
            problems.append("CHALLENGE_RUN_BINDING_MISMATCH")
        bindings.add((s["challenge_id"],str(s["run_id"]),s["run_head"],s["source_sha256"]))
        try:network_policy(s["source_url"],hosts,policy)
        except (ValueError,TypeError) as e:problems.append("NETWORK_POLICY:"+str(e))
        try:
            ancestors.append(ancestry(controller,graph));roots.add(controller)
        except (ValueError,TypeError) as e:problems.append(str(e))
        key=keys.get(kid)
        if not isinstance(key,dict) or key.get("controller_id")!=controller or not isinstance(key.get("public_key_pem"),str):
            problems.append("EXTERNAL_KEY_PIN_UNAVAILABLE");continue
        try:
            sig=base64.b64decode(r["signature_b64"],validate=True)
            valid=len(sig)==64 and bool(signature_check(key["public_key_pem"],canonical(s),sig))
        except (ValueError,TypeError,UnicodeError):valid=False
        if not valid:problems.append("SIGNATURE_INVALID")
        seen.append({"key_id":kid,"controller_claim":controller,
            "statement_sha256":hashlib.sha256(canonical(s)).hexdigest(),"signature_valid":valid})
    if len(roots)!=3:problems.append("THREE_CONTROLLER_ROOTS_NOT_PRESENT")
    if len(bindings)!=1:problems.append("CROSS_RECEIPT_BINDING_MISMATCH")
    for i,one in enumerate(ancestors):
        for two in ancestors[i+1:]:
            if one&two:problems.append("SHARED_CONTROLLER_ANCESTRY")
    problems.extend(["NETWORK_ISOLATION_NOT_MEASURED","EXTERNAL_CONTROLLER_CUSTODY_NOT_AUTHENTICATED",
        "CHALLENGE_ISSUANCE_AND_NONCE_LEDGER_NOT_INDEPENDENTLY_ATTESTED"])
    return report(problems,seen)
def main():
    p=argparse.ArgumentParser();p.add_argument("--bundle",type=Path,required=True);p.add_argument("--out",type=Path);a=p.parse_args()
    try:
        raw=a.bundle.read_bytes()
        if len(raw)>262144:raise ValueError("INPUT_SIZE_LIMIT")
        result=assess(json.loads(raw))
    except (ValueError,OSError,TypeError,UnicodeError) as e:
        result=report(["INPUT_UNAVAILABLE:"+type(e).__name__],[])
    rendered=json.dumps(result,indent=2,sort_keys=True)+"\n"
    if a.out:
        a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(rendered,encoding="utf-8")
    print(rendered,end="");return 1
if __name__=="__main__":raise SystemExit(main())
