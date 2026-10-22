"""Symbolic chemical cipher, Ne through Th: lossless nested bracket serialization."""
import random
STAGES=(('Ne',10),('Ar',18),('Kr',36),('Xe',54),('Rn',86),('Fr',87),('Ra',88),('Ac',89),('Th',90))
def encode(values):
    if len(values)!=90 or any(type(x)!=int or not 0<=x<=255 for x in values):
        raise ValueError('exactly 90 byte values required')
    s='{Ne['+','.join(f'{x:02x}' for x in values[:10])+']}'
    for (_,left),(name,right) in zip(STAGES,STAGES[1:]):
        s='{'+name+'['+s+']\\('+','.join(f'{x:02x}' for x in values[left:right])+')}'
    return s
def decode(s):
    p=0
    def expect(fragment):
        nonlocal p
        if not s.startswith(fragment,p):raise ValueError('unexpected token at '+str(p))
        p+=len(fragment)
    def read_bytes():
        nonlocal p
        v=[]
        while True:
            pair=s[p:p+2]
            if len(pair)!=2 or any(c not in '0123456789abcdef' for c in pair):
                raise ValueError('malformed byte')
            p+=2;v.append(int(pair,16))
            if s[p:p+1]!=',':return v
            p+=1
    def stage(i):
        expect('{'+STAGES[i][0]+'[')
        if i==0:
            values=read_bytes();expect(']}')
        else:
            values=stage(i-1);expect(']\\(');values+=read_bytes();expect(')}')
        if len(values)!=STAGES[i][1]:raise ValueError('incorrect stage size')
        return values
    result=stage(len(STAGES)-1)
    if p!=len(s):raise ValueError('trailing characters')
    return result
def test():
    r=random.Random(90)
    for _ in range(10000):
        v=[r.randrange(256) for _ in range(90)]
        decoded=decode(encode(v))
        assert decoded==v
        for _,n in STAGES:assert decoded[:n]==v[:n]
    print('PASS 10000 round trips through 90 addresses and 9 prefix checks per trial')
    s=encode(list(range(90)))
    corrupt=(s+'!',s[:-1],s.replace('{Th','{Ac',1),s.replace('{Ne','{Ar',1),s.replace(']\\(',']/( ',1),s.replace('\\(59)}','\\(59,5a)}',1))
    for case in corrupt:
        try:decode(case)
        except ValueError:pass
        else:raise AssertionError('accepted malformed input')
    print('PASS 6 malformed grammar cases rejected')
    altered=s.replace('00,01','ff,01',1)
    assert decode(altered)!=list(range(90))
    print('KNOWN LIMITATION: valid-byte tampering is not detected')
if __name__=='__main__':test()
