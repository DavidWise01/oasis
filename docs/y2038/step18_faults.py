"""Step 18: deterministic fault injection for snapshot persistence and WAL."""
import copy,json,os,tempfile
from pathlib import Path
from step17_snapshot import Ledger, canonical, persist
from step12_wal import WAL

def reject(fn):
    try: fn()
    except (ValueError,json.JSONDecodeError): return
    raise AssertionError("corrupted state accepted")

def ledger():
    l=Ledger()
    for term,t in enumerate((2147483647,2147483648,4102444800),1):l.append(term,t)
    return l

def test():
    count=0
    def passed(msg):
        nonlocal count
        count+=1; print('PASS',msg)
    s=ledger().snapshot();bad=copy.deepcopy(s)
    bad['body']['records'][0]['payload']='00'*16
    reject(lambda:Ledger.restore(bad));passed('snapshot corruption rejected')

    with tempfile.TemporaryDirectory() as d:
        p=Path(d)/'snapshot.json';persist(p,s)
        p.write_bytes(p.read_bytes()[:12])
        reject(lambda:Ledger.restore(json.loads(p.read_bytes())))
    passed('truncated snapshot rejected')

    with tempfile.TemporaryDirectory() as d:
        p=Path(d)/'snapshot.json';persist(p,ledger().snapshot(2));before=p.read_bytes()
        with (Path(d)/'snapshot.json.tmp').open('wb') as f:
            f.write(canonical(ledger().snapshot())[:12]);f.flush();os.fsync(f.fileno())
        assert p.read_bytes()==before
    passed('interrupted staging preserves committed snapshot')

    with tempfile.TemporaryDirectory() as d:
        p=Path(d)/'snapshot.json';persist(p,ledger().snapshot(2));before=p.read_bytes()
        old=os.replace
        def fail(*args):raise OSError('injected rename failure')
        os.replace=fail
        try:
            try:persist(p,ledger().snapshot(3))
            except OSError:pass
            else:raise AssertionError('rename failure ignored')
        finally:os.replace=old
        assert p.read_bytes()==before
    passed('failed rename preserves old snapshot')

    with tempfile.TemporaryDirectory() as d:
        p=Path(d)/'snapshot.json';persist(p,ledger().snapshot(2))
        original=os.fsync;calls=[0]
        def fail_second(fd):
            calls[0]+=1
            if calls[0]==2:raise OSError('injected directory fsync failure')
            return original(fd)
        os.fsync=fail_second
        try:
            try:persist(p,ledger().snapshot(3))
            except OSError:pass
            else:raise AssertionError('fsync failure ignored')
        finally:os.fsync=original
        assert Ledger.restore(json.loads(p.read_bytes())).commit_index in (2,3)
    passed('failed directory fsync: durability unconfirmed')

    with tempfile.TemporaryDirectory() as d:
        w=WAL(d);w.advance(1);w.append(1,bytes.fromhex('49543301000000000000611780002d80'))
        with w.log_path.open('ab') as f:
            f.write(b'partial');f.flush();os.fsync(f.fileno())
        reject(lambda:WAL(d))
    passed('torn WAL tail detected')

    with tempfile.TemporaryDirectory() as d:
        w=WAL(d);w.advance(1);w.append(1,bytes.fromhex('49543301000000000000611780002d80'))
        w.log_path.write_bytes(w.log_path.read_bytes().replace(b'495433',b'495434',1))
        reject(lambda:WAL(d))
    passed('WAL payload tamper detected')

    l=ledger();head=l.verify();snap=l.snapshot(2);l.compact(snap)
    assert l.verify()==head and l.append(4,5000000000)['prior']==head
    passed('compaction hash anchor preserved')
    assert count==8
    print('RESULT 8/8 PASS (local fault injection only)')
if __name__=='__main__':test()
