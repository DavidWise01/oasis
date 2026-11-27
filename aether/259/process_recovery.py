#!/usr/bin/env python3
"""AETHER-259-RS: real multi-process SQLite CAS and interrupted-writer recovery.

Only fixed child commands; never signal/kill processes or authorize ACT.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import time
import uuid

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "258"))
from sqlite_cas import GENESIS, HOLD, cas, connect, initialize, sha, snapshot

SCHEMA="AETHER-259/multiprocess-recovery-v1"
CRASH_SCRIPT=(
    "import os,sqlite3,sys;"
    "db=sqlite3.connect(sys.argv[1],timeout=10,isolation_level=None);"
    "db.execute('BEGIN IMMEDIATE');"
    "db.execute('UPDATE head SET hash=? WHERE id=1',('f'*64,));"
    "os._exit(17)"
)

def verify_database(path):
    """Check local committed SQLite rows, not external provenance."""
    problems=[]
    db=connect(path)
    try:
        db.execute("BEGIN")
        row=db.execute("PRAGMA integrity_check").fetchone()
        if row != ("ok",):problems.append("SQLITE_INTEGRITY_FAILED")
        seq,head=db.execute("SELECT seq,hash FROM head WHERE id=1").fetchone()
        events=db.execute("SELECT seq,previous_hash,head_hash,challenge,nonce,host,receipt_hash FROM events ORDER BY seq").fetchall()
        attempts=db.execute("SELECT id,host,decision,challenge,nonce,expected_seq,expected_head,actual_seq,actual_head,receipt_hash FROM attempts ORDER BY id").fetchall()
        previous=GENESIS
        used_challenges=set()
        used_nonces=set()
        for index,(n,prior,current,challenge,nonce,host,receipt) in enumerate(events,1):
            if n!=index:problems.append("EVENT_SEQUENCE_INVALID")
            if prior!=previous:problems.append("EVENT_PREVIOUS_HEAD_MISMATCH")
            matching=[a for a in attempts if a[2]=="ACCEPTED" and a[7]==n and a[8]==current and a[3]==challenge and a[4]==nonce and a[1]==host]
            if len(matching)!=1:problems.append("ACCEPTED_ATTEMPT_NOT_UNIQUE")
            else:
                expected=sha({"sequence":n,"previous":prior,"host":host,
                              "challenge":challenge,"nonce":nonce,"attempt_id":matching[0][0]})
                if current!=expected:problems.append("EVENT_HEAD_HASH_INVALID")
            if receipt!=sha({"kind":"accepted_event","sequence":n,"head":current}):
                problems.append("EVENT_RECEIPT_HASH_INVALID")
            if challenge in used_challenges:problems.append("CHALLENGE_REPLAY")
            if nonce in used_nonces:problems.append("NONCE_REPLAY")
            used_challenges.add(challenge);used_nonces.add(nonce)
            previous=current
        if seq!=len(events) or head!=previous:problems.append("FINAL_HEAD_MISMATCH")
        for a in attempts:
            ident,host,decision,challenge,nonce,expected_seq,expected_head,actual_seq,actual_head,receipt=a
            fields={"schema":"AETHER-258/sqlite-cas-v1","attempt_id":ident,"host":host,
                    "challenge":challenge,"nonce":nonce,"expected_sequence":expected_seq,
                    "expected_head":expected_head,"decision":decision,
                    "actual_sequence":actual_seq,"actual_head":actual_head}
            if sha(fields)!=receipt:problems.append("ATTEMPT_RECEIPT_HASH_INVALID")
            if decision not in ("ACCEPTED","STALE_REJECTED","CHALLENGE_REPLAY_REJECTED","NONCE_REPLAY_REJECTED"):
                problems.append("ATTEMPT_DECISION_INVALID")
        db.commit()
        return {"schema":SCHEMA,"checked_events":len(events),"checked_attempts":len(attempts),
                "head":{"sequence":seq,"sha256":head},
                "problems":sorted(set(problems)),**HOLD}
    finally:
        db.close()

def worker(path,attempt_id,host,challenge,nonce,seq,head,start_at):
    deadline=time.monotonic()+5
    while time.time()<start_at and time.monotonic()<deadline:
        time.sleep(0.002)
    if time.monotonic()>=deadline:raise TimeoutError("START_BARRIER_EXPIRED")
    return cas(path,attempt_id,host,challenge,nonce,seq,head)

def run_fixed(command,timeout=10):
    return subprocess.run(command,capture_output=True,text=True,timeout=timeout,check=False)

def multi_process_race(path,workers=8,runner=run_fixed):
    if type(workers) is not int or not 2<=workers<=16:raise ValueError("WORKER_COUNT_INVALID")
    initialize(path)
    original=snapshot(path)["head"]
    start=time.time()+0.6
    commands=[]
    for i in range(workers):
        commands.append([sys.executable,str(Path(__file__).resolve()),"--worker",
                         "--db",str(path),"--attempt","a-"+str(uuid.uuid4()),
                         "--host","host-"+str(i),"--challenge","challenge-"+str(i),
                         "--nonce","nonce-"+str(i),"--seq",str(original["sequence"]),
                         "--head",original["hash"],"--start-at",repr(start)])
    # Spawn all before collecting results, so the contenders overlap.
    children=[subprocess.Popen(cmd,stdin=subprocess.DEVNULL,
              stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,close_fds=True)
              for cmd in commands]
    results=[]
    for child in children:
        try:
            stdout,stderr=child.communicate(timeout=12)
            if child.returncode!=0 or len(stdout)>16384:
                results.append({"error":"WORKER_FAILED","exit_code":child.returncode})
            else:
                results.append(json.loads(stdout))
        except (subprocess.TimeoutExpired,ValueError):
            results.append({"error":"WORKER_NOT_RECORDED"})
    review=verify_database(path)
    accepted=sum(x.get("decision")=="ACCEPTED" for x in results)
    return {"schema":SCHEMA,"workers":workers,"accepted":accepted,
            "stale_rejected":sum(x.get("decision")=="STALE_REJECTED" for x in results),
            "one_local_winner":accepted==1 and all("decision" in x for x in results),
            "worker_results":results,"database_review":review,**HOLD}

def crash_recovery(path,runner=run_fixed):
    initialize(path)
    before=verify_database(path)
    if before["problems"]:raise ValueError("PRECRASH_DATABASE_INVALID")
    result=runner([sys.executable,"-I","-c",CRASH_SCRIPT,str(path)],timeout=10)
    after=verify_database(path)
    return {"schema":SCHEMA,"interrupted_child_exit_code":result.returncode,
            "expected_exit_code":17,"before":before["head"],"after":after["head"],
            "rollback_preserved_head":result.returncode==17 and before["head"]==after["head"],
            "post_restart_review":after,**HOLD}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--db",type=Path,required=True)
    parser.add_argument("--workers",type=int,default=8)
    parser.add_argument("--worker",action="store_true")
    parser.add_argument("--attempt")
    parser.add_argument("--host")
    parser.add_argument("--challenge")
    parser.add_argument("--nonce")
    parser.add_argument("--seq",type=int)
    parser.add_argument("--head")
    parser.add_argument("--start-at",type=float)
    parser.add_argument("--out",type=Path)
    args=parser.parse_args()
    try:
        if args.worker:
            result=worker(args.db,args.attempt,args.host,args.challenge,args.nonce,args.seq,args.head,args.start_at)
        else:
            result={"race":multi_process_race(args.db,args.workers),
                    "crash_restart":crash_recovery(args.db),**HOLD}
    except (ValueError,TypeError,OSError,sqlite3.Error,TimeoutError) as e:
        result={"verdict":"REJECT_OR_UNVERIFIED","reason":"EXECUTION_FAILED:"+type(e).__name__,**HOLD}
    output=json.dumps(result,indent=2,sort_keys=True)+"\n"
    if args.out:
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(output,encoding="utf-8")
    print(output,end="")
    return 0 if args.worker and "decision" in result else 1

if __name__=="__main__":
    raise SystemExit(main())
