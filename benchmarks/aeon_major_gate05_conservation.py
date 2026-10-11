"""Major Gate 5: exact quantity conservation vs information preservation.
Symbolic rationals, not experimental energy conservation.
"""
from fractions import Fraction as Q

def split(q, weight):
    if not Q(0) <= weight <= Q(1):
        raise ValueError('weight outside [0,1]')
    return (q * weight, q * (1-weight))

def merge(pair):
    return sum(pair, Q(0))

def run():
    tests={}
    q=Q(3,4)
    b3=split(q,Q(1,3)); b2=split(q,Q(1,2))
    tests['/3 paired complement conserves']=merge(b3)==q
    tests['/2 paired complement conserves']=merge(b2)==q
    tests['two alternative experiments are not simultaneous']=merge(b3)+merge(b2)==2*q
    tests['unbalanced simultaneous outputs fail']=Q(1,4)+Q(3,8)!=q
    tests['same source with supplied complementary weights']=merge((Q(1,4),Q(1,2)))==q
    tests['zero and negative quantities supported']=all(merge(split(v,Q(1,3)))==v for v in (Q(0),Q(-7,5),Q(100,13)))
    tests['branch order changes ledger not total']=merge(b3)==merge(b3[::-1])
    ledger=(('origin',q),('split /3',b3),('merge',merge(b3)))
    tests['ledger retains provenance']=ledger[0][1]==q and ledger[1][1]==b3 and ledger[2][1]==q
    tests['single output cannot identify split']=merge((Q(1,4),Q(1,2)))==merge((Q(3,8),Q(3,8)))
    tests['reject invalid weights']=False
    try:split(q,Q(5,4))
    except ValueError:tests['reject invalid weights']=True
    for k,v in tests.items():print(('PASS' if v else 'FAIL'), k)
    print('RESULT',sum(tests.values()),'/',len(tests))
    print('Original paired outputs sum to 5/8 rather than 3/4.')
    assert all(tests.values())
if __name__=='__main__':run()
