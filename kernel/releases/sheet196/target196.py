"""S196 durable target receipt service: mTLS query, atomic SQLite commit, signed reply."""
import sqlite3, json, os
from http.server import BaseHTTPRequestHandler
from authority193 import canonical
from authority195 import certfp, respond
class Handler(BaseHTTPRequestHandler):
 def log_message(self,*args):pass
 def do_POST(self):
  try:
   if certfp(self.connection.getpeercert(binary_form=True))!=self.server.allowed:raise ValueError('CLIENT_DENIED')
   n=int(self.headers.get('Content-Length','0'))
   if not 0<n<8192:raise ValueError('REQUEST_SIZE')
   q=json.loads(self.rfile.read(n)); resource=q['resource'];nonce=q['nonce']
   if self.path=='/commit':
    if self.server.read_only:raise ValueError('READ_ONLY')
    b={'schema':'oasis.sheet194.target-receipt.v1','resource':resource,'nonce':nonce,'inputHash':q['inputHash'],'walHash':q['walHash'],'seq':q['seq']}
    d=self.server.db;d.execute('BEGIN IMMEDIATE')
    try:
     found=d.execute('SELECT body,sig FROM receipts WHERE resource=? AND nonce=?',(resource,nonce)).fetchone()
     if found and json.loads(found[0])!=b:raise ValueError('RECEIPT_FORK')
     if not found:
      sig=self.server.signer.sign(canonical(b)).hex();d.execute('INSERT INTO receipts VALUES(?,?,?,?)',(resource,nonce,canonical(b).decode(),sig))
     else:sig=found[1]
     d.execute('COMMIT')
    except BaseException:d.execute('ROLLBACK');raise
    if self.server.crash_after_commit:os._exit(137)
    return respond(self,200,{'body':b,'signature':sig})
   if self.path!='/receipt':raise ValueError('PATH')
   found=self.server.db.execute('SELECT body,sig FROM receipts WHERE resource=? AND nonce=?',(resource,nonce)).fetchone()
   if not found:raise ValueError('NO_COMMITTED_TARGET')
   respond(self,200,{'body':json.loads(found[0]),'signature':found[1]})
  except Exception as e:respond(self,409,{'error':str(e)})
