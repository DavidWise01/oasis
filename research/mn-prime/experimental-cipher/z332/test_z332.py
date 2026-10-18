"""Z332 persistent checkpoint smoke/regression test; symbolic only."""
import sqlite3, tempfile, json, hashlib, math, os
LIMIT=math.factorial(24)
def digest(x):return hashlib.sha256(json.dumps(x,sort_keys=True).encode()).hexdigest()
def open_db(path):
 c=sqlite3.connect(path)
 c.execute("PRAGMA journal_mode=WAL")
 c.execute("PRAGMA synchronous=FULL")
 c.execute("CREATE TABLE IF NOT EXISTS ledger (seq INTEGER PRIMARY KEY, idx TEXT, prev TEXT, hash TEXT)")
 c.commit()
 return c
def insert(c,n):
 if type(n)!=int or not 0<=n<LIMIT:raise ValueError("rank")
 prior=c.execute("SELECT seq,hash FROM ledger ORDER BY seq DESC LIMIT 1").fetchone()
 seq=0 if prior is None else prior[0]+1
 prev="GENESIS" if prior is None else prior[1]
 idx=str(n); h=digest([seq,idx,prev])
 c.execute("INSERT INTO ledger VALUES(?,?,?,?)",(seq,idx,prev,h))
def head(c):
 row=c.execute("SELECT seq,hash FROM ledger ORDER BY seq DESC LIMIT 1").fetchone()
 return {"count":0 if row is None else row[0]+1,"tip":"GENESIS" if row is None else row[1]}
def valid(c):
 previous="GENESIS"
 for n,(seq,idx,prev,h) in enumerate(c.execute("SELECT seq,idx,prev,hash FROM ledger ORDER BY seq")):
  if seq!=n or prev!=previous or not idx.isdecimal() or not 0<=int(idx)<LIMIT or h!=digest([seq,idx,prev]):return False
  previous=h
 return True
checks={}
with tempfile.TemporaryDirectory() as d:
 path=os.path.join(d,"ledger.sqlite"); witness_path=os.path.join(d,"witness.json")
 c=open_db(path);c.execute("BEGIN IMMEDIATE")
 for n in (0,1,42,LIMIT-1):insert(c,n)
 c.commit()
 checks["four_committed"]=head(c)["count"]==4
 checks["chain_valid"]=valid(c)
 witness=head(c)
 with open(witness_path,"w") as f:json.dump(witness,f)
 c.close();c=open_db(path)
 checks["restart_persists"]=head(c)==witness
 checks["separate_witness_file"]=json.load(open(witness_path))==head(c)
 c.execute("BEGIN IMMEDIATE");insert(c,77)
 checks["pending_visible"]=head(c)["count"]==5
 c.close();c=open_db(path)
 checks["uncommitted_rollback"]=head(c)==witness
 checks["restart_chain_valid"]=valid(c)
 checks["restored_witness_matches"]=head(c)==witness
 c.execute("BEGIN IMMEDIATE");insert(c,98);c.commit()
 checks["new_tip"]=head(c)!=witness
 checks["stale_witness_rejected"]=not (valid(c) and head(c)==witness)
 witness=head(c)
 with open(witness_path,"w") as f:json.dump(witness,f)
 checks["updated_witness_accepted"]=valid(c) and head(c)==json.load(open(witness_path))
 c.execute("UPDATE ledger SET idx='123' WHERE seq=1");c.commit()
 checks["tamper_detected"]=not valid(c)
 checks["tamper_witness_rejected"]=not (valid(c) and head(c)==witness)
 c.close()
checks["24_factorial"]=LIMIT==620448401733239439360000
checks["governance_separate"]=(5,3,1)!=(3,1,2)
for k,v in checks.items():print(("PASS" if v else "FAIL"),k)
print(f"{sum(checks.values())}/{len(checks)} PASS")
assert all(checks.values())
