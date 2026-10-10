"""S207 controlled S176 writer: local advisory lock and SQLite epoch validation."""
import sqlite3,subprocess
from fence206 import lease
class Rejected(Exception):pass
def initialize(db):
 d=sqlite3.connect(db,timeout=10,isolation_level=None)
 d.execute('PRAGMA journal_mode=WAL');d.execute('PRAGMA synchronous=FULL')
 d.execute('CREATE TABLE IF NOT EXISTS owner(resource TEXT PRIMARY KEY,epoch INTEGER NOT NULL,holder TEXT NOT NULL)')
 return d
def claim(db,resource,holder):
 d=initialize(db)
 try:
  d.execute('BEGIN IMMEDIATE')
  r=d.execute('SELECT epoch FROM owner WHERE resource=?',(resource,)).fetchone()
  epoch=(r[0] if r else 0)+1
  d.execute('INSERT INTO owner VALUES(?,?,?) ON CONFLICT(resource) DO UPDATE SET epoch=excluded.epoch,holder=excluded.holder',(resource,epoch,holder))
  d.execute('COMMIT')
  return epoch
 except BaseException:
  d.execute('ROLLBACK');raise
 finally:d.close()
def write(*,owner_db,lock,resource,holder,epoch,worker,wal,key,nonce,hook=None):
 with lease(lock):
  d=initialize(owner_db)
  try:
   current=d.execute('SELECT epoch,holder FROM owner WHERE resource=?',(resource,)).fetchone()
   if current!=(epoch,holder):raise Rejected('STALE_OWNER')
   if hook:hook()
   current=d.execute('SELECT epoch,holder FROM owner WHERE resource=?',(resource,)).fetchone()
   if current!=(epoch,holder):raise Rejected('REVOKED_OWNER')
   result=subprocess.run(['node',str(worker),str(wal),str(key),nonce],capture_output=True,text=True,timeout=20)
   if result.returncode:raise Rejected('WAL_REJECTED '+result.stderr.strip())
   return result.stdout
  finally:d.close()
