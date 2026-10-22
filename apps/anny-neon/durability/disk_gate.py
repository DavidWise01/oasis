#!/usr/bin/env python3
"""ANNY file-backed crash consistency gate (SQLite WAL, synchronous=FULL).

A separate Python process starts a real SQLite transaction, signals readiness
before COMMIT or after COMMIT, then receives SIGKILL from its parent. A new
SQLite connection verifies journal + receiver records independently. This is
an analog test of the receipt protocol, NOT a test of browser IndexedDB, and
NOT proof of sudden electrical power removal or hardware flush durability.

Usage: python apps/anny-neon/durability/disk_gate.py --output evidence.json
Unix/POSIX required for os.killpg/SIGKILL. Standard library only.
"""
from __future__ import annotations
import argparse, hashlib, json, os, platform, select, signal, sqlite3
import subprocess, sys, tempfile, time
from pathlib import Path

SOURCE = bytes([1, 2, 3, 4, 5])
DIGEST = hashlib.sha256(SOURCE).hexdigest()
TRANSFER = 'anny-synthetic-40bit'
KEY = TRANSFER + ':' + DIGEST
CASES = ('PREPARE_UNCOMMITTED','COMMIT_UNCOMMITTED','RECEIVER_UNCOMMITTED',
         'CONFIRM_UNCOMMITTED','CONFIRM_COMMITTED')


def db(path: Path):
    connection = sqlite3.connect(str(path), timeout=10, isolation_level=None)
    connection.execute('PRAGMA journal_mode=WAL')
    connection.execute('PRAGMA synchronous=FULL')
    connection.execute('PRAGMA busy_timeout=10000')
    return connection


def init(base: Path):
    base.mkdir(parents=True, exist_ok=True)
    j, r = db(base/'journal.sqlite3'), db(base/'receiver.sqlite3')
    j.execute('CREATE TABLE IF NOT EXISTS journal ('
              'id TEXT PRIMARY KEY, digest TEXT NOT NULL, source_hex TEXT NOT NULL, '
              'state TEXT NOT NULL, receipt_digest TEXT)')
    r.execute('CREATE TABLE IF NOT EXISTS receiver ('
              'delivery_key TEXT PRIMARY KEY, transfer_id TEXT NOT NULL, '
              'digest TEXT NOT NULL, source_hex TEXT NOT NULL, '
              'effect_count INTEGER NOT NULL CHECK(effect_count=1), accepted INTEGER NOT NULL)')
    j.close(); r.close()


def insert_journal(base: Path, state='PREPARED', receipt_digest=None):
    with db(base/'journal.sqlite3') as c:
        c.execute('BEGIN IMMEDIATE')
        c.execute('INSERT INTO journal VALUES (?,?,?,?,?)',
                  (TRANSFER, DIGEST, SOURCE.hex(), state, receipt_digest))
        c.execute('COMMIT')


def insert_receiver(base: Path):
    with db(base/'receiver.sqlite3') as c:
        c.execute('BEGIN IMMEDIATE')
        old=c.execute('SELECT transfer_id,digest,source_hex,effect_count FROM receiver '
                      'WHERE delivery_key=?',(KEY,)).fetchone()
        if old is None:
            c.execute('INSERT INTO receiver VALUES (?,?,?,?,?,?)',
                      (KEY, TRANSFER, DIGEST, SOURCE.hex(), 1, 1))
        elif old != (TRANSFER,DIGEST,SOURCE.hex(),1):
            raise RuntimeError('CONFLICTING_RECEIVER_PAYLOAD')
        c.execute('COMMIT')


def prepare(base: Path, case: str):
    init(base)
    if case != 'PREPARE_UNCOMMITTED':
        state = 'PREPARED' if case == 'COMMIT_UNCOMMITTED' else 'RELEASE_PENDING'
        insert_journal(base, state)
    if case in ('CONFIRM_UNCOMMITTED','CONFIRM_COMMITTED'):
        insert_receiver(base)


def worker(base: Path, case: str):
    path=base/('receiver.sqlite3' if case=='RECEIVER_UNCOMMITTED' else 'journal.sqlite3')
    c=db(path)
    c.execute('BEGIN IMMEDIATE')
    if case=='PREPARE_UNCOMMITTED':
        c.execute('INSERT INTO journal VALUES (?,?,?,?,?)',
                  (TRANSFER,DIGEST,SOURCE.hex(),'PREPARED',None))
    elif case=='COMMIT_UNCOMMITTED':
        c.execute("UPDATE journal SET state='COMMITTED' WHERE id=?", (TRANSFER,))
    elif case=='RECEIVER_UNCOMMITTED':
        c.execute('INSERT INTO receiver VALUES (?,?,?,?,?,?)',
                  (KEY,TRANSFER,DIGEST,SOURCE.hex(),1,1))
    elif case in ('CONFIRM_UNCOMMITTED','CONFIRM_COMMITTED'):
        c.execute("UPDATE journal SET state='CONFIRMED',receipt_digest=? WHERE id=?",
                  (DIGEST,TRANSFER))
    else:
        raise ValueError('UNKNOWN_CASE')
    if case=='CONFIRM_COMMITTED':
        c.execute('COMMIT')
    print('READY', flush=True)
    # Hold process at exact precommit/postcommit boundary; kill from parent.
    while True:
        time.sleep(60)


def inspect(base: Path):
    j,r=db(base/'journal.sqlite3'),db(base/'receiver.sqlite3')
    try:
        row=j.execute('SELECT id,digest,source_hex,state,receipt_digest FROM journal '
                      'WHERE id=?',(TRANSFER,)).fetchone()
        receipt=r.execute('SELECT delivery_key,transfer_id,digest,source_hex,effect_count,accepted '
                          'FROM receiver WHERE delivery_key=?',(KEY,)).fetchone()
        total=r.execute('SELECT COUNT(*),COALESCE(SUM(effect_count),0) FROM receiver').fetchone()
        integrity=(j.execute('PRAGMA integrity_check').fetchone()[0],
                   r.execute('PRAGMA integrity_check').fetchone()[0])
    finally:
        j.close();r.close()
    matching=bool(row and receipt and row[0]==receipt[1] and row[1]==receipt[2]
                  and row[2]==receipt[3] and receipt[0]==KEY and receipt[4]==1
                  and receipt[5]==1 and row[4]==receipt[2])
    violet='VERIFIED' if row and row[3]=='CONFIRMED' and matching else 'HELD'
    return dict(state=row[3] if row else 'ABSENT',receipt=bool(receipt),
                effect_count=total[1],receiver_rows=total[0],violet=violet,
                integrity=list(integrity))


EXPECT={
 'PREPARE_UNCOMMITTED':('ABSENT',False,0,'HELD'),
 'COMMIT_UNCOMMITTED':('PREPARED',False,0,'HELD'),
 'RECEIVER_UNCOMMITTED':('RELEASE_PENDING',False,0,'HELD'),
 'CONFIRM_UNCOMMITTED':('RELEASE_PENDING',True,1,'HELD'),
 'CONFIRM_COMMITTED':('CONFIRMED',True,1,'VERIFIED')
}


def run_case(root: Path, case: str):
    base=root/case.lower();prepare(base,case)
    before=inspect(base)
    process=subprocess.Popen([sys.executable,str(Path(__file__).resolve()),'--worker',
                              str(base),case],stdout=subprocess.PIPE,stderr=subprocess.PIPE,
                             text=True,start_new_session=True)
    try:
        ready,_,_=select.select([process.stdout],[],[],12)
        if not ready or process.stdout.readline().strip()!='READY':
            raise RuntimeError('WORKER_NOT_READY: '+process.stderr.read(500))
        os.killpg(process.pid,signal.SIGKILL)
        code=process.wait(timeout=12)
        after=inspect(base)  # new process connection after SIGKILL
        expected=EXPECT[case]
        observed=(after['state'],after['receipt'],after['effect_count'],after['violet'])
        checks={'sigkill':code==-signal.SIGKILL,
                'state_and_receipt_atomic':observed==expected,
                'no_duplicate_rows':after['receiver_rows']<=1,
                'sqlite_integrity':after['integrity']==['ok','ok']}
        return {'case':case,'before':before,'after':after,
                'expected':list(expected),'checks':checks,
                'pass':all(checks.values())}
    finally:
        if process.poll() is None:
            os.killpg(process.pid,signal.SIGKILL)
            process.wait(timeout=12)


def run(output: Path):
    output.parent.mkdir(parents=True,exist_ok=True)
    report={'schema':'anny-disk-process-crash-v1',
            'scope':'SQLite WAL FULL on local filesystem, subprocess SIGKILL; NOT physical power loss',
            'environment':{'platform':platform.system(),'python':platform.python_version(),
                           'sqlite':sqlite3.sqlite_version},
            'source':{'bytes':SOURCE.hex(),'sha256':DIGEST},
            'scenarios':[], 'status':'RUNNING'}
    with tempfile.TemporaryDirectory(prefix='anny-disk-gate-') as tmp:
        root=Path(tmp)
        for case in CASES:
            try:
                evidence=run_case(root,case)
            except Exception as exc:
                evidence={'case':case,'pass':False,'error':str(exc)}
            report['scenarios'].append(evidence)
            print(case, 'PASS' if evidence['pass'] else 'FAIL',flush=True)
    report['passed']=sum(bool(x['pass']) for x in report['scenarios'])
    report['total']=len(report['scenarios'])
    report['status']='PASS' if report['passed']==len(CASES) else 'FAIL'
    report['exclusions']=['Electrical power loss','OS/kernel failure',
       'Filesystem controller cache loss','Browser IndexedDB durability',
       'Distributed external exactly-once effects']
    output.write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps({'status':report['status'],'passed':report['passed'],
                      'total':report['total'],'output':str(output)}),flush=True)
    return 0 if report['status']=='PASS' else 1


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--worker',nargs=2,metavar=('DIR','CASE'))
    parser.add_argument('--output',default='anny-disk-process-evidence.json')
    args=parser.parse_args()
    if args.worker:
        worker(Path(args.worker[0]),args.worker[1])
    else:
        raise SystemExit(run(Path(args.output)))
