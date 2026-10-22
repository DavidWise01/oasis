"""Ne->Ra symbolic nested cipher. Run with Python 3."""
import random
S=[("Ne",10),("Ar",18),("Kr",36),("Xe",54),("Rn",86),("Fr",87),("Ra",88)]
def encode(v):
    if len(v)!=88 or any(type(x)!=int or not 0<=x<=255 for x in v):raise ValueError("88 bytes")
    s="{Ne["+",".join(f"{x:02x}" for x in v[:10])+"]}"
    for (_,a),(name,b) in zip(S,S[1:]):
        s="{"+name+"["+s+"]\\("+",".join(f"{x:02x}" for x in v[a:b])+")}"
    return s
def decode(s):
    p=0
    def take(t):
        nonlocal p
        if not s.startswith(t,p):raise ValueError("expected "+t)
        p+=len(t)
    def part():
        nonlocal p
        a=[]
        while True:
            b=s[p:p+2]
            if len(b)!=2 or any(c not in "0123456789abcdef" for c in b):raise ValueError("bad byte")
            a.append(int(b,16));p+=2
            if s[p:p+1]==",":p+=1;continue
            return a
    def node(i):
        take("{"+S[i][0]+"[")
        if i==0:v=part();take("]}")
        else:v=node(i-1);take("]\\(");v+=part();take(")}")
        if len(v)!=S[i][1]:raise ValueError("capacity")
        return v
    v=node(6)
    if p!=len(s):raise ValueError("trailing data")
    return v
def test():
    r=random.Random(88)
    for _ in range(10000):
        v=[r.randrange(256) for _ in range(88)]
        out=decode(encode(v))
        assert out==v
        for _,n in S:assert out[:n]==v[:n]
    a=encode(list(range(88)))
    for bad in [a+"x",a.replace("{Ra","{Fr",1),a.replace("]\\(","]/(",1),a.replace("{Ne","{Xe",1),a[:-1]]:
        try:decode(bad)
        except ValueError:pass
        else:raise AssertionError("malformed accepted")
    print("PASS: 10000 round trips; ancestral prefixes; 5 malformed inputs")
    print("NOTE: no cryptographic integrity or physical chemistry verification")
if __name__=="__main__":test()
