"""etcd v3 JSON gateway backend; HTTPS + client certificates mandatory."""
import base64,json,ssl
from urllib.request import Request,urlopen
class EtcdConflict(RuntimeError):pass
class EtcdGateway:
 def __init__(self,url,ca_file,cert_file,key_file,*,transport=None):
  if not isinstance(url,str) or not url.startswith('https://') or '?' in url or '#' in url:raise ValueError('HTTPS required')
  if not all((ca_file,cert_file,key_file)):raise ValueError('mTLS credentials required')
  self.base=url.rstrip('/')
  context=ssl.create_default_context(cafile=ca_file)
  context.load_cert_chain(certfile=cert_file,keyfile=key_file)
  self.context=context;self.transport=transport
 def _post(self,path,payload):
  if self.transport is not None:response=self.transport(path,payload)
  else:
   req=Request(self.base+path,data=json.dumps(payload,sort_keys=True,separators=(',',':')).encode(),headers={'Content-Type':'application/json'},method='POST')
   with urlopen(req,timeout=5,context=self.context) as resp:response=json.loads(resp.read(1048576))
  if not isinstance(response,dict) or 'error' in response:raise ValueError('invalid etcd response')
  return response
 @staticmethod
 def _b64(data):return base64.b64encode(data).decode('ascii')
 @staticmethod
 def _revision(response):
  rev=response.get('header',{}).get('revision')
  if not isinstance(rev,str) or not rev.isdecimal() or int(rev)<1:raise ValueError('missing etcd revision')
  return int(rev)
 def submit(self,key,value):
  k=self._b64(key)
  request={'compare':[{'key':k,'target':'CREATE','result':'EQUAL','create_revision':'0'}],
           'success':[{'request_put':{'key':k,'value':self._b64(value)}}],'failure':[]}
  response=self._post('/v3/kv/txn',request)
  revision=self._revision(response)
  if response.get('succeeded') is not True:raise EtcdConflict('create-only write denied')
  return revision,value
 def read(self,key):
  response=self._post('/v3/kv/range',{'key':self._b64(key),'serializable':False,'limit':'1'})
  revision=self._revision(response);kvs=response.get('kvs',[])
  if not isinstance(kvs,list) or len(kvs)!=1:raise ValueError('missing etcd value')
  kv=kvs[0]
  if base64.b64decode(kv['key'],validate=True)!=key:raise ValueError('wrong etcd key')
  return revision,base64.b64decode(kv['value'],validate=True)
