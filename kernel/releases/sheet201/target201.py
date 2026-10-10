"""S201 target-owned proof: independently read WAL and S179 DB before signing."""
from proof199 import inspect_wal,ProofError
from receipt198 import initialize,receipt,verify,EvidenceError
from atomic179 import audit,Denied
import json
class TargetDenial(Exception):pass
def attest(wal_path,db_path,resource,request_id,cursor,signing_key):
 db=initialize(db_path)
 try:
  wal=inspect_wal(wal_path);rec=wal['commits'].get(request_id)
  if rec is None:raise TargetDenial('WAL_NOT_COMMITTED')
  audit(db)
  binding=db.execute('SELECT resource FROM resource_binding WHERE id=1').fetchone()
  if not binding or binding[0]!=resource:raise TargetDenial('WRONG_RESOURCE')
  row=db.execute('SELECT idx,payload FROM entries WHERE request_id=?',(request_id,)).fetchone()
  if not row:raise TargetDenial('TARGET_NOT_COMMITTED')
  idx,payload=row
  if idx!=cursor:raise TargetDenial('CURSOR_MISMATCH')
  body=json.loads(payload)
  if (body.get('resource'),body.get('nonce'),body.get('walHash'),body.get('inputHash'))!=(resource,request_id,rec['walHash'],rec['inputHash']):raise TargetDenial('WAL_TARGET_DIVERGENCE')
  out=receipt(db,resource,request_id,signing_key)
  verify(out,signing_key.public_key(),resource,request_id,rec['inputHash'],rec['walHash'],idx)
  return out
 except (ProofError,EvidenceError,Denied,ValueError,KeyError) as e:raise TargetDenial('PROOF_INVALID') from e
 finally:db.close()
