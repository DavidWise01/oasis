"""Phase 2.4 idempotent retry contract; deterministic mocks, NOT a real cluster."""
from phase2_idempotent import publish_once,UncertainCommit,IdentityConflict
from phase2_etcd import EtcdConflict
class Fake:
 def __init__(self):
  self.store={};self.rev=1;self.fail_after_write=False;self.no_read=False
 def submit(self,k,v):
  if k in self.store:raise EtcdConflict('exists')
  self.rev+=1;self.store[k]=v
  if self.fail_after_write:raise TimeoutError('response lost')
  return self.rev,v
 def read(self,k):
  if self.no_read:raise TimeoutError('offline')
  if k not in self.store:raise ValueError('missing')
  return self.rev,self.store[k]
def reject(cls,fn):
 try:fn()
 except cls:return
 raise AssertionError('expected '+cls.__name__)
def test():
 count=0
 def check(ok,desc):
  nonlocal count
  assert ok,desc
  count+=1;print('PASS',desc)
 b=Fake()
 a=publish_once(b,'one',2147483648)
 check(a.outcome=='created','create')
 a=publish_once(b,'one',2147483648)
 check(a.outcome=='existing','idempotent duplicate')
 reject(IdentityConflict,lambda:publish_once(b,'one',2147483649))
 check(True,'conflicting identity rejected')
 b=Fake();b.fail_after_write=True
 a=publish_once(b,'two',4102444800)
 check(a.outcome=='uncertain' and a.unix_seconds==4102444800,'lost ack resolved by readback')
 b.no_read=True
 reject(UncertainCommit,lambda:publish_once(b,'three',0))
 check(True,'unavailable linearizable read fails closed')
 reject(ValueError,lambda:publish_once(Fake(),'../invalid',0))
 check(True,'identifier validation')
 for t in (-(1<<63),-1,0,2147483647,2147483648,(1<<63)-1):
  check(publish_once(Fake(),'test',t).unix_seconds==t,'boundary '+str(t))
 print('RESULT',count,'/ 12 PASS (mock only)')
if __name__=='__main__':test()
