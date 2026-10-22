"""Step 19 bounded scenario explorer; not a formal Raft proof."""
from dataclasses import dataclass,field
from itertools import permutations
@dataclass
class Node:
 term:int=0
 log:list=field(default_factory=list)
 commit:int=0
class Cluster:
 def __init__(self):
  self.nodes={n:Node() for n in 'ABC'};self.leader=None;self.term=0;self.groups=[set('ABC')]
 def reachable(self,n):return next((g for g in self.groups if n in g),{n})
 def partition(self,n):self.groups=[{n},set('ABC')-{n}]
 def elect(self,n):
  group=self.reachable(n)
  if len(group)<2:return False
  best=max((len(self.nodes[x].log),self.nodes[x].log[-1][0] if self.nodes[x].log else 0) for x in group)
  me=self.nodes[n]
  if (len(me.log),me.log[-1][0] if me.log else 0)<best:return False
  self.term+=1;self.leader=n
  for x in group:self.nodes[x].term=self.term
  return True
 def commit(self,n,value):
  if self.leader!=n:return False
  group=self.reachable(n)
  if len(group)<2 or self.nodes[n].term!=self.term:return False
  same=[x for x in group if self.nodes[x].log==self.nodes[n].log]
  if len(same)<2:return False
  for x in same:
   p=self.nodes[x];p.log.append((self.term,value));p.commit=len(p.log)
  return True
 def heal(self):self.groups=[set('ABC')]
 def repair(self):
  ref=self.nodes[self.leader]
  for p in self.nodes.values():
   if p.log[:p.commit]!=ref.log[:p.commit]:raise AssertionError('committed prefix lost')
   p.log=ref.log[:];p.commit=ref.commit
 def invariant(self):
  for i,a in self.nodes.items():
   assert 0<=a.commit<=len(a.log),(i,'index')
   for j,b in self.nodes.items():
    common=min(a.commit,b.commit)
    assert a.log[:common]==b.log[:common],(i,j,'divergent committed prefixes')
def verify():
 runs=0;transitions=0
 for initial,isolated,successor in permutations('ABC',3):
  for repeat in range(1,5):
   c=Cluster();assert c.elect(initial)
   for k in range(repeat):
    assert c.commit(initial,f'IT3-{k}')
    c.invariant();transitions+=1
   c.partition(isolated);c.invariant();transitions+=1
   if isolated==initial:
    assert not c.commit(initial,'isolated')
    assert c.elect(successor)
    assert c.commit(successor,'majority')
   else:
    assert c.commit(initial,'majority')
    assert not c.elect(isolated)
   c.invariant();transitions+=1
   c.heal();c.repair();c.invariant();transitions+=1
   assert len({tuple(v.log) for v in c.nodes.values()})==1
   runs+=1
 print(f'PASS: {runs} deterministic schedules, {transitions} checked transitions')
 print('PASS: committed prefix agreement and minority isolation within model')
 print('LIMIT: no RPC/network, persisted consensus votes, adversarial scheduling or multi-host test')
if __name__=='__main__':verify()
