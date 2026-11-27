#!/usr/bin/env python3
"""AETHER-258-RS: actual local SQLite CAS, concurrent writer races, receipts.

Local disk transaction durability != independently witnessed external custody.
No signer keys, network access, privileged process changes, or ACT authority.
"""
import argparse,hashlib,json,sqlite3,threading,time,uuid
from pathlib import Path

SCHEMA="AETHER-258/sqlite-cas-v1"
GENESIS="0"*64
HOLD={"operational_authority":"HOLD","physical_qualification_percent":0,
      "physical_act_allowed":False,"external_atomicity_authenticated":False,
      "independent_custody_authenticated":False}

def canon(obj):
    return json.dumps(obj,sort_keys=True,separators=(",",":"),ensure_ascii=True,allow_nan=False).encode()

def sha(obj):
    return hashlib.sha256(canon(obj)).hexdigest()

def connect(path):
    db=sqlite3.connect(str(path),timeout=10,isolation_level=None)
    db.execute("PRAGMA busy_timeout=10000")
    db.execute("PRAGMA synchronous=FULL")
    db.execute("PRAGMA journal_mode=WAL")
    db.execute("PRAGMA foreign_keys=ON")
    return db

def initialize(path):
    db=connect(path)
    try:
        db.execute("BEGIN IMMEDIATE")
        db.execute("CREATE TABLE IF NOT EXISTS head (id INTEGER PRIMARY KEY CHECK(id=1), seq INTEGER NOT NULL, hash TEXT NOT NULL)")
        db.execute("CREATE TABLE IF NOT EXISTS events (seq INTEGER PRIMARY KEY, previous_hash TEXT NOT NULL, head_hash TEXT NOT NULL UNIQUE, challenge TEXT NOT NULL UNIQUE, nonce TEXT NOT NULL UNIQUE, host TEXT NOT NULL, receipt_hash TEXT NOT NULL UNIQUE)")
        db.execute("CREATE TABLE IF NOT EXISTS attempts (id TEXT PRIMARY KEY, host TEXT NOT NULL, decision TEXT NOT NULL, challenge TEXT NOT NULL, nonce TEXT NOT NULL, expected_seq INTEGER NOT NULL, expected_head TEXT NOT NULL, actual_seq INTEGER NOT NULL, actual_head TEXT NOT NULL, receipt_hash TEXT NOT NULL UNIQUE)")
        db.execute("INSERT OR IGNORE INTO head VALUES (1,0,?)",(GENESIS,))
        db.commit()
    except Exception:
        db.rollback();raise
    finally:
        db.close()

def cas(path,attempt,host,challenge,nonce,expected_seq,expected_head):
    for label,value in (("attempt",attempt),("host",host),("challenge",challenge),("nonce",nonce)):
        if not isinstance(value,str) or not value or len(value)>128:raise ValueError(label+"_INVALID")
    if type(expected_seq) is not int or expected_seq<0:raise ValueError("SEQUENCE_INVALID")
    if not isinstance(expected_head,str) or len(expected_head)!=64 or any(c not in "0123456789abcdef" for c in expected_head):
        raise ValueError("HEAD_INVALID")
    db=connect(path)
    try:
        db.execute("BEGIN IMMEDIATE")  # serializes writers, including separate processes
        row=db.execute("SELECT seq,hash FROM head WHERE id=1").fetchone()
        if row is None:raise ValueError("HEAD_NOT_INITIALIZED")
        seq,head=row
        if db.execute("SELECT id FROM attempts WHERE id=?",(attempt,)).fetchone():
            raise ValueError("ATTEMPT_ID_REPLAY")
        if (expected_seq,expected_head)!=(seq,head):
            decision="STALE_REJECTED"
        elif db.execute("SELECT 1 FROM events WHERE nonce=?",(nonce,)).fetchone():
            decision="NONCE_REPLAY_REJECTED"
        elif db.execute("SELECT 1 FROM events WHERE challenge=?",(challenge,)).fetchone():
            decision="CHALLENGE_REPLAY_REJECTED"
        else:
            decision="ACCEPTED"
        previous_head=head
        if decision=="ACCEPTED":
            seq+=1
            head=sha({"sequence":seq,"previous":previous_head,"host":host,
                      "challenge":challenge,"nonce":nonce,"attempt_id":attempt})
            event_receipt=sha({"kind":"accepted_event","sequence":seq,"head":head})
            db.execute("INSERT INTO events VALUES (?,?,?,?,?,?,?)",
                       (seq,previous_head,head,challenge,nonce,host,event_receipt))
            db.execute("UPDATE head SET seq=?,hash=? WHERE id=1",(seq,head))
        fields={"schema":SCHEMA,"attempt_id":attempt,"host":host,"challenge":challenge,
                "nonce":nonce,"expected_sequence":expected_seq,"expected_head":expected_head,
                "decision":decision,"actual_sequence":seq,"actual_head":head}
        receipt_hash=sha(fields)
        db.execute("INSERT INTO attempts VALUES (?,?,?,?,?,?,?,?,?,?)",
                   (attempt,host,decision,challenge,nonce,expected_seq,expected_head,seq,head,receipt_hash))
        db.commit()  # successful SQLite transaction, not an externally notarized receipt
        return {**fields,"receipt_sha256":receipt_hash,**HOLD}
    except Exception:
        db.rollback();raise
    finally:
        db.close()

def snapshot(path):
    db=connect(path)
    try:
        db.execute("BEGIN")  # consistent read snapshot
        seq,head=db.execute("SELECT seq,hash FROM head WHERE id=1").fetchone()
        ev=db.execute("SELECT seq,previous_hash,head_hash,challenge,nonce,host,receipt_hash FROM events ORDER BY seq").fetchall()
        attempts=db.execute("SELECT id,decision,receipt_hash FROM attempts ORDER BY id").fetchall()
        db.commit()
        return {"schema":SCHEMA,"head":{"sequence":seq,"hash":head},
                "events":[{"sequence":x[0],"previous_hash":x[1],"head_hash":x[2],
                           "challenge":x[3],"nonce":x[4],"host":x[5],"receipt_sha256":x[6]} for x in ev],
                "attempts":[{"attempt_id":x[0],"decision":x[1],"receipt_sha256":x[2]} for x in attempts],
                **HOLD}
    finally:
        db.close()

def verify_snapshot(s):
    problems=[];previous=GENESIS
    if not isinstance(s,dict) or not isinstance(s.get("events"),list) or not isinstance(s.get("head"),dict):
        return ["SNAPSHOT_INVALID"]
    for index,event in enumerate(s["events"],1):
        if not isinstance(event,dict) or event.get("sequence")!=index:
            problems.append("SEQUENCE_INVALID");continue
        if event.get("previous_hash")!=previous:problems.append("HEAD_CHAIN_BROKEN")
        previous=event.get("head_hash")
    if s["head"].get("sequence")!=len(s["events"]) or s["head"].get("hash")!=previous:
        problems.append("FINAL_HEAD_MISMATCH")
    if s.get("operational_authority")!="HOLD" or s.get("physical_act_allowed") is not False:
        problems.append("AUTHORITY_TAMPER")
    return problems

def race(path,workers=8):
    if type(workers) is not int or not 2<=workers<=32:raise ValueError("WORKER_COUNT_INVALID")
    initialize(path)
    base=snapshot(path)["head"]
    barrier=threading.Barrier(workers)
    outcomes=[None]*workers
    def run(i):
        try:
            barrier.wait(timeout=5)
            outcomes[i]=cas(path,"a-"+str(uuid.uuid4()),"host-"+str(i),
                            "c-"+str(i),"n-"+str(i),base["sequence"],base["hash"])
        except Exception as e:
            outcomes[i]={"error":type(e).__name__,**HOLD}
    jobs=[threading.Thread(target=run,args=(i,)) for i in range(workers)]
    for job in jobs:job.start()
    for job in jobs:job.join(timeout=15)
    if any(job.is_alive() for job in jobs):raise TimeoutError("WORKER_STUCK")
    decisions=[x.get("decision") for x in outcomes if isinstance(x,dict)]
    winning=decisions.count("ACCEPTED")
    return {"schema":SCHEMA,"worker_count":workers,"accepted":winning,
            "stale_rejected":decisions.count("STALE_REJECTED"),
            "all_attempts_accounted":len(decisions)==workers,
            "single_winner_observed":winning==1,
            "results":outcomes,"snapshot":snapshot(path),**HOLD}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--db",type=Path,required=True)
    parser.add_argument("--workers",type=int,default=8)
    parser.add_argument("--out",type=Path)
    args=parser.parse_args()
    try:
        result=race(args.db,args.workers)
    except (OSError,ValueError,sqlite3.Error,TimeoutError) as e:
        result={"schema":SCHEMA,"reason":"LOCAL_CAS_FAILED:"+type(e).__name__,**HOLD}
    text=json.dumps(result,indent=2,sort_keys=True)+"\n"
    if args.out:
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(text,encoding="utf-8")
    print(text,end="")
    return 1
if __name__=="__main__":
    raise SystemExit(main())
