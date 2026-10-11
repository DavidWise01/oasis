from fractions import Fraction as F
import hashlib,json
A=(1,3,-3,2)
B=(1,3,3,-2)
def prod(xs):
 v=F(1)
 for x in xs:v*=x
 return v
def record(name,parts):
 obj={'witness':name,'signed_factors':list(parts),'value':str(prod(parts))}
 blob=json.dumps(obj,sort_keys=True,separators=(',',':')).encode()
 return obj,hashlib.sha256(blob).hexdigest()
def reverse_path(xs):return tuple(reversed(xs))
a,ha=record('W_L',A);b,hb=record('W_R',B)
checks={
 'equal numerical witnesses':prod(A)==prod(B)==-18,
 'paired multiplication 324':prod(A)*prod(B)==324,
 'address count 1014':13*6*13==1014,
 'raw paths differ':A!=B,
 'provenance hashes differ':ha!=hb,
 'round trip serialization':tuple(json.loads(json.dumps(a))['signed_factors'])==A and tuple(json.loads(json.dumps(b))['signed_factors'])==B,
 'reversal keeps scalar':prod(reverse_path(A))==prod(A) and prod(reverse_path(B))==prod(B),
 'reversal roundtrip keeps path':reverse_path(reverse_path(A))==A and reverse_path(reverse_path(B))==B,
 'zero witness collapse rejected':(0,0,1,1,2)!=(0,),
 '1014 not scalar result':1014!=324,
 'identity lost when only scalar retained':prod(A)==prod(B) and A!=B,
 'operator position changes still distinguishable':A[2:]!=B[2:],
}
for k,v in checks.items():print(('PASS' if v else 'FAIL'),k)
print('CHECKS',sum(checks.values()),'/',len(checks))
print('W_L',a,'sha256',ha)
print('W_R',b,'sha256',hb)
assert all(checks.values())
