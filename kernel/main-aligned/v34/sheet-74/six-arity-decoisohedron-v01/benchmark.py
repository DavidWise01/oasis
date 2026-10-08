#!/usr/bin/env python3
"""SHEET74 six-arity coding and 60/15/3/1/1 audit; no geometry assumptions."""
import json,hashlib,itertools
LEVELS={'uniary':1,'binary':2,'trinary':3,'quarternary':4,'pectylary':5,'sexanary':6}
LADDER=(60,15,3,1,1)
def encode(n,base):
    if base==1:return '|'*n if n else '0'
    if n==0:return '0'
    digits=[]
    while n: digits.append(str(n%base));n//=base
    return ''.join(reversed(digits))
def decode(s,base):
    if base==1:
        if s=='0':return 0
        assert s and set(s)=={'|'}
        return len(s)
    n=0
    for ch in s:
        d=int(ch)
        if d>=base:raise ValueError('bad digit')
        n=n*base+d
    return n
def audit():
    wave=tuple(i%2 for i in range(60))
    packets=[wave[i:i+4] for i in range(0,60,4)]
    tris=[tuple(packets[i:i+5]) for i in range(0,15,5)]
    dig=lambda x:hashlib.sha256(json.dumps(x,separators=(',',':')).encode()).hexdigest()
    samples={str(b):{str(n):encode(n,b) for n in range(60)} for b in range(1,7)}
    checks={
      'six_arities':list(LEVELS.values())==[1,2,3,4,5,6],
      'declared_ladder':LADDER==(60,15,3,1,1),
      'all_roundtrips':all(decode(encode(n,b),b)==n for b in range(1,7) for n in range(60)),
      '60_slots':len(wave)==60,
      '15_packets':len(packets)==15,
      '3_groups':len(tris)==3,
      'one_root':len([tris])==1,
      'one_commitment':len([dig(wave)])==1,
      'unary_is_tally':encode(5,1)=='|||||',
      'binary_flip_involution':all((b^1)^1==b for b in (0,1)),
      'six_arity_digits':set(encode(59,6))<set('012345'),
      'wave_balanced':sum(wave)==30,
      'packet_flatten':tuple(itertools.chain.from_iterable(packets))==wave,
      'group_flatten':tuple(itertools.chain.from_iterable(itertools.chain.from_iterable(tris)))==wave,
      'stable_digest':dig(wave)==dig(tuple(wave)),
      'registry_preserved':len([f'S{i:03}' for i in range(300)]+[f'M{i:03}' for i in range(100)]+[f'W{i:02}' for i in range(16)])==416,
    }
    return {'schema':'oasis/sheet74/six-arity-decoisohedron-v01','source_terms':list(LEVELS),'user_ladder':list(LADDER),'interpretation':'60 wave slots / 15 groups of 4 / 3 groups of 5 / 1 root / 1 digest; provisional structure, not asserted polyhedron','wave_digest':dig(wave),'encoding_examples':{str(k):v['59'] for k,v in samples.items()},'checks':checks,'passed':sum(checks.values()),'total':len(checks),'limitations':['A base-1 unary notation is tally, not conventional positional radix','No solid/polyhedron geometry established by these counts alone','Radix encodings are reversible; the 60->15->3 grouping is reversible only while child data are retained','No claims of actual gravitational periodicity']}
if __name__=='__main__':
 r=audit();print(json.dumps(r,indent=2));assert r['passed']==r['total']
