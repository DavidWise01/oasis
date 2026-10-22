"""Step 17: committed snapshot, bounded compaction, validated restore. Stdlib only."""
import hashlib,json,os,tempfile
from pathlib import Path
from struct import pack
def canonical(x):return json.dumps(x,sort_keys=True,separators=(',',':')).encode()
def digest(i,t,p,prior):return hashlib.sha256(canonical(dict(index=i,term=t,payload=p,prior=prior))).hexdigest()
def packet(t):
 q,p=divmod(t,86400)
 return b'IT3\x01'+pack('>qI',q,((q&1)<<31)|p)
class Ledger:
 def __init__(self):
  self.base_index=0;self.base_hash='0'*64;self.entries=[];self.commit_index=0
 def append(self,term,ts):
  i=self.base_index+len(self.entries)+1
  prior=self.entries[-1]['hash'] if self.entries else self.base_hash
  p=packet(ts).hex()
  e=dict(index=i,term=term,payload=p,prior=prior,hash=digest(i,term,p,prior))
  self.entries.append(e);self.commit_index=i;return e
 def verify(self):
  h=self.base_hash
  for i,e in enumerate(self.entries,self.base_index+1):
   if e['index']!=i or e['prior']!=h or e['hash']!=digest(i,e['term'],e['payload'],h):raise ValueError('chain')
   if len(bytes.fromhex(e['payload']))!=16:raise ValueError('payload')
   h=e['hash']
  if self.commit_index!=self.base_index+len(self.entries):raise ValueError('commit')
  return h
 def snapshot(self,at=None):
  self.verify();at=self.commit_index if at is None else at
  if not self.base_index<=at<=self.commit_index:raise ValueError('uncommitted')
  rows=self.entries[:at-self.base_index];head=rows[-1]['hash'] if rows else self.base_hash
  body=dict(version=1,base_index=self.base_index,base_hash=self.base_hash,index=at,head=head,records=rows)
  return dict(body=body,digest=hashlib.sha256(canonical(body)).hexdigest())
 @staticmethod
 def restore(s):
  if set(s)!={'body','digest'} or hashlib.sha256(canonical(s['body'])).hexdigest()!=s['digest']:raise ValueError('digest')
  b=s['body']
  if b['version']!=1:raise ValueError('version')
  x=Ledger();x.base_index=b['base_index'];x.base_hash=b['base_hash'];x.entries=list(b['records']);x.commit_index=b['index']
  if x.verify()!=b['head']:raise ValueError('head')
  return x
 def compact(self,s):
  v=Ledger.restore(s);at=v.commit_index
  if v.base_index!=self.base_index or v.base_hash!=self.base_hash or at>self.commit_index or self.entries[:at-self.base_index]!=v.entries:raise ValueError('anchor')
  self.entries=self.entries[at-self.base_index:];self.base_index=at;self.base_hash=v.verify()
def persist(path,s):
 path=Path(path);tmp=path.with_name(path.name+'.tmp')
 with tmp.open('wb') as f:f.write(canonical(s));f.flush();os.fsync(f.fileno())
 os.replace(tmp,path)
 fd=os.open(path.parent,os.O_RDONLY|getattr(os,'O_DIRECTORY',0))
 try:os.fsync(fd)
 finally:os.close(fd)
def test():
 l=Ledger()
 for i,t in enumerate([2147483647,2147483648,4102444800],1):l.append(i,t)
 head=l.verify();print('PASS committed chain')
 snap=l.snapshot(2);assert Ledger.restore(snap).commit_index==2;print('PASS restore')
 with tempfile.TemporaryDirectory() as d:
  p=Path(d)/'s.json';persist(p,snap);assert Ledger.restore(json.loads(p.read_text())).verify()==snap['body']['head'];print('PASS persistent readback')
  bad=json.loads(p.read_text());bad['body']['records'][0]['payload']='00'*16
  try:Ledger.restore(bad);raise AssertionError('bad accepted')
  except ValueError:pass
  print('PASS corruption rejected')
 l.compact(snap);assert len(l.entries)==1 and l.verify()==head;print('PASS compaction continuity')
 assert l.append(4,5000000000)['prior']==head;print('PASS append after compaction')
 try:l.snapshot(l.commit_index+1);raise AssertionError('future accepted')
 except ValueError:pass
 print('PASS uncommitted future rejected')
 try:l.compact(snap);raise AssertionError('stale accepted')
 except ValueError:pass
 print('PASS stale snapshot rejected')
 print('RESULT 8/8 PASS')
if __name__=='__main__':test()
