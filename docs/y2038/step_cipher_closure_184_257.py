"""Explicit symbolic structural closure comparison: 184 vs 257."""
from dataclasses import dataclass
@dataclass(frozen=True)
class Result:
    size:int
    complete_pairs:bool
    root_plus_triads:bool
    root_plus_binary_tree:bool
def classify(n):
    if n<=0:raise ValueError('positive address count required')
    return Result(n,n%2==0,(n-1)%3==0,n>1 and ((n-1)&(n-2))==0)
def test():
    a,b=classify(184),classify(257)
    assert (a.complete_pairs,a.root_plus_triads,a.root_plus_binary_tree)==(True,True,False)
    assert (b.complete_pairs,b.root_plus_triads,b.root_plus_binary_tree)==(False,False,True)
    assert 184==92*2==1+61*3
    assert 257==1+2**8
    for n in range(1,1001):
        x=classify(n)
        assert x.complete_pairs==(n%2==0)
        assert x.root_plus_triads==((n-1)%3==0)
        assert x.root_plus_binary_tree==(n>1 and (n-1)&(n-2)==0)
    print('PASS 1000 predicate checks')
    print(a);print(b)
    print('LIMIT: mathematical tests of user-defined closure criteria, not physics')
if __name__=='__main__':test()
