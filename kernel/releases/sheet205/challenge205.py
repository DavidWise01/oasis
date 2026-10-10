"""S205 local challenge-bound proof/floor verifier. Prototype; no cross-store atomicity."""
import sqlite3,hashlib,json,time,secrets
from cryptography.exceptions import InvalidSignature
from snapshot204 import capture,validate_fresh
class Denied(Exception):pass
def canonical(obj):return json.dumps(obj,sort_keys=True,separators=(',',':')).encode()
def digest(obj):return hashlib.sha256(canonical(obj)).hexdigest()
def make_challenge(resource,generation,previous,ttl_ns=2000000000):
 if not resource or not isinstance(generation,int) or generation<1 or not isinstance(previous,str) or len(previous)!=64:raise Denied('BAD_CHALLENGE')
 return {'resource':resource,'generation':generation,'previous':previous,'nonce':secrets.token_hex(16),'issued_ns':time.monotonic_ns(),'ttl_ns':ttl_ns}
def evidence(challenge,snapshot,private_key):
 fields={k:snapshot[k] for k in ('wal_head','wal_seq','target_head','cursor','request_id','row')}
 body={'challenge':challenge,'snapshot':fields}
 return {'body':body,'signature':private_key.sign(canonical(body)).hex()}
def check_signed(proof,challenge,public_key):
 if proof.get('body',{}).get('challenge')!=challenge:raise Denied('CHALLENGE_MISMATCH')
 try:public_key.verify(bytes.fromhex(proof['signature']),canonical(proof['body']))
 except (InvalidSignature,KeyError,ValueError,TypeError):raise Denied('BAD_SIGNATURE')
 return proof['body']['snapshot']
class Floor:
 def __init__(self,path):
  self.db=sqlite3.connect(path,isolation_level=None,timeout=5)
  self.db.execute('PRAGMA journal_mode=WAL');self.db.execute('PRAGMA synchronous=FULL')
  self.db.execute('CREATE TABLE IF NOT EXISTS floor (resource TEXT PRIMARY KEY,generation INTEGER,head TEXT)')
  self.db.execute('CREATE TABLE IF NOT EXISTS used (nonce TEXT PRIMARY KEY)')
 def head(self,resource):
  r=self.db.execute('SELECT generation,head FROM floor WHERE resource=?',(resource,)).fetchone()
  return r if r else (0,'0'*64)
 def authorize(self,challenge,proof,pub,wal,db,request_id,before_commit=None):
  signed=check_signed(proof,challenge,pub)
  if signed.get('request_id')!=request_id:raise Denied('WRONG_REQUEST')
  if challenge['ttl_ns']<=0 or time.monotonic_ns()-challenge['issued_ns']>challenge['ttl_ns']:raise Denied('EXPIRED')
  snap=capture(wal,db,request_id)
  expected={k:snap[k] for k in ('wal_head','wal_seq','target_head','cursor','request_id','row')}
  if signed!=expected:raise Denied('STALE_EVIDENCE')
  if before_commit:before_commit()
  validate_fresh(snap,wal,db,challenge['ttl_ns'])
  self.db.execute('BEGIN IMMEDIATE')
  try:
   if self.db.execute('SELECT 1 FROM used WHERE nonce=?',(challenge['nonce'],)).fetchone():raise Denied('REPLAY')
   gen,prev=self.head(challenge['resource'])
   if challenge['generation']!=gen+1 or challenge['previous']!=prev:raise Denied('FORK')
   h=digest({'previous':prev,'generation':gen+1,'evidence':signed,'nonce':challenge['nonce']})
   self.db.execute('INSERT INTO used VALUES(?)',(challenge['nonce'],))
   self.db.execute('INSERT INTO floor VALUES(?,?,?) ON CONFLICT(resource) DO UPDATE SET generation=excluded.generation,head=excluded.head',(challenge['resource'],gen+1,h))
   self.db.execute('COMMIT');return {'generation':gen+1,'head':h}
  except BaseException:self.db.execute('ROLLBACK');raise
