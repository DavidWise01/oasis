"""S218 immutable, issuer-signed input provenance ledger."""
import sqlite3,json,hashlib
from cryptography.exceptions import InvalidSignature
class Denied(Exception):pass
def canonical(x):return json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()
def hash_input(x):return hashlib.sha256(json.dumps(x,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
class Ledger:
 def __init__(self,path,pub):
  self.path=str(path);self.pub=pub
  with self.open() as d:d.execute('CREATE TABLE IF NOT EXISTS inputs(resource TEXT NOT NULL,nonce TEXT NOT NULL,op TEXT NOT NULL,input_json BLOB NOT NULL,input_hash TEXT NOT NULL,authorization BLOB NOT NULL,PRIMARY KEY(resource,nonce))')
 def open(self):
  d=sqlite3.connect(self.path,timeout=10,isolation_level=None);d.execute('PRAGMA journal_mode=WAL');d.execute('PRAGMA synchronous=FULL');return d
 def register(self,statement,sig):
  if not isinstance(statement,dict) or set(statement)!={'resource','nonce','op','input','inputHash'}:raise Denied('FIELDS')
  if not all(isinstance(statement[k],str) and statement[k] for k in ('resource','nonce','op')):raise Denied('IDENTITY')
  if statement['inputHash']!=hash_input(statement['input']):raise Denied('INPUT_HASH')
  try:self.pub.verify(bytes.fromhex(sig),canonical(statement))
  except (InvalidSignature,ValueError,TypeError):raise Denied('ISSUER_SIGNATURE')
  d=self.open()
  try:
   d.execute('BEGIN IMMEDIATE')
   old=d.execute('SELECT op,input_json,input_hash,authorization FROM inputs WHERE resource=? AND nonce=?',(statement['resource'],statement['nonce'])).fetchone()
   vals=(statement['op'],canonical(statement['input']),statement['inputHash'],bytes.fromhex(sig))
   if old and old!=vals:raise Denied('NONCE_REPLAY_CONFLICT')
   if not old:d.execute('INSERT INTO inputs VALUES(?,?,?,?,?,?)',(statement['resource'],statement['nonce'],*vals))
   d.execute('COMMIT');return not bool(old)
  except BaseException:
   if d.in_transaction:d.execute('ROLLBACK')
   raise
  finally:d.close()
 def get(self,resource,nonce):
  d=self.open()
  try:row=d.execute('SELECT op,input_json,input_hash,authorization FROM inputs WHERE resource=? AND nonce=?',(resource,nonce)).fetchone()
  finally:d.close()
  if row is None:raise Denied('UNREGISTERED_INPUT')
  op,inp,h,sig=row;statement={'resource':resource,'nonce':nonce,'op':op,'input':json.loads(inp),'inputHash':h}
  if hash_input(statement['input'])!=h:raise Denied('LEDGER_HASH_CHANGED')
  try:self.pub.verify(sig,canonical(statement))
  except InvalidSignature:raise Denied('LEDGER_SIGNATURE_CHANGED')
  return statement
