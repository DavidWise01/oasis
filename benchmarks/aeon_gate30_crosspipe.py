"""Gate 30: X is simultaneously a coordinate crossing and a reversible route.
Symbolic Euclidean model; not a physical spacetime gateway.
"""
import math
ADDRESS=('000','00','11','24','42','11','00','000')
PIVOT=(0.0,0.0)
SWAP={'24':'42','42':'24'}
def invert_address(a):
    return tuple(SWAP.get(x,x) for x in reversed(a))
def rotate(p,degrees):
    a=math.radians(degrees);x,y=p
    return (x*math.cos(a)-y*math.sin(a),x*math.sin(a)+y*math.cos(a))
def close(a,b,tol=1e-12):
    return all(abs(x-y)<tol for x,y in zip(a,b))
def route(source,fold=False):
    return SWAP.get(source,source) if fold else source
def run():
    x=(1.,1.);corners=[x,(-1.,1.),(-1.,-1.),(1.,-1.)];phases=[0,15,30,45,60]
    tests={
       'source address preserved':ADDRESS==('000','00','11','24','42','11','00','000'),
       'mirror involution':invert_address(invert_address(ADDRESS))==ADDRESS,
       'mirrored source invariant':invert_address(ADDRESS)==ADDRESS,
       'two distinct X route addresses':route('24')!=route('42'),
       'fold exchanges address 24':route('24',True)=='42',
       'fold exchanges address 42':route('42',True)=='24',
       'double fold restores both routes':all(route(route(r,True),True)==r for r in ('24','42')),
       'four equal 15-degree phases':all(phases[i+1]-phases[i]==15 for i in range(4)),
       'pivot fixed during every phase':all(close(rotate(PIVOT,p),PIVOT) for p in phases),
       'forward reverse restores X corners':all(close(rotate(rotate(p,60),-60),p) for p in corners),
       'radius preserved for each phase':all(math.isclose(sum(z*z for z in rotate(p,deg)),2.,abs_tol=1e-12) for p in corners for deg in phases),
       '60 degrees not full closure':not close(rotate(x,60),x),
       'six sectors make full revolution':close(rotate(x,6*60),x),
       'X intersection is origin':close(PIVOT,(0.,0.)),
    }
    for name,ok in tests.items():print(('PASS' if ok else 'FAIL'),name)
    print(f'RESULT {sum(tests.values())}/{len(tests)}')
    assert all(tests.values())
if __name__=='__main__':run()
