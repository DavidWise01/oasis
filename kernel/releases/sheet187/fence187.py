"""S187: SQLite epoch fencing and Ed25519 checkpoint archive (Python 3.10+)."""
import sqlite3,hashlib,json
from cryptography.exceptions import InvalidSignature
class Quarantine(Exception):pass
def enc(x):return json.dumps(x,sort_keys=True,separators=(',',':')).encode()
def digest(x):return hashlib.sha256(enc(x)).hexdigest()
def open_db(path):
 d=sqlite3.connect(path,timeout=10,isolation_level=None)
 d.execute('PRAGMA journal_mode=WAL');d.execute('PRAGMA synchronous=FULL')
 d.execute('CREATE TABLE IF NOT EXISTS owner(resource TEXT PRIMARY KEY,epoch INTEGER NOT NULL,holder TEXT NOT NULL)')
 d.execute('CREATE TABLE IF NOT EXISTS archive(resource TEXT,generation INTEGER,epoch INTEGER,cursor INTEGER,target_head TEXT,prev_hash TEXT,entry_hash TEXT,signature TEXT,PRIMARY KEY(resource,generation))')
 return d
def claim(d,resource,holder):
 d.execute('BEGIN IMMEDIATE')
 try:
  r=d.execute('SELECT epoch FROM owner WHERE resource=?',(resource,)).fetchone();epoch=(r[0]+1 if r else 1)
  d.execute('INSERT INTO owner VALUES(?,?,?) ON CONFLICT(resource) DO UPDATE SET epoch=excluded.epoch,holder=excluded.holder',(resource,epoch,holder))
  d.execute('COMMIT');return epoch
 except BaseException:d.execute('ROLLBACK');raise
def publish(d,resource,holder,epoch,cursor,target_head,key):
 d.execute('BEGIN IMMEDIATE')
 try:
  if d.execute('SELECT holder,epoch FROM owner WHERE resource=?',(resource,)).fetchone()!=(holder,epoch):raise Quarantine('STALE_OWNER')
  prev=d.execute('SELECT generation,cursor,entry_hash FROM archive WHERE resource=? ORDER BY generation DESC LIMIT 1',(resource,)).fetchone()
  if not isinstance(cursor,int) or cursor<0 or (prev and cursor<=prev[1]):raise Quarantine('BAD_CURSOR')
  body={'resource':resource,'generation':prev[0]+1 if prev else 1,'epoch':epoch,'cursor':cursor,'target_head':target_head,'previous':prev[2] if prev else '0'*64}
  d.execute('INSERT INTO archive VALUES(?,?,?,?,?,?,?,?)',(resource,body['generation'],epoch,cursor,target_head,body['previous'],digest(body),key.sign(enc(body)).hex()))
  d.execute('COMMIT');return body
 except BaseException:d.execute('ROLLBACK');raise
def audit(d,resource,pub):
 rows=d.execute('SELECT generation,epoch,cursor,target_head,prev_hash,entry_hash,signature FROM archive WHERE resource=? ORDER BY generation',(resource,)).fetchall()
 parent='0'*64;last=-1
 for index,(gen,epoch,cursor,head,prev,hash_,sig) in enumerate(rows,1):
  body={'resource':resource,'generation':gen,'epoch':epoch,'cursor':cursor,'target_head':head,'previous':prev}
  if gen!=index or prev!=parent or cursor<=last or digest(body)!=hash_:raise Quarantine('ARCHIVE_FORK')
  try:pub.verify(bytes.fromhex(sig),enc(body))
  except (ValueError,InvalidSignature):raise Quarantine('BAD_SIGNATURE')
  parent=hash_;last=cursor
 return {'count':len(rows),'head':parent,'cursor':last}
