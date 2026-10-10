"""SHEET 209: serializable SQLite epoch authority for controlled S208 WAL append."""
import sqlite3,subprocess,json,pathlib
class Denied(Exception):pass
def connect(db):
 d=sqlite3.connect(str(db),timeout=10,isolation_level=None)
 d.execute('PRAGMA journal_mode=WAL');d.execute('PRAGMA synchronous=FULL')
 d.execute('CREATE TABLE IF NOT EXISTS owner(resource TEXT PRIMARY KEY,epoch INTEGER NOT NULL,holder TEXT NOT NULL)')
 return d
def rotate(db,resource,holder):
 d=connect(db)
 try:
  d.execute('BEGIN IMMEDIATE')
  r=d.execute('SELECT epoch FROM owner WHERE resource=?',(resource,)).fetchone()
  epoch=(r[0] if r else 0)+1
  d.execute('INSERT INTO owner VALUES(?,?,?) ON CONFLICT(resource) DO UPDATE SET epoch=excluded.epoch,holder=excluded.holder',(resource,epoch,holder))
  d.execute('COMMIT');return epoch
 except BaseException:
  if d.in_transaction:d.execute('ROLLBACK')
  raise
 finally:d.close()
def fenced_append(db,resource,holder,proof_path,authority_public_key,worker,wal,issuer,nonce,hook=None):
 d=connect(db)
 try:
  d.execute('BEGIN IMMEDIATE')
  claim=json.loads(pathlib.Path(proof_path).read_text())['claims']
  state=d.execute('SELECT epoch,holder FROM owner WHERE resource=?',(resource,)).fetchone()
  if state!=(claim.get('epoch'),holder) or claim.get('holder')!=holder or claim.get('resource')!=resource:raise Denied('STALE_EPOCH')
  if hook:hook()
  p=subprocess.run(['node',str(worker),str(wal),str(issuer),nonce,str(proof_path),str(authority_public_key)],capture_output=True,text=True,timeout=12)
  if p.returncode:raise Denied('NODE_DENIED:'+p.stderr.strip())
  d.execute('COMMIT');return p.stdout
 except BaseException:
  if d.in_transaction:d.execute('ROLLBACK')
  raise
 finally:d.close()
