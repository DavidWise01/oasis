"""Gate 19: typed overlay for the 26 literal signed cipher expressions.
Framework-local semantics supplied by the user; not claims about physical chemistry.
"""
from dataclasses import dataclass

CIPHER="""a+b-
-b+c
c+d
-d+e
e+f
-f+g
g+h
-h+i
i+j
-j+k
k+l
-l+m
m+n
-n+o
o+p
-p+q
q+r
-r+s
s+t
-t+s
u+v
-v+u
w+x
-x+w
y+z
-z+y""".splitlines()

@dataclass(frozen=True)
class Coord:
    x:int;y:int;z:int

def operate_at_on_cg(c:int,g:int,activate:bool=True):
    # A/T gate operates on C/G payload, not an alphabetic link.
    return (g,c) if activate else (c,g)

def zipper_merge(u:tuple,v:tuple):
    # Preserve both inputs and order, even if their lengths differ.
    output=[]
    for i in range(max(len(u),len(v))):
        if i<len(u):output.append(('u',u[i]))
        if i<len(v):output.append(('v',v[i]))
    return tuple(output)

def adapt_water_modal(current:str, mode:str):
    if mode not in ('water','modal'):raise ValueError('unknown mode')
    return (current,mode)  # provenance retained

def transform_xyz(p:Coord, flip:bool=False):
    return Coord(-p.x,-p.y,-p.z) if flip else p

def test():
    z=zipper_merge((1,2,3),('a','b'))
    checks={
        '26 unchanged source expressions':len(CIPHER)==26,
        'a/t swaps cg':operate_at_on_cg(2,7)==(7,2),
        'a/t inverse restores cg':operate_at_on_cg(*operate_at_on_cg(2,7))==(2,7),
        'zipper preserves all 5 inputs':len(z)==5,
        'zipper deterministic':z==(('u',1),('v','a'),('u',2),('v','b'),('u',3)),
        'water modal retains input':adapt_water_modal('seed','water')==('seed','water'),
        'xyz inverse self closure':transform_xyz(transform_xyz(Coord(2,-3,4),True),True)==Coord(2,-3,4),
        'xyz independent axes':transform_xyz(Coord(1,2,3),True)==Coord(-1,-2,-3),
    }
    for label,passed in checks.items():print('PASS' if passed else 'FAIL',label)
    assert all(checks.values())
    print(f'{len(checks)}/{len(checks)} passed')
if __name__=='__main__':test()
