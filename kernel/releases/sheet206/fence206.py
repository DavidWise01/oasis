"""S206 cooperative writer lock; local challenge/floor authorization."""
import fcntl,os,pathlib
from contextlib import contextmanager
from challenge205 import Floor,make_challenge
@contextmanager
def lease(path,blocking=True):
 p=pathlib.Path(path);p.parent.mkdir(parents=True,exist_ok=True)
 fd=os.open(p,os.O_RDWR|os.O_CREAT,0o600)
 try:
  fcntl.flock(fd,fcntl.LOCK_EX|(0 if blocking else fcntl.LOCK_NB));yield
 finally:
  fcntl.flock(fd,fcntl.LOCK_UN);os.close(fd)
class FencedFloor(Floor):
 def __init__(self,dbpath,lockpath):super().__init__(dbpath);self.lockpath=lockpath
 def challenge(self,resource,ttl_ns=2_000_000_000):
  with lease(self.lockpath):
   generation,head=self.head(resource)
   return make_challenge(resource,generation+1,head,ttl_ns)
 def decide(self,challenge,proof,pub,wal,db,request_id,hook=None):
  with lease(self.lockpath):
   return self.authorize(challenge,proof,pub,wal,db,request_id,before_commit=hook)
