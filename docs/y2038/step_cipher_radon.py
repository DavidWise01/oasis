"""Lossless symbolic noble-gas zipper Neon to Radon."""
import random
STAGES=(('Ne',10),('Ar',18),('Kr',36),('Xe',54),('Rn',86))
def cross(a,b):
    b=tuple(reversed(b)); out=[]
    for i in range(max(len(a),len(b))):
        if i<len(a):out.append(a[i])
        if i<len(b):out.append(b[i])
    return tuple(out)
def unweave(z,na,nb):
    a=[];b=[];j=0
    for i in range(max(na,nb)):
        if i<na:a.append(z[j]);j+=1
        if i<nb:b.append(z[j]);j+=1
    if j!=len(z):raise ValueError('length mismatch')
    return tuple(a),tuple(reversed(b))
def test():
    lengths=[10,18,36,54,86]
    assert [b-a for a,b in zip(lengths,lengths[1:])]==[8,18,18,32]
    print('PASS four noble-gas extensions')
    rng=random.Random(2038)
    for _ in range(10000):
        values=tuple(rng.randrange(256) for _ in range(86))
        for n,m in zip(lengths,lengths[1:]):
            a,b=values[:n],values[n:m]
            assert unweave(cross(a,b),len(a),len(b))==(a,b)
            assert a+b==values[:m]
    print('PASS 10000 randomized byte round trips for each transition')
    data=tuple(range(1,87))
    assert all(data[:n]==tuple(range(1,n+1)) for n in reversed(lengths))
    print('PASS Radon to Xenon to Krypton to Argon to Neon ancestry')
    try:unweave(cross(data[:54],data[54:])[:-1],54,32)
    except (ValueError,IndexError):print('PASS malformed crossing rejected')
    else:raise AssertionError('corrupt crossing accepted')
    print('RESULT 4/4 PASS')
if __name__=='__main__':test()
