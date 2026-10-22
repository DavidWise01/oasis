"""Mock transport tests; no live cluster verification."""
import unittest,base64
from phase2_etcd import EtcdGateway,EtcdConflict
from phase2_adapter import publish,CommitNotVerified
class Fake(EtcdGateway):
 def __init__(self):
  self.records={};self.rev=1;self.corrupt=False;self.calls=[]
 def _post(self,path,payload):
  self.calls.append((path,payload))
  k=base64.b64decode(payload.get('key',payload.get('compare',[{}])[0].get('key','')))
  if path.endswith('/txn'):
   if k in self.records:return {'header':{'revision':str(self.rev)},'succeeded':False}
   self.rev+=1;self.records[k]=base64.b64decode(payload['success'][0]['request_put']['value'])
   return {'header':{'revision':str(self.rev)},'succeeded':True}
  if k not in self.records:return {'header':{'revision':str(self.rev)},'kvs':[]}
  v=b'corrupt' if self.corrupt else self.records[k]
  return {'header':{'revision':str(self.rev)},'kvs':[{'key':base64.b64encode(k).decode(),'value':base64.b64encode(v).decode()}]}
class Tests(unittest.TestCase):
 def test_01_create(self):
  f=Fake();r=publish(f,'boundary',2147483648)
  self.assertEqual(r.unix_seconds,2147483648)
  self.assertEqual(f.calls[0][1]['compare'][0]['create_revision'],'0')
  self.assertFalse(f.calls[1][1]['serializable'])
 def test_02_duplicate(self):
  f=Fake();publish(f,'id',0)
  with self.assertRaises(EtcdConflict):publish(f,'id',1)
 def test_03_corrupt(self):
  f=Fake();f.corrupt=True
  with self.assertRaises(CommitNotVerified):publish(f,'id',0)
 def test_04_missing(self):
  with self.assertRaises(ValueError):Fake().read(b'unknown')
 def test_05_https(self):
  with self.assertRaises(ValueError):EtcdGateway('http://localhost:2379','ca','cert','key')
  with self.assertRaises(ValueError):EtcdGateway('https://localhost:2379','','cert','key')
 def test_06_revision(self):
  with self.assertRaises(ValueError):EtcdGateway._revision({'header':{'revision':'0'}})
 def test_07_times(self):
  for t in (-(1<<63),-1,0,2147483647,2147483648,(1<<63)-1):
   self.assertEqual(publish(Fake(),'id',t).unix_seconds,t)
if __name__=='__main__':unittest.main(verbosity=2)
