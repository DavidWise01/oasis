import hashlib,json,itertools
def H(p):return hashlib.sha256(json.dumps(p,sort_keys=True).encode()).hexdigest()
class Carousel:
 def __init__(self):self.m={};self.j={};self.w={};self.log={};self.delivered=set();self.acks=set()
 def submit(self,k,p):self.m[k]=dict(p);self.log[k]={'payload':dict(p),'hash':H(p),'stage':0}
 def step(self,k,crash=None):
  q=self.log[k]
  for pos in range(q['stage'],6):
   if pos==3 and H(q['payload'])!=q['hash']:return 'REJECT'
   if pos==4 and k not in self.delivered:
    self.j[k]=dict(q['payload']);self.w[k]=q['payload']['winding'];self.delivered.add(k)
   if pos==5:self.acks.add(k)
   q['stage']=pos+1
   if pos==crash:return 'CRASH'
  return 'ACK'
 def restart(self):
  q=Carousel()
  for n in ('m','j','w','log'):setattr(q,n,json.loads(json.dumps(getattr(self,n))))
  q.delivered=set(self.delivered);q.acks=set(self.acks)
  return q
checks=0
for crash,slot in itertools.product(range(6),range(6)):
 c=Carousel();key=f'A{slot}:B{slot}';payload={'id':key,'winding':slot+5,'phase':slot*4}
 c.submit(key,payload)
 assert c.step(key,crash)=='CRASH';checks+=1
 c=c.restart();assert c.step(key)=='ACK';checks+=1
 assert c.step(key)=='ACK';checks+=1
 assert len(c.delivered)==1 and c.acks=={key};checks+=1
 assert c.m[key]==c.j[key]==payload;checks+=1
 assert c.w[key]==payload['winding'];checks+=1
c=Carousel()
for i in range(6):c.submit(str(i),{'id':str(i),'winding':i})
for i in (5,0,4,1,3,2,5,5,0,2):c.step(str(i))
assert len(c.delivered)==6;checks+=1
assert len(c.m)==len(c.j)==len(c.w)==6;checks+=1
x=Carousel();x.submit('bad',{'winding':7});x.log['bad']['payload']['winding']=8
assert x.step('bad')=='REJECT' and not x.delivered;checks+=1
z=Carousel();z.submit('late',{'winding':8});assert z.step('late',4)=='CRASH';checks+=1
z=z.restart();assert z.step('late')=='ACK' and len(z.delivered)==1;checks+=1
assert checks==221
print('PASS:',checks,'checks, 36 restart scenarios')
