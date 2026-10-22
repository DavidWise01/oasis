"""Rose V6 — durable SQLite transactional transfers, simulated restart recovery."""
import sqlite3,tempfile,hashlib,json
from pathlib import Path
EDGES=[(i,i+1) for lo,hi in ((122,125),(140,145),(360,366)) for i in range(lo,hi)]
SCALE=10**12
def connect(path):
 d=sqlite3.connect(path)
 d.execute("PRAGMA journal_mode=DELETE")
 d.execute("PRAGMA synchronous=FULL")
 d.execute("CREATE TABLE IF NOT EXISTS balance(slot INTEGER PRIMARY KEY,units INTEGER NOT NULL)")
 d.execute("CREATE TABLE IF NOT EXISTS receipt(seq INTEGER PRIMARY KEY,src INTEGER,dst INTEGER,amount INTEGER)")
 if not d.execute("SELECT 1 FROM balance LIMIT 1").fetchone():
  with d:d.executemany("INSERT INTO balance VALUES(?,?)",[(i,100*SCALE) for i in range(1,367)])
 return d
def apply(d,i,fault=None):
 a,b=EDGES[i]
 if fault=="before_transaction":return "CRASH"
 d.execute("BEGIN IMMEDIATE")
 if d.execute("SELECT 1 FROM receipt WHERE seq=?",(i,)).fetchone():
  d.rollback();return "DUPLICATE"
 try:
  if fault=="after_begin":raise RuntimeError()
  amount=d.execute("SELECT units FROM balance WHERE slot=?",(a,)).fetchone()[0]*25//1000
  d.execute("UPDATE balance SET units=units-? WHERE slot=?",(amount,a))
  if fault=="after_debit":raise RuntimeError()
  d.execute("UPDATE balance SET units=units+? WHERE slot=?",(amount,b))
  d.execute("INSERT INTO receipt VALUES(?,?,?,?)",(i,a,b,amount))
  if fault=="before_commit":raise RuntimeError()
  d.commit();return "COMMITTED"
 except RuntimeError:
  d.close();return "CRASH"
def recover(path):
 d=connect(path)
 for i in range(14):apply(d,i)
 return d
def snapshot(d):
 rows=d.execute("SELECT slot,units FROM balance ORDER BY slot").fetchall()
 receipts=d.execute("SELECT * FROM receipt ORDER BY seq").fetchall()
 h=hashlib.sha256(str(rows).encode()).hexdigest()
 return h,receipts,sum(v for _,v in rows)
def test():
 with tempfile.TemporaryDirectory() as folder:
  d=recover(Path(folder)/"base.db");reference=snapshot(d);d.close()
  assert len(reference[1])==14 and reference[2]==366*100*SCALE
  n=0
  for fault in ("before_transaction","after_begin","after_debit","before_commit"):
   for i in range(14):
    path=Path(folder)/f"{fault}-{i}.db";d=connect(path)
    for j in range(i):assert apply(d,j)=="COMMITTED"
    assert apply(d,i,fault)=="CRASH"
    try:d.close()
    except sqlite3.ProgrammingError:pass
    d=recover(path)
    assert snapshot(d)==reference
    assert apply(d,i)=="DUPLICATE" and snapshot(d)==reference
    d.close();n+=1
  assert n==56
  return dict(status="PASS",scenarios=n,edges=14,origin="0vwxyz",identities=24,phase_bins=60,shadow="unresolved",total_units=reference[2],digest=reference[0],scope="simulated process restart, not real power failure")
if __name__=="__main__":print(json.dumps(test(),indent=2))
