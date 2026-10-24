from collections import deque
class Carousel:
 def __init__(self,dwell,elastic=True):
  self.q=deque();self.dwell=dwell;self.elastic=elastic;self.layers=3;self.accepted=[];self.exited=[];self.rejected=[];self.added=0;self.removed=0;self.peak=0
 def tick(self,t,arrivals):
  for _ in range(3):
   if self.q and self.q[0][1]<=t:self.exited.append(self.q.popleft()[0])
  for item in arrivals:
   if len(self.q)==3*self.layers:
    if not self.elastic:self.rejected.append(item);continue
    self.layers+=1;self.added+=1
   self.q.append((item,t+self.dwell,f'inference:{item}',True));self.accepted.append(item)
  self.peak=max(self.peak,len(self.q))
  while self.layers>3 and len(self.q)<=3*(self.layers-1):
   self.layers-=1;self.removed+=1
  assert len(self.accepted)==len(self.exited)+len(self.q)
  assert len(self.q)<=3*self.layers
def trial(dwell,elastic=True):
 c=Carousel(dwell,elastic)
 for t in range(120):
  c.tick(t,[f'{t}:{i}' for i in range(3)] if t<20 else [])
 assert [x[0] for x in c.exited]==c.accepted and not c.q
 assert all(x[2]==f'inference:{x[0]}' and x[3] for x in c.exited)
 assert c.layers==3
 return len(c.accepted),len(c.rejected),c.peak,c.added,c.removed
for d,expect in [(3,(60,0,9,0,0)),(7,(60,0,21,4,4)),(12,(60,0,36,9,9)),(20,(60,0,60,17,17))]:
 got=trial(d)
 assert got==expect,(d,got,expect)
 print('elastic',d,got)
assert trial(7,False)==(27,33,9,0,0)
print('PASS 5 scenarios')
