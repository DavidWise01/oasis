"""Symbolic Ne-to-257 nested register cipher. No chemical element-257 claim."""
import random,re
STAGES=(('Ne',10),('Ar',18),('Kr',36),('Xe',54),('Rn',86),('Fr',87),('Ra',88),('Ac',89),('Th',90),('Z257',257))
def encode(values):
    if len(values)!=257 or any(type(v)!=int or not 0<=v<=255 for v in values):raise ValueError('257 bytes required')
    s='{Ne['+','.join(f'{v:02x}' for v in values[:10])+']}'
    for (_,n),(name,m) in zip(STAGES,STAGES[1:]):
        s='{'+name+'['+s+']\\('+','.join(f'{v:02x}' for v in values[n:m])+')}'
    return s
def decode(s):
    pos=0
    def take(token):
        nonlocal pos
        if not s.startswith(token,pos):raise ValueError('expected '+token)
        pos+=len(token)
    def segment():
        nonlocal pos
        start=pos
        while pos<len(s) and s[pos] in '0123456789abcdef,':pos+=1
        raw=s[start:pos]
        if re.fullmatch(r'[0-9a-f]{2}(,[0-9a-f]{2})*',raw) is None:raise ValueError('bad byte segment')
        return bytes(int(v,16) for v in raw.split(','))
    def node(i):
        take('{'+STAGES[i][0]+'[')
        if i==0:v=segment();take(']}')
        else:v=node(i-1);take(']\\(');v+=segment();take(')}')
        if len(v)!=STAGES[i][1]:raise ValueError('stage length')
        return v
    v=node(len(STAGES)-1)
    if pos!=len(s):raise ValueError('trailing input')
    return v
def test():
    r=random.Random(257)
    for _ in range(10000):
        data=bytes(r.randrange(256) for _ in range(257))
        output=decode(encode(data))
        assert output==data
        for _,n in STAGES:assert output[:n]==data[:n]
    print('PASS 10000 randomized 257-byte round trips and ten ancestral prefixes')
    original=encode(bytes(i%256 for i in range(257)))
    bad=[original+'x',original[:-1],original.replace('{Z257','{Th',1),original.replace('{Ne','{Xe',1),original.replace(']\\(',']/( ',1),original.replace('00,01','0g,01',1)]
    for item in bad:
        try:decode(item)
        except ValueError:pass
        else:raise AssertionError('malformed accepted')
    print('PASS six malformed structures rejected')
    assert decode(original.replace('00,01','ff,01',1))!=decode(original)
    print('NOTE: valid data mutation is not authenticated')
if __name__=='__main__':test()
