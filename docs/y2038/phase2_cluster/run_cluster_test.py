"""Phase 2.3 local 3-etcd Docker experiment. No TLS: NEVER use in production."""
import base64,json,subprocess,time,struct,sys
from pathlib import Path
from urllib.request import Request,urlopen
ROOT=Path(__file__).resolve().parent
URL={'node1':'http://127.0.0.1:12379','node2':'http://127.0.0.1:22379','node3':'http://127.0.0.1:32379'}
def compose(*args):subprocess.run(['docker','compose','-f',str(ROOT/'compose.yaml'),*args],check=True)
def b64(x):return base64.b64encode(x).decode()
def post(node,path,payload):
 req=Request(URL[node]+path,json.dumps(payload).encode(),{'Content-Type':'application/json'},method='POST')
 with urlopen(req,timeout=2) as r:return json.load(r)
def health(node):
 with urlopen(URL[node]+'/health',timeout=2) as r:return json.load(r).get('health') in ('true',True)
def packet(t):
 q,p=divmod(t,86400)
 return b'IT3\x01'+struct.pack('>qI',q,((q&1)<<31)|p)
def put(node,key,value):
 result=post(node,'/v3/kv/txn',{'compare':[{'key':b64(key),'target':'CREATE','result':'EQUAL','create_revision':'0'}],'success':[{'request_put':{'key':b64(key),'value':b64(value)}}],'failure':[]})
 if result.get('succeeded') is not True:raise AssertionError('write rejected')
def get(node,key):
 r=post(node,'/v3/kv/range',{'key':b64(key),'serializable':False})
 return base64.b64decode(r['kvs'][0]['value'])
def wait(fn,seconds=50):
 stop=time.monotonic()+seconds
 while time.monotonic()<stop:
  try:
   if fn():return
  except Exception:pass
  time.sleep(.5)
 raise AssertionError('readiness timeout')
def main():
 compose('up','-d')
 wait(lambda:all(health(n) for n in URL))
 print('PASS 3 healthy members')
 first=packet(2147483648);put('node1',b'it3/p23/one',first)
 assert get('node3',b'it3/p23/one')==first
 print('PASS cross-node byte readback')
 compose('stop','node3')
 second=packet(4102444800);put('node1',b'it3/p23/two',second)
 assert get('node2',b'it3/p23/two')==second
 print('PASS 2/3 write')
 compose('stop','node2')
 try:put('node1',b'it3/p23/isolated',packet(0))
 except Exception:print('PASS minority write not acknowledged')
 else:raise AssertionError('unsafe minority acknowledgment')
 compose('start','node2')
 wait(lambda:get('node2',b'it3/p23/two')==second)
 print('PASS majority recovery')
 compose('start','node3')
 wait(lambda:get('node3',b'it3/p23/two')==second)
 print('PASS follower catch-up')
 print('RESULT 6/6 PASS')
if __name__=='__main__':
 if '--clean' in sys.argv:compose('down','--volumes')
 elif '--down' in sys.argv:compose('down')
 else:main()
