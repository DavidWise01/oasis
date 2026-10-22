"""Lossless Ne->Rn nested bracket cipher, symbolic and not physical."""
import random,re
STAGES=[('Ne',10),('Ar',18),('Kr',36),('Xe',54),('Rn',86)]
class ParseError(ValueError):pass
def encode(vals):
    if len(vals)!=86 or any(type(x)!=int or not 0<=x<=255 for x in vals):raise ValueError('86 bytes required')
    out='{Ne['+','.join(f'{x:02x}' for x in vals[:10])+']}'
    for (_,n),(name,m) in zip(STAGES,STAGES[1:]):
        out='{'+name+'['+out+']\\('+','.join(f'{x:02x}' for x in vals[n:m])+')}'
    return out
def decode(s):
    pos=0
    def expect(token):
        nonlocal pos
        if not s.startswith(token,pos):raise ParseError('expected '+token+' at '+str(pos))
        pos+=len(token)
    def byte_list():
        nonlocal pos
        vals=[]
        while True:
            if pos+2>len(s) or not re.fullmatch('[0-9a-f]{2}',s[pos:pos+2]):raise ParseError('byte expected')
            vals.append(int(s[pos:pos+2],16));pos+=2
            if pos<len(s) and s[pos]==',':pos+=1;continue
            return vals
    def node(depth):
        expect('{');expect(STAGES[depth][0]);expect('[')
        if depth==0:
            vals=byte_list();expect(']');expect('}')
        else:
            vals=node(depth-1);expect(']');expect('\\(')
            ext=byte_list();expect(')');expect('}')
            if len(ext)!=STAGES[depth][1]-STAGES[depth-1][1]:raise ParseError('extension count')
            vals+=ext
        if len(vals)!=STAGES[depth][1]:raise ParseError('stage count')
        return vals
    vals=node(4)
    if pos!=len(s):raise ParseError('trailing text')
    return vals
def test():
    rng=random.Random(86)
    for _ in range(10000):
        vals=[rng.randrange(256) for _ in range(86)]
        assert decode(encode(vals))==vals
        for _,n in STAGES:assert decode(encode(vals))[:n]==vals[:n]
    print('PASS 10000 86-byte exact round trips and ancestry prefixes')
    original=encode(list(range(86)))
    bad=[original.replace('\\(','/(',1),original.replace('{Rn','{Xe',1),original+'!',original.replace('}',')',1),original.replace('00','0g',1)]
    for item in bad:
        try:decode(item)
        except ParseError:pass
        else:raise AssertionError('malformed structure accepted')
    print('PASS 5 malformed structures rejected')
if __name__=='__main__':test()
