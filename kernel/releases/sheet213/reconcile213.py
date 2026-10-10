"""S213 orphan reconciliation: exact WAL-tail matching and dual signed authorization."""
import json, pathlib, hashlib
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from service210 import wal_head,init
from fence209 import Denied
def canonical(x):return json.dumps(x,sort_keys=True,separators=(',',':')).encode()
def verify(item,pub,kind,expected):
 if item.get('body')!={'kind':kind,**expected}:raise Denied('WRONG_'+kind)
 try:pub.verify(bytes.fromhex(item['signature']),canonical(item['body']))
 except Exception:raise Denied('BAD_'+kind+'_SIGNATURE')
def reconcile(config,request):
 if set(request)!={'op','target','floor'} or request['op']!='reconcile':raise Denied('FIELDS')
 d=init(config['db'])
 try:
  d.execute('BEGIN IMMEDIATE')
  resource=config['resource']
  bound=d.execute('SELECT head,seq FROM bound WHERE resource=?',(resource,)).fetchone()
  if not bound:raise Denied('NO_BOUND_BASE')
  prior,offset=bound;head,seq=wal_head(config['wal'])
  if seq!=offset+2:raise Denied('TAIL_SIZE')
  rows=pathlib.Path(config['wal']).read_text().splitlines()
  prev=prior;tail=[]
  for idx,line in enumerate(rows[offset:],offset+1):
   r=json.loads(line);b={k:r[k] for k in ('seq','prev','kind','payload')}
   expected=hashlib.sha256(json.dumps(b,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
   if r['seq']!=idx or r['prev']!=prev or r['hash']!=expected:raise Denied('TAIL_CHAIN')
   prev=r['hash'];tail.append(r)
  if len(tail)!=2 or tail[0]['kind']!='prepare' or tail[1]['kind']!='commit' or tail[1]['payload'].get('nonce')!=tail[0]['payload'].get('nonce') or tail[1]['payload'].get('prepareHash')!=tail[0]['payload'].get('prepareHash') or prev!=head:raise Denied('TAIL_SEMANTICS')
  epoch,holder=d.execute('SELECT epoch,holder FROM owner WHERE resource=?',(resource,)).fetchone()
  common={'resource':resource,'previous_head':prior,'previous_seq':offset,'head':head,'seq':seq,'nonce':tail[0]['payload']['nonce'],'epoch':epoch,'holder':holder}
  key=lambda p:Ed25519PublicKey.from_public_bytes(pathlib.Path(config[p]).read_bytes())
  verify(request['target'],key('target_pub'),'target',common)
  gen=request['floor'].get('body',{}).get('generation')
  if not isinstance(gen,int) or gen<1:raise Denied('GENERATION')
  verify(request['floor'],key('floor_pub'),'floor',{**common,'generation':gen})
  d.execute('CREATE TABLE IF NOT EXISTS repair_floor(resource TEXT PRIMARY KEY,generation INTEGER NOT NULL)')
  row=d.execute('SELECT generation FROM repair_floor WHERE resource=?',(resource,)).fetchone()
  if gen!=(row[0]+1 if row else 1):raise Denied('FLOOR_GENERATION')
  d.execute('UPDATE bound SET head=?,seq=? WHERE resource=? AND head=? AND seq=?',(head,seq,resource,prior,offset))
  if d.execute('SELECT changes()').fetchone()[0]!=1:raise Denied('RACE')
  d.execute('INSERT INTO repair_floor VALUES(?,?) ON CONFLICT(resource) DO UPDATE SET generation=excluded.generation',(resource,gen))
  d.execute('COMMIT')
  return {'ok':True,'head':head,'seq':seq,'generation':gen}
 except BaseException:
  if d.in_transaction:d.execute('ROLLBACK')
  raise
 finally:d.close()
