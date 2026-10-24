import sqlite3, tempfile, json
from pathlib import Path
def connect(path):
 c=sqlite3.connect(path);c.execute('PRAGMA journal_mode=WAL');c.execute('PRAGMA synchronous=FULL')
 c.executescript('CREATE TABLE IF NOT EXISTS jobs(id TEXT PRIMARY KEY,payload TEXT,status TEXT); CREATE TABLE IF NOT EXISTS effects(id TEXT PRIMARY KEY,amount INTEGER);');c.commit();return c
def run(c,id,stage='none'):
 if stage=='before_transaction':return 'CRASH'
 c.execute('BEGIN IMMEDIATE')
 payload,status=c.execute('SELECT payload,status FROM jobs WHERE id=?',(id,)).fetchone()
 if status=='done':c.rollback();return 'ALREADY'
 c.execute('INSERT OR IGNORE INTO effects VALUES (?,?)',(id,int(payload)))
 if stage=='after_effect_before_commit':c.rollback();return 'CRASH'
 c.execute("UPDATE jobs SET status='done' WHERE id=?",(id,));c.commit()
 return 'CRASH' if stage=='after_commit_before_ack' else 'ACK'
for stage in ['before_transaction','after_effect_before_commit','after_commit_before_ack','none']:
 with tempfile.TemporaryDirectory() as d:
  p=Path(d)/'db';c=connect(p)
  with c:c.executemany('INSERT INTO jobs VALUES (?,?,"pending")',[(str(i),str(i+1)) for i in range(60)])
  run(c,'0',stage);c.close();c=connect(p)
  for i in range(60):run(c,str(i))
  assert c.execute('SELECT COUNT(*),SUM(amount) FROM effects').fetchone()==(60,1830)
  assert c.execute("SELECT COUNT(*) FROM jobs WHERE status='done'").fetchone()[0]==60
  c.close()
print('PASS 4/4, 60 unique committed effects per scenario')
