#!/usr/bin/env python3
"""AETHER-304-RS: bounded remote registry and clock preimage readback.

This verifies HTTPS observations against a frozen AETHER-303 qualification
bundle. Separate hosts and valid signatures do NOT prove independent control.
"""
import argparse,base64,hashlib,json,sqlite3,sys
from pathlib import Path
from urllib.parse import urlsplit
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"264"),str(ROOT/"294"),str(ROOT/"303")]
from acquisition import acquire,validate_url
from live_provider_capture import observation
from identity_rotation_time import qualify,canon,sha,hex64
SCHEMA="AETHER-304/controller-readback-v1"
ZERO="0"*64
SLOTS=("registry_old","registry_new","clock_first","clock_second")
HOLD={"verdict":"REJECT_OR_UNVERIFIED","operational_authority":"HOLD",
      "physical_act_allowed":False,"physical_qualification_percent":0,
      "independent_registry_control_verified":False,
      "independent_clock_control_verified":False,
      "independent_elapsed_time_verified":False,
      "external_custody_verified":False}

def digest(raw):return hashlib.sha256(raw).hexdigest()
def host(url):
    if not isinstance(url,str):raise ValueError("URL_INVALID")
    parsed=urlsplit(url)
    name=parsed.hostname
    if not name:raise ValueError("URL_HOST_REQUIRED")
    return validate_url(url,[name])[0]
def validate(plan,pin,bundle,roots,roots_pin):
    if (not isinstance(plan,dict) or set(plan)!={"schema","bundle_sha256","roots_sha256","endpoints"}
        or plan["schema"]!="AETHER-304/readback-plan-v1" or not hex64(pin) or sha(plan)!=pin):
        raise ValueError("PLAN_PIN_OR_SCHEMA_INVALID")
    if plan["bundle_sha256"]!=sha(bundle) or plan["roots_sha256"]!=sha(roots) or roots_pin!=sha(roots):
        raise ValueError("BUNDLE_OR_ROOT_PIN_CONFLICT")
    endpoints=plan["endpoints"]
    if not isinstance(endpoints,dict) or set(endpoints)!=set(SLOTS):
        raise ValueError("ENDPOINT_SET_INVALID")
    registry_hosts={host(endpoints["registry_old"]),host(endpoints["registry_new"])}
    clock_hosts={host(endpoints["clock_first"]),host(endpoints["clock_second"])}
    if len(registry_hosts)!=1 or len(clock_hosts)!=1 or registry_hosts==clock_hosts:
        raise ValueError("REGISTRY_CLOCK_HOST_ANCESTRY_RISK")
    if len(set(endpoints.values()))!=4:raise ValueError("DUPLICATE_ENDPOINT_URL")
    qualified=qualify(bundle,roots,roots_pin)
    if qualified.get("signature_and_ancestry_claims_consistent") is not True:
        raise ValueError("FROZEN_303_QUALIFICATION_FAILED")
    return qualified
def expected(bundle,slot):
    return {"registry_old":bundle["old_registry"],"registry_new":bundle["new_registry"],
            "clock_first":bundle["time_windows"][0],
            "clock_second":bundle["time_windows"][1]}[slot]
def fetch(url,collector):
    raw,obs=observation(collector(url,[host(url)]),url)
    if len(raw)>65536:raise ValueError("BODY_LIMIT")
    return raw,obs
def compare(raw,reference,slot):
    if raw!=canon(reference):raise ValueError("REMOTE_PREIMAGE_DIVERGENCE:"+slot)
    try:parsed=json.loads(raw)
    except (ValueError,UnicodeError) as exc:raise ValueError("REMOTE_JSON_INVALID") from exc
    if parsed!=reference:raise ValueError("REMOTE_CONTENT_DIVERGENCE:"+slot)
    return digest(raw)
def init(path):
    db=sqlite3.connect(str(path),isolation_level=None,timeout=10)
    try:
        db.execute("PRAGMA journal_mode=WAL")
        db.execute("PRAGMA synchronous=FULL")
        db.execute("BEGIN IMMEDIATE")
        db.execute("CREATE TABLE IF NOT EXISTS readback (seq INTEGER PRIMARY KEY,nonce TEXT UNIQUE NOT NULL,previous_head TEXT NOT NULL,head TEXT UNIQUE NOT NULL,plan_pin TEXT NOT NULL,manifest TEXT NOT NULL)")
        db.commit()
    except Exception:db.rollback();raise
    finally:db.close()
def capture(path,plan,pin,bundle,roots,roots_pin,nonce,collector=acquire):
    validate(plan,pin,bundle,roots,roots_pin)
    if not isinstance(nonce,str) or not 16<=len(nonce)<=128:
        raise ValueError("WINDOW_NONCE_INVALID")
    init(path)
    db=sqlite3.connect(str(path),isolation_level=None,timeout=10)
    try:
        db.execute("PRAGMA busy_timeout=10000");db.execute("BEGIN IMMEDIATE")
        previous=db.execute("SELECT seq,head,plan_pin FROM readback ORDER BY seq DESC LIMIT 1").fetchone()
        seq=previous[0]+1 if previous else 1
        if seq>2:raise ValueError("TWO_WINDOWS_ONLY")
        if previous and previous[2]!=pin:raise ValueError("PLAN_CHANGED_BETWEEN_WINDOWS")
        if db.execute("SELECT 1 FROM readback WHERE nonce=?",(nonce,)).fetchone():
            raise ValueError("WINDOW_NONCE_REPLAY")
        observations={}
        for slot in SLOTS:
            url=plan["endpoints"][slot]
            raw,obs=fetch(url,collector)
            observations[slot]={"observation":obs,"preimage_sha256":compare(raw,expected(bundle,slot),slot)}
        manifest={"schema":SCHEMA,"seq":seq,"nonce":nonce,
                  "previous_head_sha256":previous[1] if previous else ZERO,
                  "plan_sha256":pin,"bundle_sha256":sha(bundle),
                  "roots_sha256":roots_pin,"observations":observations}
        head=sha(manifest)
        db.execute("INSERT INTO readback VALUES (?,?,?,?,?,?)",
                   (seq,nonce,manifest["previous_head_sha256"],head,pin,canon(manifest).decode()))
        db.commit()
        return {**HOLD,"window_sequence":seq,"head_sha256":head,"raw_observations":4,
                "frozen_signatures_and_exact_preimages_matched":True,
                "reasons":["HTTPS_HOSTS_DO_NOT_PROVE_OPERATOR_INDEPENDENCE",
                           "REGISTRY_AND_CLOCK_TRUST_ROOTS_SELF_PINNED",
                           "NO_AUTHENTICATED_ELAPSED_TIME"]}
    except Exception:db.rollback();raise
    finally:db.close()
def audit(path,plan,pin,bundle,roots,roots_pin,prefix_seq=None,prefix_sha=None):
    validate(plan,pin,bundle,roots,roots_pin)
    db=sqlite3.connect(Path(path).resolve().as_uri()+"?mode=ro",uri=True,isolation_level=None)
    try:
        db.execute("PRAGMA query_only=ON");db.execute("BEGIN")
        rows=list(db.execute("SELECT seq,nonce,previous_head,head,plan_pin,manifest FROM readback ORDER BY seq"))
        db.commit()
    finally:db.close()
    faults=[];parent=ZERO;nonces=set()
    for index,(seq,nonce,prior,head,pinrow,raw) in enumerate(rows,1):
        if seq!=index or prior!=parent or nonce in nonces:
            faults.append("CHAIN_SEQUENCE_INVALID")
        nonces.add(nonce)
        try:
            manifest=json.loads(raw)
            if canon(manifest)!=raw.encode() or sha(manifest)!=head:
                faults.append("MANIFEST_PREIMAGE_OR_HEAD_INVALID")
            if (manifest["schema"]!=SCHEMA or manifest["seq"]!=seq or
                manifest["nonce"]!=nonce or manifest["previous_head_sha256"]!=prior or
                manifest["plan_sha256"]!=pin or pinrow!=pin or
                manifest["bundle_sha256"]!=sha(bundle) or
                manifest["roots_sha256"]!=roots_pin):
                faults.append("FROZEN_PIN_OR_HEADER_INVALID")
            if set(manifest["observations"])!=set(SLOTS):
                faults.append("OBSERVATION_SET_INVALID")
            else:
                for slot in SLOTS:
                    url=plan["endpoints"][slot]
                    raw_body,obs=observation(manifest["observations"][slot]["observation"],url)
                    actual=compare(raw_body,expected(bundle,slot),slot)
                    if actual!=manifest["observations"][slot]["preimage_sha256"]:
                        faults.append("RECORDED_PREIMAGE_SHA_INVALID")
        except (ValueError,TypeError,KeyError,UnicodeError):
            faults.append("RETAINED_OBSERVATION_INVALID")
        parent=head
    if len(rows)>2:faults.append("MORE_THAN_TWO_WINDOWS")
    if prefix_seq is not None or prefix_sha is not None:
        if type(prefix_seq) is not int or prefix_seq<1 or not hex64(prefix_sha):
            faults.append("EXTERNAL_PREFIX_INVALID")
        elif len(rows)<prefix_seq:faults.append("HISTORICAL_WINDOW_REMOVED")
        elif rows[prefix_seq-1][3]!=prefix_sha:faults.append("HISTORICAL_WINDOW_REWRITTEN")
    faults.extend(["REGISTRY_OWNERSHIP_NOT_INDEPENDENTLY_ESTABLISHED",
                   "CLOCK_OWNER_AND_ELAPSED_TIME_UNVERIFIED",
                   "SEPARATE_HOSTNAMES_NOT_INDEPENDENT_WITNESSES",
                   "LOCAL_JOURNAL_AND_PINS_CAN_ROLL_BACK"])
    return {**HOLD,"windows":len(rows),"latest_head_sha256":parent,
            "reasons":sorted(set(faults))}
def main():
    p=argparse.ArgumentParser();sub=p.add_subparsers(dest="operation",required=True)
    for command in ("capture","audit"):
        s=sub.add_parser(command)
        for name in ("db","plan","bundle","roots"):s.add_argument("--"+name,type=Path,required=True)
        s.add_argument("--plan-sha256",required=True);s.add_argument("--roots-sha256",required=True)
        if command=="capture":s.add_argument("--nonce",required=True)
        else:
            s.add_argument("--prefix-seq",type=int);s.add_argument("--prefix-sha256")
    args=p.parse_args()
    try:
        plan=json.loads(args.plan.read_bytes());bundle=json.loads(args.bundle.read_bytes())
        roots=json.loads(args.roots.read_bytes())
        if args.operation=="capture":
            result=capture(args.db,plan,args.plan_sha256,bundle,roots,args.roots_sha256,args.nonce)
        else:result=audit(args.db,plan,args.plan_sha256,bundle,roots,args.roots_sha256,args.prefix_seq,args.prefix_sha256)
    except (ValueError,TypeError,OSError,KeyError,sqlite3.Error) as exc:
        result={**HOLD,"reasons":["REJECTED:"+type(exc).__name__+":"+str(exc)[:110]]}
    print(json.dumps(result,sort_keys=True,indent=2))
    return 1
if __name__=="__main__":raise SystemExit(main())
