#!/usr/bin/env python3
"""AETHER-252-RS: Linux process identity, append-only challenge & witness gate."""
import argparse,base64,hashlib,json,re
from pathlib import Path

SCHEMA="AETHER-252/process-ledger-v1"
HOLD={"operational_authority":"HOLD","physical_qualification_percent":0,
"physical_act_allowed":False,"independent_custody_authenticated":False}
def canon(x):return json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=True,allow_nan=False).encode()
def digest(x):return hashlib.sha256(canon(x)).hexdigest()
def parse_stat(raw):
    """Linux /proc/<pid>/stat: comm in parentheses may contain spaces and ')'."""
    if not isinstance(raw,str):raise ValueError("STAT_NOT_TEXT")
    start=raw.find("(");end=raw.rfind(")")
    if start<1 or end<=start:raise ValueError("STAT_FORMAT")
    tail=raw[end+1:].strip().split()
    # tail[0] is field 3, Linux starttime is field 22 -> tail[19].
    if len(tail)<20:raise ValueError("STAT_TRUNCATED")
    pid=int(raw[:start].strip());ticks=int(tail[19])
    if pid<=0 or ticks<0:raise ValueError("STAT_ID_INVALID")
    return {"pid":pid,"start_ticks":ticks}
def process_identity(pid,proc=Path("/proc")):
    if type(pid) is not int or pid<=0:raise ValueError("PID_INVALID")
    base=proc/str(pid)
    before=parse_stat((base/"stat").read_text())
    namespace=(base/"ns"/"net").stat().st_ino
    boot=(proc/"sys"/"kernel"/"random"/"boot_id").read_text().strip()
    after=parse_stat((base/"stat").read_text())
    if before!=after or before["pid"]!=pid:raise ValueError("PID_REUSED_OR_EXITED")
    if type(namespace) is not int or namespace<=0:raise ValueError("NETNS_INVALID")
    if not re.fullmatch("[0-9a-fA-F-]{36}",boot):raise ValueError("BOOT_ID_INVALID")
    return {"pid":pid,"start_ticks":before["start_ticks"],"netns_inode":namespace,"boot_id":boot.lower()}
def verify_ed25519(pem,msg,sig):
    try:
        from cryptography.exceptions import InvalidSignature
        from cryptography.hazmat.primitives import serialization
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
        key=serialization.load_pem_public_key(pem.encode("ascii"))
        if not isinstance(key,Ed25519PublicKey) or len(sig)!=64:return False
        key.verify(sig,msg);return True
    except (ImportError,InvalidSignature,ValueError,TypeError,UnicodeError):return False
def assess(bundle,verify=verify_ed25519):
    problems=[];observed={"signatures":[]}
    if not isinstance(bundle,dict):return {"schema":SCHEMA,"verdict":"REJECT_OR_UNVERIFIED","reasons":["BUNDLE_INVALID"],"observed":observed,**HOLD}
    identities=bundle.get("identities");events=bundle.get("consumption_events")
    pins=bundle.get("witness_pins");receipts=bundle.get("receipts")
    anchor=bundle.get("externally_pinned_previous_head")
    if not isinstance(identities,dict) or set(identities)!={"supervisor","worker"}:
        problems.append("IDENTITIES_MISSING");identities={}
    else:
        values=[]
        for role in ("supervisor","worker"):
            i=identities[role]
            if not isinstance(i,dict) or set(i)!={"pid","start_ticks","netns_inode","boot_id"}:
                problems.append("IDENTITY_SCHEMA_INVALID");continue
            if any(type(i[k]) is not int or i[k]<0 for k in ("pid","start_ticks","netns_inode")) or i["pid"]<=0 or i["netns_inode"]<=0:
                problems.append("IDENTITY_VALUES_INVALID")
            if not isinstance(i["boot_id"],str) or not re.fullmatch("[0-9a-f-]{36}",i["boot_id"]):
                problems.append("BOOT_ID_INVALID")
            values.append(i)
        if len(values)==2:
            if values[0]["boot_id"]!=values[1]["boot_id"]:problems.append("BOOT_ID_MISMATCH")
            if values[0]["netns_inode"]==values[1]["netns_inode"]:problems.append("NAMESPACE_NOT_SEPARATED")
            if (values[0]["pid"],values[0]["start_ticks"])==(values[1]["pid"],values[1]["start_ticks"]):
                problems.append("SAME_PROCESS_IDENTITY")
    if not isinstance(anchor,str) or not re.fullmatch("[0-9a-f]{64}",anchor):
        problems.append("EXTERNAL_ANCHOR_INVALID");anchor="0"*64
    if not isinstance(events,list) or not 1<=len(events)<=128:
        problems.append("EVENT_COUNT_INVALID");events=[]
    prev=anchor;seen=set()
    for index,e in enumerate(events):
        if not isinstance(e,dict) or set(e)!={"sequence","challenge_id","nonce","run_id","identity_sha256","previous_sha256","event_sha256"}:
            problems.append("EVENT_SCHEMA_INVALID");break
        if type(e["sequence"]) is not int or e["sequence"]!=index:problems.append("EVENT_SEQUENCE_INVALID")
        if e["previous_sha256"]!=prev:problems.append("EVENT_CHAIN_BROKEN")
        nonce=e["nonce"]
        if not isinstance(nonce,str) or not nonce or nonce in seen:problems.append("NONCE_REPLAY")
        if isinstance(nonce,str):seen.add(nonce)
        if type(e["run_id"]) is not int or e["run_id"]<=0:problems.append("EVENT_RUN_INVALID")
        if not isinstance(e["challenge_id"],str) or not e["challenge_id"]:problems.append("EVENT_CHALLENGE_INVALID")
        if e["identity_sha256"]!=digest(identities):problems.append("EVENT_IDENTITY_SUBSTITUTED")
        actual=digest({k:v for k,v in e.items() if k!="event_sha256"})
        if actual!=e["event_sha256"]:problems.append("EVENT_HASH_INVALID")
        prev=actual
    observed["head_sha256"]=prev
    if not isinstance(receipts,list) or len(receipts)!=3:problems.append("THREE_RECEIPTS_REQUIRED");receipts=[]
    if not isinstance(pins,dict):problems.append("PUBLIC_KEY_PINS_MISSING");pins={}
    roots=set();keys=set();statement={"schema":SCHEMA,"head_sha256":prev,"identity_sha256":digest(identities)}
    for r in receipts:
        if not isinstance(r,dict) or set(r)!={"key_id","controller_root","signature_b64"}:
            problems.append("RECEIPT_SCHEMA_INVALID");continue
        kid=r["key_id"];root=r["controller_root"]
        if not isinstance(kid,str) or not kid or kid in keys:problems.append("KEY_DUPLICATE_OR_INVALID");continue
        keys.add(kid)
        if not isinstance(root,str) or not root or root in roots:problems.append("ROOT_DUPLICATE_OR_INVALID")
        if isinstance(root,str):roots.add(root)
        pin=pins.get(kid)
        if not isinstance(pin,dict) or pin.get("controller_root")!=root or not isinstance(pin.get("public_key_pem"),str):
            problems.append("PUBLIC_KEY_NOT_PINNED");continue
        try:
            sig=base64.b64decode(r["signature_b64"],validate=True)
            valid=bool(verify(pin["public_key_pem"],canon(statement),sig))
        except (ValueError,TypeError,UnicodeError):valid=False
        if not valid:problems.append("SIGNATURE_INVALID")
        observed["signatures"].append({"key_id":kid,"controller_root":root,"valid":valid})
    if len(roots)!=3:problems.append("THREE_CONTROLLER_LABELS_REQUIRED")
    problems+=["LIVE_PROCESS_LIVENESS_NOT_INDEPENDENTLY_ATTESTED",
               "EXTERNAL_LEDGER_ANCHOR_AND_NONCE_CUSTODY_UNVERIFIED",
               "WITNESS_CONTROLLER_ANCESTRY_UNVERIFIED"]
    return {"schema":SCHEMA,"verdict":"REJECT_OR_UNVERIFIED","reasons":sorted(set(problems)),"observed":observed,**HOLD}
def main():
    p=argparse.ArgumentParser();s=p.add_subparsers(dest="mode",required=True)
    i=s.add_parser("identity");i.add_argument("--pid",type=int,required=True)
    a=s.add_parser("review");a.add_argument("--bundle",type=Path,required=True)
    p.add_argument("--out",type=Path);args=p.parse_args()
    try:
        if args.mode=="identity":result={"observation":process_identity(args.pid),**HOLD}
        else:
            raw=args.bundle.read_bytes()
            if len(raw)>512*1024:raise ValueError("INPUT_TOO_LARGE")
            result=assess(json.loads(raw))
    except (OSError,ValueError,TypeError) as e:
        result={"schema":SCHEMA,"verdict":"REJECT_OR_UNVERIFIED","reasons":["INPUT_FAILED:"+type(e).__name__],**HOLD}
    output=json.dumps(result,sort_keys=True,indent=2)+"\n"
    if args.out:args.out.write_text(output,encoding="utf-8")
    print(output,end="");return 1
if __name__=="__main__":raise SystemExit(main())
