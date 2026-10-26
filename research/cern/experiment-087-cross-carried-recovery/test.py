import sqlite3,tempfile,itertools,json,hashlib
from pathlib import Path
N={'A1':'(0,0,0)','B1':'(0,0,i)','C1':'(-1,0,+1)'}
P=['[{()}]','{[()]}','([{}])','({[]})','[({})]','{([])}']
def open_db(root,node):
 c=sqlite3.connect(root/(node+'.db'),isolation_level=None)
 c.execute('PRAGMA journal_mode=WAL')
 c.execute('PRAGMA synchronous=FULL')
 c.execute('CREATE TABLE IF NOT EXISTS tether(id TEXT PRIMARY KEY,anchor TEXT)')
 c.execute('CREATE TABLE IF NOT EXISTS inbox(id TEXT PRIMARY KEY,body TEXT)')
 c.execute('CREATE TABLE IF NOT EXISTS outbox(id TEXT PRIMARY KEY,body TEXT,ack INTEGER DEFAULT 0)')
 c.execute('INSERT OR IGNORE INTO tether VALUES (?,?)',(node,N[node]))
 return c
checks=0
for cutoff in range(4):
 with tempfile.TemporaryDirectory() as t:
  root=Path(t); db={n:open_db(root,n) for n in N}; jobs=[]
  for src,dst in itertools.permutations(N,2):
   for idx,p in enumerate(P):
    key=f'{src}>{dst}:{idx}';payload=json.dumps(dict(src=src,dst=dst,pattern=p,winding=idx),sort_keys=True)
    db[src].execute('INSERT INTO outbox VALUES (?,?,0)',(key,payload));jobs.append((src,dst,key,payload));checks+=1
  if cutoff>0:
   for src,dst,key,payload in jobs:
    assert payload;checks+=1
    if cutoff>=2:db[dst].execute('INSERT OR IGNORE INTO inbox VALUES (?,?)',(key,payload));checks+=1
    if cutoff==3:db[src].execute('UPDATE outbox SET ack=1 WHERE id=?',(key,));checks+=1
  for c in db.values():c.close()
  db={n:open_db(root,n) for n in N}
  for src,dst,key,payload in jobs:
   db[dst].execute('INSERT OR IGNORE INTO inbox VALUES (?,?)',(key,payload))
   assert db[dst].execute('SELECT body FROM inbox WHERE id=?',(key,)).fetchone()[0]==payload;checks+=1
   db[src].execute('UPDATE outbox SET ack=1 WHERE id=?',(key,))
   db[dst].execute('INSERT OR IGNORE INTO inbox VALUES (?,?)',(key,payload))
   assert db[dst].execute('SELECT COUNT(*) FROM inbox WHERE id=?',(key,)).fetchone()[0]==1;checks+=1
   assert db[src].execute('SELECT ack FROM outbox WHERE id=?',(key,)).fetchone()[0]==1;checks+=1
  for n in N:
   assert db[n].execute('SELECT COUNT(*) FROM inbox').fetchone()[0]==12;checks+=1
   assert db[n].execute('SELECT COUNT(*) FROM outbox WHERE ack=1').fetchone()[0]==12;checks+=1
   assert db[n].execute('SELECT anchor FROM tether').fetchone()[0]==N[n];checks+=1
  for c in db.values():c.close()
print('PASS',checks,'checks')
