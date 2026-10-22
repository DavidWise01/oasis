"""Ne->Ac symbolic nested bracket grammar, address invariant test."""
import random
S=(('Ne',10),('Ar',18),('Kr',36),('Xe',54),('Rn',86),('Fr',87),('Ra',88),('Ac',89))
def encode(values):
    if len(values)!=89 or any(type(x) is not int or not 0<=x<=255 for x in values):
        raise ValueError('89 byte values required')
    s='{Ne['+','.join(f'{v:02x}' for v in values[:10])+']}'
    for (_,a),(name,b) in zip(S,S[1:]):
        s='{'+name+'['+s+']\\('+','.join(f'{v:02x}' for v in values[a:b])+')}'
    return s
def decode(s):
    p=0
    def take(fragment):
        nonlocal p
        if not s.startswith(fragment,p):raise ValueError('unexpected grammar')
        p+=len(fragment)
    def bytes_():
        nonlocal p
        vals=[]
        while True:
            byte=s[p:p+2]
            if len(byte)!=2 or any(ch not in '0123456789abcdef' for ch in byte):
                raise ValueError('bad byte')
            vals.append(int(byte,16));p+=2
            if s[p:p+1]==',':p+=1;continue
            return vals
    def nested(i):
        take('{'+S[i][0]+'[')
        if i==0: vals=bytes_();take(']}')
        else:
            vals=nested(i-1);take(']\\('); vals+=bytes_();take(')}')
        if len(vals)!=S[i][1]:raise ValueError('generation size')
        return vals
    result=nested(len(S)-1)
    if p!=len(s):raise ValueError('trailing content')
    return result
def test():
    rng=random.Random(89)
    for i in range(10000):
        original=[rng.randrange(256) for _ in range(89)]
        actual=decode(encode(original))
        assert actual==original,(i,'round trip')
        for _,n in S: assert actual[:n]==original[:n]
    print('PASS: 10,000 randomized 89-byte round trips; 8 ancestral prefixes')
    good=encode(list(range(89)))
    bads=[good+'?',good.replace('{Ac','{Ra',1),good.replace('{Rn','{Xe',1),good.replace(']\\(',']/( ',1),good[:-1],good.replace('58)}','5859)}')]
    for bad in bads:
        try: decode(bad)
        except ValueError: pass
        else:raise AssertionError('Malformed grammar accepted')
    print('PASS: 6 malformed strings rejected')
    modified=good.replace('00,01','ff,01',1)
    assert decode(modified)!=list(range(89))
    print('NOTE: valid byte edits are decodable; no authenticity guaranteed')
    print('RESULT: PASS (symbolic cipher only)')
if __name__=='__main__':test()
