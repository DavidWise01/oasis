"""SHEET 203: target-owned, floor-compatible receipt endpoint."""
import json,hashlib
from service202 import ProofHandler,make_server
from receipt198 import initialize
from target201 import attest,TargetDenial
class FloorTarget203(ProofHandler):
 def do_POST(self):
  def reply(code,obj):
   b=json.dumps(obj,sort_keys=True).encode()
   self.send_response(code);self.send_header('Content-Length',str(len(b)));self.end_headers();self.wfile.write(b)
  try:
   cert=self.connection.getpeercert(binary_form=True)
   if not cert or hashlib.sha256(cert).hexdigest() not in self.server.client_fingerprints:raise TargetDenial('CLIENT_DENIED')
   if self.path!='/receipt':raise TargetDenial('PATH')
   length=int(self.headers.get('Content-Length','0'))
   if not 0<length<=4096:raise TargetDenial('SIZE')
   obj=json.loads(self.rfile.read(length))
   if not isinstance(obj,dict) or set(obj)!={'resource','nonce'}:raise TargetDenial('FIELDS')
   if obj['resource']!=self.server.resource or not isinstance(obj['nonce'],str) or not obj['nonce']:raise TargetDenial('SCOPE')
   d=initialize(self.server.db_path)
   try:row=d.execute('SELECT idx FROM entries WHERE request_id=?',(obj['nonce'],)).fetchone()
   finally:d.close()
   if not row:raise TargetDenial('NO_TARGET')
   proof=attest(self.server.wal_path,self.server.db_path,obj['resource'],obj['nonce'],row[0],self.server.signer)
   reply(200,proof)
  except (TargetDenial,KeyError,TypeError,ValueError) as e:reply(409,{'error':str(e)})
  except Exception:reply(503,{'error':'UNAVAILABLE'})
def make_floor_target(*args,**kwargs):
 s=make_server(*args,**kwargs);s.RequestHandlerClass=FloorTarget203;return s
