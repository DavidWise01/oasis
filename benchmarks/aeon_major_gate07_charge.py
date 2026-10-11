"""Major Gate 7: exact signed-charge conservation of symbolic crosspipe.
Not a derivation of Maxwell's equations or experimental electromagnetism.
"""
from fractions import Fraction as Q

def split(charge, fraction):
    return charge*fraction, charge*(1-fraction)

def crosspipe(pair):
    return pair[::-1]

def total(pair):
    return sum(pair, Q(0))

def test():
    charges=(Q(1),Q(-1),Q(0),Q(3,4))
    weights=(Q(0),Q(1,3),Q(1,2),Q(1))
    cases=[(q,w,split(q,w)) for q in charges for w in weights]
    tests={
        '16 exact split scenarios':len(cases)==16,
        'source equals daughter charge sum':all(total(p)==q for q,w,p in cases),
        'crosspipe conserves charge':all(total(crosspipe(p))==q for q,w,p in cases),
        'double crossing restores routes':all(crosspipe(crosspipe(p))==p for q,w,p in cases),
        'recombination conserves signed charge':all(total(crosspipe(p))==q for q,w,p in cases),
        'opposite charges cancel':total((Q(1),Q(-1)))==0,
        'neutral source stays neutral':all(total(p)==0 for q,w,p in cases if q==0),
        'negative charge retained':all(total(p)==-1 for q,w,p in cases if q==-1),
        'fault injection detected':total((Q(1,4),Q(3,8)))!=Q(3,4),
        'fractions avoid rounding':split(Q(3,4),Q(1,3))==(Q(1,4),Q(1,2)),
        'crossing does not imply charge creation':total(crosspipe((Q(2),Q(-3))))==Q(-1),
        'charge and route identity distinct':crosspipe((Q(1,4),Q(1,2)))!=(Q(1,4),Q(1,2)),
    }
    for name,passed in tests.items():print(('PASS' if passed else 'FAIL'),name)
    print(f'RESULT {sum(tests.values())}/{len(tests)}')
    assert all(tests.values())

if __name__=='__main__':test()
