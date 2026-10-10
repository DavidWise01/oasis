"""Read-only target-owned mTLS proof endpoint. Evidence paths are configured server-side."""
import json,ssl,hashlib
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from target201 import attest,TargetDenial
class ProofHandler(BaseHTTPRequestHandler):
 def log_message(self,*args):pass
 def do_POST(self):
  def reply(code,body):
   raw=json.dumps(body,sort_keys=True).encode();self.send_response(code);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(raw)));self.end_headers();self.wfile.write(raw)
  try:
   cert=self.connection.getpeercert(binary_form=True)
   if cert is None or hashlib.sha256(cert).hexdigest() not in self.server.client_fingerprints:raise TargetDenial('UNAUTHORIZED_CLIENT')
   if self.path!='/receipt':raise TargetDenial('PATH_DENIED')
   length=int(self.headers.get('Content-Length','0'))
   if not 0<length<=4096:raise TargetDenial('REQUEST_LENGTH')
   q=json.loads(self.rfile.read(length))
   if not isinstance(q,dict) or set(q)!={'resource','nonce','cursor'}:raise TargetDenial('EVIDENCE_FIELDS_FORBIDDEN')
   if q['resource']!=self.server.resource or not isinstance(q['nonce'],str) or not q['nonce'] or type(q['cursor']) is not int or q['cursor']<1:raise TargetDenial('RESOURCE_OR_CURSOR')
   receipt=attest(self.server.wal_path,self.server.db_path,self.server.resource,q['nonce'],q['cursor'],self.server.signer)
   reply(200,receipt)
  except (TargetDenial,ValueError,TypeError,KeyError) as e:reply(409,{'error':str(e)})
  except Exception:reply(503,{'error':'PROOF_UNAVAILABLE'})
def make_server(port,wal,db,resource,signer,cert,key,ca,allowed):
 srv=ThreadingHTTPServer(('127.0.0.1',port),ProofHandler);srv.wal_path=str(wal);srv.db_path=str(db);srv.resource=resource;srv.signer=signer;srv.client_fingerprints=set(allowed)
 ctx=ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER);ctx.minimum_version=ssl.TLSVersion.TLSv1_2;ctx.load_cert_chain(str(cert),str(key));ctx.load_verify_locations(cafile=str(ca));ctx.verify_mode=ssl.CERT_REQUIRED;srv.socket=ctx.wrap_socket(srv.socket,server_side=True)
 return srv
