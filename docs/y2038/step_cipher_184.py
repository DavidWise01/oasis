"""Symbolic 184-position nested cipher invariant; not a physical element model."""
import random,re
STAGES=(('Ne',10),('Ar',18),('Kr',36),('Xe',54),('Rn',86),('Fr',87),('Ra',88),('Ac',89),('Th',90),('Z184',184))
def encode(v):
    if len(v)!=184 or any(type(x)!=int or not 0<=x<=255 for x in v):raise ValueError('184 byte values required')
    s='{Ne['+','.join(f'{x:02x}' for x in v[:10])+']}'
    for (_,a),(name,b) in zip(STAGES,STAGES[1:]):
        s='{'+name+'['+s+']\\('+','.join(f'{x:02x}' for x in v[a:b])+')}'
    return s
def decode(s):
    p=0
    def take(t):
        nonlocal p
        if not s.startswith(t,p):raise ValueError('unexpected token')
        p+=len(t)
    def segment():
        nonlocal p
        start=p
        while p<len(s) and s[p] in '0123456789abcdef,':p+=1
        raw=s[start:p]
        if re.fullmatch(r'[0-9a-f]{2}(,[0-9a-f]{2})*',raw) is None:raise ValueError('bad segment')
        return bytes(int(x,16) for x in raw.split(','))
    def node(i):
        take('{'+STAGES[i][0]+'[')
        if i==0:v=segment();take(']}')
        else:v=node(i-1);take(']\\(');v+=segment();take(')}')
        if len(v)!=STAGES[i][1]:raise ValueError('stage length')
        return v
    v=node(len(STAGES)-1)
    if p!=len(s):raise ValueError('trailing data')
    return v
def test():
    rng=random.Random(184)
    for _ in range(10000):
        original=bytes(rng.randrange(256) for _ in range(184))
        restored=decode(encode(original))
        assert restored==original
        for _,n in STAGES:assert restored[:n]==original[:n]
    print('PASS 10000 randomized round trips, all 10 ancestral checkpoints')
    sample=encode(bytes(range(184)))
    malformed=[sample+'!',sample[:-1],sample.replace('{Z184','{Z257',1),sample.replace('{Ne','{Ar',1),sample.replace(']\\(',']/( ',1),sample.replace('00,01','0g,01',1)]
    for bad in malformed:
        try:decode(bad)
        except ValueError:pass
        else:raise AssertionError('malformed input accepted')
    print('PASS six malformed inputs rejected')
    assert decode(sample.replace('00,01','ff,01',1))!=decode(sample)
    print('LIMITATION valid-byte tampering not authenticated')
if __name__=='__main__':test()
