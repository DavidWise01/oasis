"""Phase 2 transport contract tests. Fixtures are NOT a real consensus engine."""
from phase2_adapter import CommitNotVerified, publish
class Fake:
    def __init__(self, revision=7, committed=None, readback=None):
        self.revision=revision;self.committed=committed;self.readback=readback
    def submit(self,key,value):
        self.last=value
        return self.revision,value if self.committed is None else self.committed
    def read(self,key):
        return self.revision,self.last if self.readback is None else self.readback

class Offline:
    def submit(self,key,value):raise ConnectionError("offline")
    def read(self,key):raise AssertionError("should not read")

def rejected(fn):
    try:fn()
    except (ValueError, CommitNotVerified):return
    raise AssertionError("unsafe acceptance")
def test():
    cases=0
    def ok(x,name):
        nonlocal cases
        assert x,name
        cases+=1;print("PASS",name)
    r=publish(Fake(),"boundary-2038",2147483648)
    ok(r.revision==7 and r.unix_seconds==2147483648,"valid receipt")
    rejected(lambda:publish(Fake(committed=b"x"),"x",0))
    ok(True,"wrong committed bytes rejected")
    rejected(lambda:publish(Fake(readback=b"x"),"x",0))
    ok(True,"wrong readback rejected")
    rejected(lambda:publish(Fake(revision=0),"x",0))
    ok(True,"missing commit revision rejected")
    rejected(lambda:publish(Offline(),"x",0))
    ok(True,"offline commit uncertainty rejected")
    rejected(lambda:publish(Fake(),"../escape",0))
    ok(True,"record identifier validated")
    for t in (-(1<<63),-1,0,2147483647,2147483648,(1<<63)-1):
        ok(publish(Fake(),"time",t).unix_seconds==t,"time boundary "+str(t))
    print("RESULT",cases,"/ 12 PASS (mock transport only)")
if __name__=="__main__":test()
