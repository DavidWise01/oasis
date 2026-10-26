import sqlite3, tempfile, hashlib, json, itertools
from pathlib import Path
N={'A1':'(0,0,0)','B1':'(0,0,i)','C1':'(-1,0,+1)'}
EVENTS=['match','drift','missing','altered','frame_offset','combined']
CUTS=[0,1,2,3]
def canon(x):return json.dumps(x,sort_keys=True,separators=(',',':'))
def digest(x):return hashlib.sha256(canon(x).encode()).hexdigest()
def db(path,node):
 c=sqlite3.connect(path/(node+'.db'))
 c.execute('PRAGMA journal_mode=WAL');c.execute('PRAGMA synchronous=FULL')
 c.execute('CREATE TABLE IF NOT EXISTS tether (id TEXT PRIMARY KEY,coord TEXT)')
 c.execute('CREATE TABLE IF NOT EXISTS obs (event TEXT PRIMARY KEY,body TEXT,sha TEXT)')
 c.execute('CREATE TABLE IF NOT EXISTS why (event TEXT PRIMARY KEY,body TEXT,obs_sha TEXT)')
 c.execute('INSERT OR IGNORE INTO tether VALUES (?,?)',(node,N[node]));c.commit()
 return c
def obs(event,node):
 v=dict(event=event,clock=100,phase=7,payload='E',coord=0)
 if event in ('drift','combined') and node=='B1':v['clock']=101
 if event in ('missing','combined') and node=='C1':v.pop('phase')
 if event=='altered' and node=='A1':v['payload']='X'
 if event=='frame_offset' and node=='B1':v['coord']=12
 return v
checks=0
for event,cut in itertools.product(EVENTS,CUTS):
 with tempfile.TemporaryDirectory() as t:
  path=Path(t);reports={}
  for node in N:
   v=obs(event,node);ex=f'{node}: {event}: local witness recording'
   c=db(path,node)
   if cut>0:
    c.execute('INSERT OR IGNORE INTO obs VALUES (?,?,?)',(event,canon(v),digest(v)));c.commit()
   if cut>1:
    c.execute('INSERT OR IGNORE INTO why VALUES (?,?,?)',(event,ex,digest(v)));c.commit()
   c.close()
   c=db(path,node)
   c.execute('INSERT OR IGNORE INTO obs VALUES (?,?,?)',(event,canon(v),digest(v)))
   c.execute('INSERT OR IGNORE INTO why VALUES (?,?,?)',(event,ex,digest(v)));c.commit()
   assert c.execute('SELECT body,sha FROM obs').fetchone()==(canon(v),digest(v));checks+=1
   assert c.execute('SELECT body,obs_sha FROM why').fetchone()==(ex,digest(v));checks+=1
   c.execute('INSERT OR IGNORE INTO why VALUES (?,?,?)',(event,'ATTEMPTED REPLAY',digest(v)));c.commit()
   assert c.execute('SELECT body FROM why').fetchone()[0]==ex;checks+=1
   assert c.execute('SELECT coord FROM tether').fetchone()[0]==N[node];checks+=1
   reports[node]=v;c.close()
  normalized=[]
  for node,v in reports.items():
   q=dict(v)
   if event=='frame_offset' and node=='B1':q['coord']-=12
   normalized.append(q)
  assert (normalized[0]==normalized[1]==normalized[2])==(event in ('match','frame_offset'));checks+=1
print('PASS',checks,'checks, 24 interruption scenarios')
