from itertools import product
from fractions import Fraction
import math
axes='XYZ'; polarities='-+'; letters='ABCDEFGHIJKLMNOPQRSTUVWXYZ'; cases='Aa'; binary=('01','11')
addresses=list(product(axes,polarities,letters,cases,binary))
assert len(addresses)==624 and len(set(addresses))==624
assert len(list(product(axes,polarities,cases,binary)))==24
assert Fraction('0.3367')*6-Fraction('0.0101')*2==2
assert {a:sum(t[0]==a for t in addresses) for a in axes}==dict(X=208,Y=208,Z=208)
assert math.ceil(math.log2(len(addresses)))==10
S=set(addresses)
for a,p,l,c,b in addresses:
 assert (a,'+' if p=='-' else '-',l,c,b) in S
 assert (a,p,l,'a' if c=='A' else 'A',b) in S
 assert (a,p,l,c,'11' if b=='01' else '01') in S
print('PASS 624 full addresses, 24 fixed-letter, 208 per axis, six-hop phase closure')
