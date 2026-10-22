"""Step 16 authenticated envelope model. DEMO KEYS ONLY, not TLS or production Raft."""
import hashlib,hmac,json
from dataclasses import dataclass,field
KEYS={n:hashlib.sha256(('demo-only-'+n).encode()).digest() for n in 'ABC'}
def canon(x):return json.dumps(x,sort_keys=True,separators=(',',':')).encode()
def sign(sender,term,sequence,payload):
 if sender not in KEYS:raise ValueError('unknown member')
 body=dict(sender=sender,term=term,sequence=sequence,payload=payload)
 return dict(body=body,tag=hmac.new(KEYS[sender],canon(body),hashlib.sha256).hexdigest())
@dataclass
class Receiver:
 highest_term:int=0
 seen:dict=field(default_factory=dict)
 def accept(self,msg):
  if not isinstance(msg,dict) or set(msg)!={'body','tag'} or not isinstance(msg['body'],dict):return False
  b=msg['body']
  if set(b)!={'sender','term','sequence','payload'}:return False
  sender=b['sender']
  if not isinstance(sender,str) or sender not in KEYS:return False
  if type(b['term']) is not int or type(b['sequence']) is not int:return False
  if b['term']<0 or b['sequence']<1 or not isinstance(b['payload'],str) or not isinstance(msg['tag'],str):return False
  if not hmac.compare_digest(msg['tag'],hmac.new(KEYS[sender],canon(b),hashlib.sha256).hexdigest()):return False
  if b['term']<self.highest_term:return False
  if b['term']>self.highest_term:self.highest_term=b['term'];self.seen={}
  if b['sequence']<=self.seen.get(sender,0):return False
  self.seen[sender]=b['sequence'];return True
def test():
 r=Receiver();m=sign('A',1,1,'IT3:2147483648')
 assert r.accept(m);print('PASS authenticated member')
 assert not r.accept(m);print('PASS replay')
 assert not r.accept(dict(body=dict(m['body'],payload='IT3:0'),tag=m['tag']));print('PASS tamper')
 assert not r.accept(dict(body=dict(m['body'],sender='D'),tag=m['tag']));print('PASS nonmember')
 assert r.accept(sign('B',2,1,'new term'));print('PASS term advanced')
 assert not r.accept(sign('A',1,2,'old'));print('PASS stale term')
 assert r.accept(sign('B',2,2,'next'));print('PASS sequence')
 assert not r.accept(sign('B',2,1,'delayed'));print('PASS delayed replay')
 print('RESULT 8/8 PASS')
if __name__=='__main__':test()
