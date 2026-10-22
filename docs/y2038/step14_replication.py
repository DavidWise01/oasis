"""Step 14: three disk-backed replicas, bounded quorum model; NOT full Raft."""
import json,os,tempfile,hashlib
from pathlib import Path
class Replica:
 def __init__(self,root,name):
  self.dir=Path(root)/name;self.dir.mkdir(exist_ok=True);self.path=self.dir/'state.json'
  if not self.path.exists():self.save(dict(term=0,entries=[],commit=0))
  self.state=json.loads(self.path.read_text())
 def save(self,state):
  tmp=self.dir/'state.tmp'
  with tmp.open('w') as f:
   json.dump(state,f,sort_keys=True);f.flush();os.fsync(f.fileno())
  os.replace(tmp,self.path)
  fd=os.open(self.dir,os.O_RDONLY)
  try:os.fsync(fd)
  finally:os.close(fd)
  self.state=state
 def append(self,term,entry,prefix):
  if term<self.state['term'] or self.state['entries']!=prefix:return False
  self.save(dict(self.state,term=term,entries=prefix+[entry]));return True
 def commit(self,index):
  if index>len(self.state['entries']):return False
  self.save(dict(self.state,commit=max(index,self.state['commit'])));return True
class Cluster:
 def __init__(self,root):
  self.nodes={n:Replica(root,n) for n in 'abc'};self.leader=None
  self.term=max(r.state['term'] for r in self.nodes.values())
 def elect(self,name,reachable):
  if name not in reachable or len(reachable)<2:return False
  maxcommit=max(r.state['commit'] for r in self.nodes.values())
  trusted=[r.state['entries'][:maxcommit] for r in self.nodes.values() if r.state['commit']==maxcommit]
  if self.nodes[name].state['entries'][:maxcommit] not in trusted:return False
  self.term+=1;self.leader=name
  for n in reachable:
   r=self.nodes[n];r.save(dict(r.state,term=self.term))
  return True
 def propose(self,payload,reachable):
  if self.leader not in reachable:return False
  leader=self.nodes[self.leader]
  if leader.state['term']!=self.term:return False
  prefix=leader.state['entries'][:]
  entry=dict(term=self.term,payload=payload,prior=hashlib.sha256(json.dumps(prefix,sort_keys=True).encode()).hexdigest())
  ack=[n for n in reachable if self.nodes[n].append(self.term,entry,prefix)]
  if len(ack)<2:return False
  for n in ack:self.nodes[n].commit(len(prefix)+1)
  return True
 def sync(self,node):
  self.nodes[node].save(dict(self.nodes[self.leader].state))
def test():
 with tempfile.TemporaryDirectory() as d:
  c=Cluster(d)
  assert c.elect('a',{'a','b','c'});print('PASS election')
  assert c.propose('IT3:2147483648',{'a','b'});print('PASS 2/3 fsynced proposal')
  assert c.nodes['a'].state['commit']==c.nodes['b'].state['commit']==1;print('PASS commit index')
  c=Cluster(d);assert c.nodes['a'].state['commit']==1;print('PASS restart')
  assert not c.elect('c',{'b','c'});print('PASS stale candidate rejection')
  assert c.elect('b',{'a','b'});print('PASS leader change')
  assert not c.propose('minority',{'b'});print('PASS minority blocked')
  c.sync('c');assert c.nodes['c'].state['commit']==1;print('PASS catch-up')
 print('RESULT 8/8 PASS, single-host bounded model only')
if __name__=='__main__':test()
