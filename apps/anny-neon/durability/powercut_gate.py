#!/usr/bin/env python3
"""ANNY sacrificial-machine power-interruption evidence gate.

Never cuts power, reboots, shuts down, edits system config or touches an
existing user database. Writes synthetic five-byte WAL fixtures only under
a separately acknowledged sacrificial directory. An independent observer
must record REGISTER/OFF/ON on ANOTHER machine. A report is always a
CANDIDATE, never an automatically certified electrical power-loss result.

Linux, Python standard library. Use --help and POWER_CUT_PROTOCOL.md.
"""
from __future__ import annotations
import argparse, datetime as dt, hashlib, json, os, pathlib, platform
import socket, sqlite3, sys, tempfile, time, uuid, fcntl
from urllib.parse import quote

MARKER="ANNY_SACRIFICIAL_STORAGE_ONLY"
CASES=("PREPARE_UNCOMMITTED","COMMIT_UNCOMMITTED","RECEIVER_UNCOMMITTED",
       "CONFIRM_UNCOMMITTED","CONFIRM_COMMITTED")
EXPECT={
 "PREPARE_UNCOMMITTED":("ABSENT",False,0,"HELD"),
 "COMMIT_UNCOMMITTED":("PREPARED",False,0,"HELD"),
 "RECEIVER_UNCOMMITTED":("RELEASE_PENDING",False,0,"HELD"),
 "CONFIRM_UNCOMMITTED":("RELEASE_PENDING",True,1,"HELD"),
 "CONFIRM_COMMITTED":("CONFIRMED",True,1,"VERIFIED")
}
BYTES=bytes([1,2,3,4,5])
DIGEST=hashlib.sha256(BYTES).hexdigest()
SCHEMA="anny-powercut-protocol-v1"

def canonical(value):
 return json.dumps(value,sort_keys=True,ensure_ascii=False,separators=(",",":")).encode()

def sha(value):
 return hashlib.sha256(canonical(value)).hexdigest()

def now():
 return dt.datetime.now(dt.timezone.utc).isoformat()

def boot_id():
 p=pathlib.Path("/proc/sys/kernel/random/boot_id")
 return p.read_text().strip() if p.exists() else None

def host_id():
 p=pathlib.Path("/etc/machine-id")
 machine=p.read_text().strip() if p.exists() else None
 return {"hostname":socket.gethostname(),"machine_id":machine,"boot_id":boot_id()}

def same_physical_host(a,b):
 # Hostname alone is insufficient evidence of independent hardware.
 return a.get("machine_id") and a.get("machine_id")==b.get("machine_id")

def safe_root(root):
 p=pathlib.Path(root).expanduser().absolute()
 if p.is_symlink() or not p.is_dir() or p==pathlib.Path("/") or p==pathlib.Path.home():
  raise ValueError("REJECT_UNSAFE_TARGET_PATH")
 marker=p/MARKER
 if marker.is_symlink() or not marker.is_file() or marker.read_text().strip()!=MARKER:
  raise ValueError("SACRIFICIAL_MARKER_REQUIRED")
 return p

def open_db(path):
 c=sqlite3.connect(str(path),timeout=10,isolation_level=None)
 c.execute("PRAGMA journal_mode=WAL")
 c.execute("PRAGMA synchronous=FULL")
 c.execute("PRAGMA busy_timeout=10000")
 return c

def read_db(path):
 # Avoid mutating SQLite journal mode or accidentally creating a database
 # during a post-restart audit. SQLite may perform ordinary WAL recovery.
 p=pathlib.Path(path).resolve(strict=True)
 uri="file:"+quote(str(p),safe="/")+"?mode=ro"
 c=sqlite3.connect(uri,uri=True,timeout=10,isolation_level=None)
 c.execute("PRAGMA query_only=ON")
 return c

def parse_witness_clock(value):
 try:
  d=dt.datetime.fromisoformat(value)
  if d.tzinfo is None:raise ValueError("NAIVE_TIMESTAMP")
  return d.astimezone(dt.timezone.utc)
 except (TypeError,AttributeError,ValueError) as e:
  raise ValueError("WITNESS_TIMESTAMP_INVALID") from e

def validate_witness_sequence(events,manifest):
 # Hashes detect changes, not truth of an operator-entered event.
 if len(events)!=3:return {"host_stable":False,"clock_ordered":False,
  "manifest_bound":False,"distinct_event_ids":False}
 expected=("REGISTER","OFF_OBSERVED","ON_OBSERVED")
 host=events[0].get("witness_host")
 host_stable=bool(isinstance(host,dict) and host.get("hostname")
  and host.get("machine_id") and host.get("boot_id")
  and all(e.get("witness_host")==host for e in events))
 manifest_bound=all(e.get("schema")==SCHEMA
  and e.get("event")==expected[i]
  and e.get("run_id")==manifest.get("run_id")
  and e.get("manifest_sha256")==manifest.get("manifest_sha256")
  for i,e in enumerate(events))
 nonces=[e.get("event_nonce") for e in events]
 distinct_event_ids=all(isinstance(n,str) and len(n)==32
  and all(c in "0123456789abcdef" for c in n) for n in nonces)
 distinct_event_ids=distinct_event_ids and len(set(nonces))==3
 clock_ordered=False
 try:
  times=[parse_witness_clock(e["observed_utc"]) for e in events]
  clocks=[e["monotonic_ns"] for e in events]
  clock_ordered=(times[0]<times[1]<times[2]
   and all(type(n) is int and n>=0 for n in clocks)
   and clocks[0]<clocks[1]<clocks[2])
 except (KeyError,TypeError,ValueError):pass
 return {"host_stable":host_stable,"clock_ordered":clock_ordered,
  "manifest_bound":manifest_bound,"distinct_event_ids":distinct_event_ids}

def setup_fixture(root,case):
 if case not in CASES: raise ValueError("UNKNOWN_CASE")
 dest=safe_root(root)/("run-"+uuid.uuid4().hex)
 dest.mkdir(mode=0o700)
 # Persist directory creation metadata before arming the actual power cut.
 parent_fd=os.open(str(dest.parent),os.O_RDONLY|os.O_DIRECTORY)
 try:os.fsync(parent_fd)
 finally:os.close(parent_fd)
 j=open_db(dest/"journal.sqlite3")
 r=open_db(dest/"receiver.sqlite3")
 j.execute("CREATE TABLE journal (id TEXT PRIMARY KEY,digest TEXT NOT NULL,"
           "source_hex TEXT NOT NULL,state TEXT NOT NULL,receipt_digest TEXT)")
 r.execute("CREATE TABLE receiver (delivery_key TEXT PRIMARY KEY,"
           "transfer_id TEXT NOT NULL,digest TEXT NOT NULL,"
           "source_hex TEXT NOT NULL,effect_count INTEGER NOT NULL,"
           "accepted INTEGER NOT NULL)")
 key="transfer:"+DIGEST
 if case!="PREPARE_UNCOMMITTED":
  state="PREPARED" if case=="COMMIT_UNCOMMITTED" else "RELEASE_PENDING"
  j.execute("INSERT INTO journal VALUES (?,?,?,?,NULL)",("transfer",DIGEST,BYTES.hex(),state))
 if case in ("CONFIRM_UNCOMMITTED","CONFIRM_COMMITTED"):
  r.execute("INSERT INTO receiver VALUES (?,?,?,?,1,1)",(key,"transfer",DIGEST,BYTES.hex()))
 j.close();r.close()
 target_identity=host_id()
 if not all(target_identity.get(k) for k in ("hostname","machine_id","boot_id")):
  raise ValueError("TARGET_IDENTITY_INCOMPLETE")
 manifest={"schema":SCHEMA,"run_id":dest.name,"case":case,"created_utc":now(),
   "target":target_identity,"fixture_dir":str(dest),"source_sha256":DIGEST,
   "expected":list(EXPECT[case])}
 manifest["manifest_sha256"]=sha(manifest)
 mf=dest/"manifest.json"
 with mf.open("w",encoding="utf-8") as file:
  file.write(json.dumps(manifest,indent=2)+"\n")
  file.flush();os.fsync(file.fileno())
 dir_fd=os.open(str(dest),os.O_RDONLY|os.O_DIRECTORY)
 try:os.fsync(dir_fd)
 finally:os.close(dir_fd)
 print(json.dumps({"status":"PREPARED_NOT_ARMED","manifest":str(mf),
                   "manifest_sha256":manifest["manifest_sha256"]}))
 return manifest

def read_manifest(path,need_target=False):
 p=pathlib.Path(path).expanduser().absolute()
 x=json.loads(p.read_text())
 if x.get("schema")!=SCHEMA or x.get("case") not in CASES:
  raise ValueError("BAD_MANIFEST")
 h=x.pop("manifest_sha256",None)
 if not h or h!=sha(x):raise ValueError("MANIFEST_HASH_MISMATCH")
 x["manifest_sha256"]=h
 if not x.get("run_id","").startswith("run-") or x["source_sha256"]!=DIGEST:
  raise ValueError("MANIFEST_IDENTITY_MISMATCH")
 if need_target:
  d=pathlib.Path(x["fixture_dir"]).resolve()
  if p.parent.resolve()!=d or d.name!=x["run_id"]:
   raise ValueError("MANIFEST_NOT_AT_FIXTURE")
  safe_root(d.parent)
  if x["target"].get("machine_id") and host_id().get("machine_id")!=x["target"]["machine_id"]:
   raise ValueError("DIFFERENT_TARGET_HARDWARE")
 return x

def arm(manifest_path,seconds):
 m=read_manifest(manifest_path,True)
 if seconds<1 or seconds>3600:raise ValueError("HOLD_LIMIT_1_TO_3600_SECONDS")
 d=pathlib.Path(m["fixture_dir"])
 c=open_db(d/("receiver.sqlite3" if m["case"]=="RECEIVER_UNCOMMITTED" else "journal.sqlite3"))
 c.execute("BEGIN IMMEDIATE")
 key="transfer:"+DIGEST
 case=m["case"]
 if case=="PREPARE_UNCOMMITTED":
  c.execute("INSERT INTO journal VALUES (?,?,?,?,NULL)",("transfer",DIGEST,BYTES.hex(),"PREPARED"))
 elif case=="COMMIT_UNCOMMITTED":
  c.execute("UPDATE journal SET state='COMMITTED' WHERE id='transfer'")
 elif case=="RECEIVER_UNCOMMITTED":
  c.execute("INSERT INTO receiver VALUES (?,?,?,?,1,1)",(key,"transfer",DIGEST,BYTES.hex()))
 else:
  c.execute("UPDATE journal SET state='CONFIRMED',receipt_digest=? WHERE id='transfer'",(DIGEST,))
  if case=="CONFIRM_COMMITTED":c.execute("COMMIT")
 print(json.dumps({"status":"ARMED_EXTERNAL_POWER_ACTION_ONLY",
   "case":case,"run_id":m["run_id"],"transaction":
   "COMMITTED" if case=="CONFIRM_COMMITTED" else "OPEN_UNCOMMITTED",
   "expires_seconds":seconds}),flush=True)
 # No command in this program cuts or toggles electrical power.
 try:time.sleep(seconds)
 finally:
  if case!="CONFIRM_COMMITTED":
   try:c.execute("ROLLBACK")
   except sqlite3.Error:pass
  c.close()
 print(json.dumps({"status":"EXPIRED_WITHOUT_POWER_CUT","run_id":m["run_id"]}))

def inspect(manifest):
 d=pathlib.Path(manifest["fixture_dir"])
 j=read_db(d/"journal.sqlite3")
 r=read_db(d/"receiver.sqlite3")
 try:
  row=j.execute("SELECT id,digest,source_hex,state,receipt_digest FROM journal "
                "WHERE id='transfer'").fetchone()
  rec=r.execute("SELECT delivery_key,transfer_id,digest,source_hex,effect_count,accepted "
                "FROM receiver").fetchall()
  integrity=[j.execute("PRAGMA integrity_check").fetchone()[0],
             r.execute("PRAGMA integrity_check").fetchone()[0]]
 finally:j.close();r.close()
 match=bool(row and len(rec)==1 and rec[0]==
    ("transfer:"+DIGEST,"transfer",DIGEST,BYTES.hex(),1,1)
    and row[1]==DIGEST and row[2]==BYTES.hex() and row[4]==DIGEST)
 violet="VERIFIED" if row and row[3]=="CONFIRMED" and match else "HELD"
 return {"state":row[3] if row else "ABSENT",
  "receipt":len(rec)==1,"effect_count":sum(x[4] for x in rec),
  "receiver_rows":len(rec),"violet":violet,"integrity":integrity,
  "source_consistent":not row or (row[1]==DIGEST and row[2]==BYTES.hex())}

def ledger_parse(lines):
 events=[]; prev="GENESIS"; nonces=set()
 for line in lines:
  try:e=json.loads(line)
  except (ValueError,TypeError) as exc:
   raise ValueError("WITNESS_CHAIN_INVALID") from exc
  if not isinstance(e,dict):raise ValueError("WITNESS_CHAIN_INVALID")
  digest=e.get("entry_sha256")
  core={k:v for k,v in e.items() if k!="entry_sha256"}
  if e.get("previous_sha256")!=prev or sha(core)!=digest:
   raise ValueError("WITNESS_CHAIN_INVALID")
  nonce=e.get("event_nonce")
  if not isinstance(nonce,str) or len(nonce)!=32 or nonce in nonces:
   raise ValueError("WITNESS_NONCE_REPLAY")
  nonces.add(nonce)
  events.append(e);prev=digest
 return events,prev

def ledger_load(path):
 p=pathlib.Path(path)
 if p.is_symlink():raise ValueError("WITNESS_SYMLINK_FORBIDDEN")
 return ledger_parse(p.read_text().splitlines() if p.exists() else [])

def witness(manifest_path,ledger_path,event,operator):
 if event not in ("REGISTER","OFF_OBSERVED","ON_OBSERVED"):
  raise ValueError("INVALID_WITNESS_EVENT")
 m=read_manifest(manifest_path)
 witness_host=host_id()
 if same_physical_host(m["target"],witness_host) or m["target"]["hostname"]==witness_host["hostname"]:
  raise ValueError("WITNESS_MUST_BE_ON_SEPARATE_HOST")
 if not all(witness_host.get(k) for k in ("hostname","machine_id","boot_id")):
  raise ValueError("WITNESS_IDENTITY_INCOMPLETE")
 if not isinstance(operator,str) or not operator.strip():
  raise ValueError("WITNESS_NOTE_REQUIRED")
 p=pathlib.Path(ledger_path)
 p.parent.mkdir(parents=True,exist_ok=True)
 if p.is_symlink():raise ValueError("WITNESS_SYMLINK_FORBIDDEN")
 # Lock the full validate-and-append operation. Without flock concurrent
 # observer processes can each append the same event to the same prior tail.
 with p.open("a+",encoding="utf-8") as f:
  fcntl.flock(f.fileno(),fcntl.LOCK_EX)
  try:
   f.seek(0)
   lines=f.read().splitlines()
   events,prev=ledger_parse(lines)
   same=[e for e in events if e.get("run_id")==m["run_id"]]
   actual=[e.get("event") for e in same]
   expected={"REGISTER":[],"OFF_OBSERVED":["REGISTER"],
             "ON_OBSERVED":["REGISTER","OFF_OBSERVED"]}[event]
   if actual!=expected:raise ValueError("WITNESS_EVENT_ORDER")
   if same:
    if any(e.get("manifest_sha256")!=m["manifest_sha256"]
      or e.get("witness_host")!=witness_host for e in same):
     raise ValueError("WITNESS_IDENTITY_MISMATCH")
   observed_at=now()
   clock=time.monotonic_ns()
   if same and (parse_witness_clock(observed_at)<=
      parse_witness_clock(same[-1]["observed_utc"])
      or clock<=same[-1].get("monotonic_ns",-1)):
    raise ValueError("WITNESS_CLOCK_REVERSED")
   core={"schema":SCHEMA,"event":event,"run_id":m["run_id"],
         "manifest_sha256":m["manifest_sha256"],
         "witness_host":witness_host,"observed_utc":observed_at,
         "monotonic_ns":clock,"event_nonce":uuid.uuid4().hex,
         "operator_note":operator.strip()[:300],"previous_sha256":prev}
   e={**core,"entry_sha256":sha(core)}
   f.seek(0,os.SEEK_END)
   f.write(json.dumps(e,sort_keys=True,ensure_ascii=False)+"\n")
   f.flush();os.fsync(f.fileno())
  finally:fcntl.flock(f.fileno(),fcntl.LOCK_UN)
 dir_fd=os.open(str(p.parent),os.O_RDONLY|os.O_DIRECTORY)
 try:os.fsync(dir_fd)
 finally:os.close(dir_fd)
 print(json.dumps({"event_recorded":event,"run_id":m["run_id"],
                   "entry_sha256":e["entry_sha256"],
                   "warning":"operator statement only; hash chain not independent electrical measurement"}))

def verify(manifest_path,ledger_path,out_path):
 m=read_manifest(manifest_path,True)
 snapshot=inspect(m)
 observed=[snapshot["state"],snapshot["receipt"],snapshot["effect_count"],snapshot["violet"]]
 checks={"sqlite_integrity":snapshot["integrity"]==["ok","ok"],
 "expected_atomic_state":observed==m["expected"],
 "no_duplicate_effects":snapshot["receiver_rows"]<=1,
 "correct_source_digest":snapshot["source_consistent"],
 "target_boot_changed":bool(boot_id() and m["target"].get("boot_id") and
                             boot_id()!=m["target"]["boot_id"])}
 events,prev=ledger_load(ledger_path) if ledger_path else ([],None)
 chosen=[e for e in events if e["run_id"]==m["run_id"]]
 checks["external_witness_three_events"]=[e["event"] for e in chosen]==[
     "REGISTER","OFF_OBSERVED","ON_OBSERVED"]
 checks["target_identity_complete"]=bool(all(
   m["target"].get(k) for k in ("hostname","machine_id","boot_id")))
 checks["witness_on_separate_host"]=bool(chosen
   and checks["target_identity_complete"]
   and chosen[0].get("witness_host",{}).get("machine_id")
   and not same_physical_host(m["target"],chosen[0]["witness_host"])
   and m["target"]["hostname"]!=chosen[0]["witness_host"].get("hostname"))
 checks["witness_manifest_consistent"]=bool(chosen and all(
   e.get("manifest_sha256")==m["manifest_sha256"] for e in chosen))
 sequence=validate_witness_sequence(chosen,m)
 checks["witness_host_stable"]=sequence["host_stable"]
 checks["witness_clock_monotonic"]=sequence["clock_ordered"]
 checks["witness_event_binding"]=sequence["manifest_bound"]
 checks["witness_event_nonce_unique"]=sequence["distinct_event_ids"]
 # This is intentionally not certified: witness is operator-reported and
 # no independent electrical meter / immutable attestation has been checked.
 status="EVIDENCE_CANDIDATE_MANUAL_REVIEW" if all(checks.values()) else "NOT_CERTIFIED"
 result={"schema":SCHEMA,"run_id":m["run_id"],"case":m["case"],
   "status":status,"certified":False,"checks":checks,"snapshot":snapshot,
   "expected":m["expected"],"manifest_sha256":m["manifest_sha256"],
   "witness_tail":prev,"evidence_class":"OPERATOR_STATEMENTS_ONLY",
   "independent_electrical_measurement_verified":False,
   "excluded":["unverified electrical waveform",
   "uncorroborated operator statements","hardware cache flush guarantees",
   "browser IndexedDB", "external exactly-once effects"],"verified_utc":now()}
 pathlib.Path(out_path).write_text(json.dumps(result,indent=2)+"\n")
 print(json.dumps({"status":status,"certified":False,
                   "checks_passed":sum(checks.values()),"checks_total":len(checks),
                   "report":str(out_path)}))
 return result

def self_test():
 with tempfile.TemporaryDirectory(prefix="anny-powercut-selftest-") as temp:
  root=pathlib.Path(temp)
  (root/MARKER).write_text(MARKER+"\n")
  for case in CASES:
   m=setup_fixture(root,case)
   report=verify(pathlib.Path(m["fixture_dir"])/"manifest.json",None,
                 root/(m["run_id"]+".report.json"))
   if report["certified"] or report["status"]!="NOT_CERTIFIED":
    raise AssertionError("SIMULATED_FIXTURE_IMPROPERLY_CERTIFIED")
  print(json.dumps({"self_test":"PASS","scenarios":len(CASES),
    "status":"NO_PHYSICAL_CUT_PERFORMED","certified":False}))

def main():
 p=argparse.ArgumentParser(description=__doc__)
 sub=p.add_subparsers(dest="cmd",required=True)
 prep=sub.add_parser("prepare");prep.add_argument("--root",required=True)
 prep.add_argument("--case",choices=CASES,required=True)
 prep.add_argument("--ack-sacrificial",action="store_true")
 hold=sub.add_parser("arm");hold.add_argument("--manifest",required=True)
 hold.add_argument("--seconds",type=int,default=600)
 hold.add_argument("--ack-sacrificial",action="store_true")
 wi=sub.add_parser("witness");wi.add_argument("--manifest",required=True)
 wi.add_argument("--ledger",required=True);wi.add_argument("--event",required=True,
 choices=("REGISTER","OFF_OBSERVED","ON_OBSERVED"))
 wi.add_argument("--operator-note",required=True)
 vf=sub.add_parser("verify");vf.add_argument("--manifest",required=True)
 vf.add_argument("--ledger");vf.add_argument("--report",required=True)
 sub.add_parser("self-test")
 a=p.parse_args()
 if a.cmd=="prepare":
  if not a.ack_sacrificial:raise ValueError("ACK_SACRIFICIAL_REQUIRED")
  setup_fixture(a.root,a.case)
 elif a.cmd=="arm":
  if not a.ack_sacrificial:raise ValueError("ACK_SACRIFICIAL_REQUIRED")
  arm(a.manifest,a.seconds)
 elif a.cmd=="witness":witness(a.manifest,a.ledger,a.event,a.operator_note)
 elif a.cmd=="verify":verify(a.manifest,a.ledger,a.report)
 else:self_test()

if __name__=="__main__":
 try:main()
 except (ValueError,OSError,sqlite3.Error) as e:
  print(json.dumps({"status":"FAIL_CLOSED","error":str(e)}),file=sys.stderr)
  sys.exit(2)
