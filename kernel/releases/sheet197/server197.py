import sys,ssl,sqlite3
from pathlib import Path
from cryptography.hazmat.primitives import serialization
from target196 import Handler as Target
from authority195 import FloorHandler,serve
role,p,port=sys.argv[1],Path(sys.argv[2]),int(sys.argv[3]);p.mkdir(exist_ok=True)
key=lambda n: serialization.load_pem_private_key((p/(n+'.pem')).read_bytes(),password=None)
pub=lambda n: serialization.load_pem_public_key((p/(n+'.pub')).read_bytes())
if role=='target':
 db=sqlite3.connect(p/'target.sqlite',isolation_level=None);db.execute('PRAGMA journal_mode=WAL');db.execute('PRAGMA synchronous=FULL');db.execute('CREATE TABLE IF NOT EXISTS receipts(resource TEXT,nonce TEXT,body TEXT,sig TEXT,PRIMARY KEY(resource,nonce))')
 s=serve(Target,port,str(p/'target.crt'),str(p/'target.key'),str(p/'ca.pem'));s.allowed=(p/'floor-client.fp').read_text();s.db=db;s.signer=key('target-sign');s.crash_after_commit=False;s.read_only=False
else:
 db=sqlite3.connect(p/'floor.sqlite',isolation_level=None);db.execute('PRAGMA journal_mode=WAL');db.execute('PRAGMA synchronous=FULL');db.execute('CREATE TABLE IF NOT EXISTS floors(resource TEXT PRIMARY KEY,generation INTEGER,head TEXT,seq INTEGER,request_hash TEXT,ack TEXT)')
 s=serve(FloorHandler,port,str(p/'floor.crt'),str(p/'floor.key'),str(p/'ca.pem'));s.db=db;s.permits={(p/'operator.fp').read_text():{'root'}};s.target_url='https://localhost:'+str((p/'target.port').read_text());c=ssl.create_default_context(cafile=str(p/'ca.pem'));c.load_cert_chain(str(p/'floor-client.crt'),str(p/'floor-client.key'));s.target_ctx=c;s.target_pub=pub('target-sign');s.voters={'a':pub('vote-a'),'b':pub('vote-b')};s.signer=key('floor-sign');s.drop_ack_once=(p/'dropack.flag').exists()
print('READY',role,flush=True);s.serve_forever()
