from collections import deque
import json
class Carousel:
 def __init__(self,capacity=9,dwell=3):
  self.q=deque();self.capacity=capacity;self.dwell=dwell;self.accepted=[];self.out=[];self.rejected=[]
 def tick(self,t,arrivals):
  for _ in range(3):
   if self.q and self.q[0][1]<=t:self.out.append(self.q.popleft()[0])
  for ident in arrivals:
   if len(self.q)<self.capacity:
    self.q.append((ident,t+self.dwell));self.accepted.append(ident)
   else:self.rejected.append(ident)
  assert len(self.accepted)==len(self.out)+len(self.q)
def simulate(dwell):
 c=Carousel(dwell=dwell)
 for t in range(20):c.tick(t,[f'{t}:{i}' for i in range(3)])
 for t in range(20,100):c.tick(t,[])
 assert list(c.accepted)==list(c.out)
 assert len(c.accepted)+len(c.rejected)==60
 return dict(accepted=len(c.accepted),exited=len(c.out),rejected=len(c.rejected))
assert simulate(3)==dict(accepted=60,exited=60,rejected=0)
assert simulate(7)==dict(accepted=27,exited=27,rejected=33)
print('PASS: conservation, FIFO and explicit overflow')
