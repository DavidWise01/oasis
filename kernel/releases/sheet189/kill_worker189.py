"""S189 test child: hold BEGIN IMMEDIATE after original S176 WAL writes until SIGKILL."""
import sys,pathlib,subprocess,time
from fence188 import dbopen,scan_wal
DB,WAL,KEY,WORKER,READY=map(pathlib.Path,sys.argv[1:])
d=dbopen(DB)
d.execute('BEGIN IMMEDIATE')
assert d.execute('SELECT epoch,owner FROM ownership WHERE resource=?',('root',)).fetchone()==(1,'alpha')
r=subprocess.run(['node',str(WORKER),str(WAL),str(KEY),'crashed'],capture_output=True,text=True,timeout=6)
if r.returncode:raise Exception(r.stderr)
assert scan_wal(WAL)[0]==4
READY.write_text('WAL_COMMITTED')
while True:time.sleep(5)
