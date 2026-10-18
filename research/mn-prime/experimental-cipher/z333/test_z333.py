"""Z333 signed checkpoint witness regression. Symbolic research only."""
import json, hashlib, math
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.exceptions import InvalidSignature
LIMIT=math.factorial(24)
def canon(x):return json.dumps(x,sort_keys=True,separators=(',',':')).encode()
def h(x):return hashlib.sha256(canon(x)).hexdigest()
def chain(indices):
 out=[];prev='GENESIS'
 for seq,index in enumerate(indices):
  if type(index)!=int or not 0<=index<LIMIT:raise ValueError('index')
  e={'seq':seq,'index':str(index),'prev':prev};e['hash']=h(e);out.append(e);prev=e['hash']
 return out
def valid(rows):
 prev='GENESIS'
 for seq,e in enumerate(rows):
  if set(e)!={'seq','index','prev','hash'} or type(e['seq'])!=int or e['seq']!=seq or not isinstance(e['index'],str) or not e['index'].isdecimal() or not 0<=int(e['index'])<LIMIT or e['prev']!=prev or e['hash']!=h({k:e[k] for k in ('seq','index','prev')}):return False
  prev=e['hash']
 return True
def cp(rows):
 if not valid(rows):raise ValueError('invalid chain')
 return {'schema':'z333-v1','count':len(rows),'tip':rows[-1]['hash'] if rows else 'GENESIS'}
def receipt(sk,c,epoch):
 p={'checkpoint':c,'epoch':epoch};return {'payload':p,'signature':sk.sign(canon(p)).hex()}
def verify(pk,r,rows,floor=0):
 try:
  p=r['payload'];pk.verify(bytes.fromhex(r['signature']),canon(p))
  return type(p['epoch'])==int and p['epoch']>=floor and valid(rows) and cp(rows)==p['checkpoint']
 except (InvalidSignature,ValueError,TypeError,KeyError,AttributeError):return False
def run():
 sk=Ed25519PrivateKey.generate();pk=sk.public_key();wrong=Ed25519PrivateKey.generate().public_key()
 rows=chain([0,1,42,LIMIT-1,5]);c=cp(rows);r=receipt(sk,c,5)
 checks={
  'factorial':LIMIT==620448401733239439360000,
  'valid_chain':valid(rows),
  'valid_receipt':verify(pk,r,rows),
  'serialized_round_trip':verify(pk,json.loads(canon(r)),json.loads(canon(rows))),
  'signature_64_bytes':len(bytes.fromhex(r['signature']))==64,
  'wrong_key':not verify(wrong,r,rows),
  'bad_signature':not verify(pk,{**r,'signature':'00'*64},rows),
  'bad_count':not verify(pk,receipt(sk,{**c,'count':4},5),rows),
  'bad_tip':not verify(pk,receipt(sk,{**c,'tip':'0'*64},5),rows),
  'truncated':not verify(pk,r,rows[:-1]),
  'extended':not verify(pk,r,chain([0,1,42,LIMIT-1,5,6])),
  'reordered':not verify(pk,r,[rows[1],rows[0]]+rows[2:]),
  'edited_index':not verify(pk,r,[{**rows[0],'index':'6'}]+rows[1:]),
  'edited_hash':not verify(pk,r,[{**rows[0],'hash':'0'*64}]+rows[1:]),
  'floor_accept':verify(pk,r,rows,5),
  'floor_reject':not verify(pk,r,rows,6),
  'old_epoch':not verify(pk,receipt(sk,c,4),rows,5),
  'empty_chain':verify(pk,receipt(sk,cp([]),0),[]),
  'out_of_range':False,
  'distinct_registers':(5,3,1)!=(3,1,2)
 }
 try:chain([LIMIT])
 except ValueError:checks['out_of_range']=True
 for name,ok in checks.items():print(('PASS' if ok else 'FAIL'),name)
 print(f'{sum(checks.values())}/{len(checks)} PASS')
 assert all(checks.values())
if __name__=='__main__':run()
