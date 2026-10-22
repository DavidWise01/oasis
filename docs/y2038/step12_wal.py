"""Step 12: single-node persisted term and append-only hash-chain WAL."""
import os,hashlib,json,tempfile
from pathlib import Path
class WAL:
 def __init__(self,root):
  self.root=Path(root);self.root.mkdir(parents=True,exist_ok=True)
  self.term_path=self.root/'term';self.log_path=self.root/'log'
  if not self.term_path.exists():self.atomic(self.term_path,b'0\n')
  if not self.log_path.exists():self.atomic(self.log_path,b'')
  self.read()
 def atomic(self,path,data):
  name=self.root/'staging'
  with name.open('wb') as f:f.write(data);f.flush();os.fsync(f.fileno())
  os.replace(name,path)
  fd=os.open(self.root,os.O_RDONLY|getattr(os,'O_DIRECTORY',0))
  try:os.fsync(fd)
  finally:os.close(fd)
 @property
 def term(self):return int(self.term_path.read_text())
 def advance(self,term):
  if type(term)!=int or term<=self.term:raise ValueError('non-increasing term')
  self.atomic(self.term_path,f'{term}\n'.encode())
 def read(self):
  self.entries=[];head='0'*64
  data=self.log_path.read_bytes()
  if data and not data.endswith(b'\n'):raise ValueError('torn WAL tail')
  for line in data.splitlines():
   r=json.loads(line)
   body=f"{r['index']}|{r['term']}|{r['packet']}|{head}".encode()
   if r['index']!=len(self.entries)+1 or r['prior']!=head or r['hash']!=hashlib.sha256(body).hexdigest():raise ValueError('WAL chain mismatch')
   head=r['hash'];self.entries.append(r)
 def append(self,term,packet):
  if term!=self.term:raise ValueError('stale term')
  if len(packet)!=16 or packet[:4]!=b'IT3\x01':raise ValueError('invalid IT3 header')
  prior=self.entries[-1]['hash'] if self.entries else '0'*64
  index=len(self.entries)+1;data=packet.hex()
  h=hashlib.sha256(f'{index}|{term}|{data}|{prior}'.encode()).hexdigest()
  r=dict(index=index,term=term,packet=data,prior=prior,hash=h)
  with self.log_path.open('ab') as f:f.write((json.dumps(r,separators=(',',':'))+'\n').encode());f.flush();os.fsync(f.fileno())
  self.entries.append(r)
def test():
 with tempfile.TemporaryDirectory() as root:
  w=WAL(root);w.advance(1);pkt=bytes.fromhex('49543301000000000000611780002d80')
  w.append(1,pkt);assert len(w.entries)==1;print('PASS durable append')
  w=WAL(root);assert len(w.entries)==1;print('PASS reopen')
  w.advance(2)
  try:w.append(1,pkt);raise AssertionError('stale term accepted')
  except ValueError:pass
  print('PASS term fencing')
  w.append(2,pkt);assert len(WAL(root).entries)==2;print('PASS new term append')
  with w.log_path.open('ab') as f:f.write(b'broken');f.flush();os.fsync(f.fileno())
  try:WAL(root);raise AssertionError('torn record accepted')
  except ValueError:pass
  print('PASS torn tail detected')
  with w.log_path.open('rb+') as f:f.seek(-6,2);f.truncate();f.flush();os.fsync(f.fileno())
  assert len(WAL(root).entries)==2;print('PASS preserved prefix')
 print('RESULT 6/6 PASS')
if __name__=='__main__':test()
