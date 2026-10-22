import os, pathlib, tempfile, hashlib, multiprocessing, struct
MAGIC=b'IT3S'
def frame(t):
 q,p=divmod(t,86400); w=b'IT3\x01'+struct.pack('>qI',q,((q&1)<<31)|p)
 return MAGIC+w+hashlib.sha256(w).digest()
def read(path):
 x=path.read_bytes()
 if len(x)!=52 or x[:4]!=MAGIC or hashlib.sha256(x[4:20]).digest()!=x[20:]: raise ValueError('invalid record')
 q,f=struct.unpack('>qI',x[8:20]);p=f&0x1ffff
 if f&0x7ffe0000 or p>=86400 or f>>31!=(q&1):raise ValueError('invalid packet')
 return q*86400+p
def sync_dir(d):
 fd=os.open(d,os.O_RDONLY|getattr(os,'O_DIRECTORY',0))
 try:os.fsync(fd)
 finally:os.close(fd)
def commit(root,t):
 import fcntl
 lock=root/'lock';current=root/'current.it3s';pending=root/'pending.it3s'
 with open(lock,'a+b') as lf:
  fcntl.flock(lf,fcntl.LOCK_EX)
  try:
   with open(pending,'wb') as f:
    f.write(frame(t));f.flush();os.fsync(f.fileno())
   assert read(pending)==t
   os.replace(pending,current)
   sync_dir(root)
  finally:fcntl.flock(lf,fcntl.LOCK_UN)
def worker(root,t):commit(pathlib.Path(root),t)
def test():
 with tempfile.TemporaryDirectory() as d:
  root=pathlib.Path(d);cur=root/'current.it3s';pending=root/'pending.it3s'
  commit(root,2147483648);assert read(cur)==2147483648;print('PASS sync commit')
  pending.write_bytes(frame(4102444800)[:11]);assert read(cur)==2147483648;print('PASS interrupted staging unchanged')
  commit(root,4102444800);assert read(cur)==4102444800 and not pending.exists();print('PASS recovery staged replacement')
  jobs=[multiprocessing.Process(target=worker,args=(d,2147483648+i)) for i in range(12)]
  for j in jobs:j.start()
  for j in jobs:j.join();assert j.exitcode==0
  assert read(cur) in range(2147483648,2147483660);print('PASS concurrent writers serialized')
  assert not pending.exists();print('PASS no pending path after writes')
  assert len(cur.read_bytes())==52;print('PASS committed record intact')
 print('RESULT 6/6 PASS')
if __name__=='__main__':test()
