"""Symbolic Ne->Fr nested chemical cipher; not a physical electron model."""
import random,re
STAGES=[('Ne',10),('Ar',18),('Kr',36),('Xe',54),('Rn',86),('Fr',87)]
def encode(v):
    if len(v)!=87 or any(type(x)!=int or x<0 or x>255 for x in v):raise ValueError('87 bytes')
    s='{Ne['+','.join(f'{x:02x}' for x in v[:10])+']}'
    for (_,a),(name,b) in zip(STAGES,STAGES[1:]):
        s='{'+name+'['+s+']\\('+','.join(f'{x:02x}' for x in v[a:b])+')}'
    return s
def decode(s):
    pos=0
    def expect(v):
        nonlocal pos
        if not s.startswith(v,pos):raise ValueError('expected '+v)
        pos+=len(v)
    def values():
        nonlocal pos
        start=pos
        while pos<len(s) and s[pos] in '0123456789abcdef,':pos+=1
        chunk=s[start:pos]
        if not re.fullmatch(r'[0-9a-f]{2}(,[0-9a-f]{2})*',chunk):raise ValueError('malformed byte list')
        return [int(x,16) for x in chunk.split(',')]
    def node(i):
        expect('{'+STAGES[i][0]+'[')
        if i==0:
            out=values();expect(']}')
        else:
            out=node(i-1);expect(']\\(');out+=values();expect(')}')
        if len(out)!=STAGES[i][1]:raise ValueError('wrong length')
        return out
    out=node(5)
    if pos!=len(s):raise ValueError('trailing content')
    return out
def test():
    rng=random.Random(87)
    for _ in range(10000):
        x=[rng.randrange(256) for _ in range(87)]
        y=decode(encode(x))
        assert y==x
        for _,n in STAGES:assert y[:n]==x[:n]
    print('PASS: 10000 random 87-byte exact round trips; all ancestral prefixes retained')
    v=encode(list(range(87)))
    malformed=[v+'x',v.replace('{Fr','{Rn',1),v.replace(']\\(',']/( ',1),v.replace('56)}','fff)}'),v.replace('{Ne','{Xe',1)]
    for corrupt in malformed:
        try:decode(corrupt)
        except ValueError:pass
        else:raise AssertionError('accepted malformed structure')
    print('PASS: five malformed structures rejected')
    print('NOTE: valid-byte tampering is not detectable without integrity protection')
if __name__=='__main__':test()
