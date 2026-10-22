"""BIFROST 11D — no SQL, symbolic toroidal append-only journal."""
import json, hashlib, os, tempfile
from pathlib import Path
from decimal import Decimal
EDGES=[(i,i+1) for lo,hi in ((122,125),(140,145),(360,366)) for i in range(lo,hi)]
BANDS=('H','O','N')
PATHS=('---','--+','-+-','-++','+--','+-+','++-','+++')
def coordinate(slot,phase,band,path):
 n=slot-1
 return (n//256,(n//64)%4,(n//16)%4,(n//4)%4,n%4,
         *(int(c=='+') for c in path),BANDS.index(band),phase%60,n)
def encode(o): return json.dumps(o,sort_keys=True,separators=(',',':'))
def load(path):
 b={i:Decimal(100) for i in range(1,367)}; done=set();last='0'*64
 if not path.exists():return b,done,last
 for line in path.read_text().splitlines():
  e=json.loads(line);body={k:v for k,v in e.items() if k!='hash'}
  assert e['prev']==last and hashlib.sha256(encode(body).encode()).hexdigest()==e['hash']
  i=e['seq'];a,z=EDGES[i];assert i not in done and (a,z)==(e['src'],e['dst'])
  amt=b[a]*Decimal('.025');assert str(amt)==e['amount']
  b[a]-=amt;b[z]+=amt;done.add(i);last=e['hash']
 return b,done,last
def execute(path,halt=None):
 b,done,last=load(path)
 for i,(a,z) in enumerate(EDGES):
  if i in done:continue
  if i==halt:return 'HALT'
  amt=b[a]*Decimal('.025')
  body={'seq':i,'src':a,'dst':z,'amount':str(amt),'prev':last,'origin':'0vwxyz'}
  body['hash']=hashlib.sha256(encode(body).encode()).hexdigest()
  with path.open('a') as f:f.write(encode(body)+'\n');f.flush();os.fsync(f.fileno())
  b[a]-=amt;b[z]+=amt;last=body['hash']
 return 'COMPLETE'
def test():
 assert len(EDGES)==14
 assert len(coordinate(122,0,'H','---'))==11
 assert len({coordinate(s,p,b,g) for s in range(1,367) for p in (0,1) for b in BANDS for g in PATHS})==366*2*3*8
 assert all(coordinate(s,60,'H','---')==coordinate(s,0,'H','---') for s in (1,122,366))
 with tempfile.TemporaryDirectory() as d:
  root=Path(d);base=root/'base.jsonl';execute(base)
  b,done,_=load(base);assert len(done)==14 and sum(b.values())==Decimal(36600)
  original=base.read_bytes();execute(base);assert base.read_bytes()==original
  for i in range(14):
   p=root/f'{i}.jsonl';assert execute(p,halt=i)=='HALT'
   assert execute(p)=='COMPLETE' and p.read_bytes()==original
  bad=root/'bad.jsonl';bad.write_bytes(original.replace(b'0vwxyz',b'0vwxyZ',1))
  try:load(bad);raise AssertionError('undetected alteration')
  except AssertionError as e:
   if str(e)=='undetected alteration':raise
 return {'status':'PASS','checks':8,'restarts':14,'dimensions':11,'channels':24,'phase_bins':60,'origin':'0vwxyz','storage':'JSONL fsync, no SQL','limits':'single writer; no torn-record repair or power-loss guarantee'}
if __name__=='__main__':print(json.dumps(test(),indent=2))
