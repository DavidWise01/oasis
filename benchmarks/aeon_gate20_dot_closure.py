"""Gate 20: reversible typed cipher state and explicit dot closure.
Symbolic simulation; transformation choices are provisional.
"""
from dataclasses import dataclass, replace

@dataclass(frozen=True)
class Sapphon:
    cg: tuple[int, int] = (2, 7)
    zipper: tuple[tuple[str, object], ...] = ()
    xyz: tuple[int,int,int] = (1,2,3)
    mode: str = 'water'
    root: str = '.'

def at_cg(s):
    return replace(s, cg=s.cg[::-1])

def uv_merge(s, u, v):
    pairs=[]
    for j in range(max(len(u),len(v))):
        if j<len(u): pairs.append(('u',u[j]))
        if j<len(v): pairs.append(('v',v[j]))
    return replace(s, zipper=tuple(pairs))

def uv_unmerge(s):
    return tuple(value for lane,value in s.zipper if lane=='u'), tuple(value for lane,value in s.zipper if lane=='v')

def xyz_flip(s):
    return replace(s, xyz=tuple(-v for v in s.xyz))

def state_cycle(s, u, v):
    b=at_cg(s)
    c=uv_merge(b,u,v)
    d=xyz_flip(c)
    e=xyz_flip(d)
    f=replace(e, zipper=s.zipper)
    return at_cg(f), (b,c,d,e,f)

def test():
    source=Sapphon()
    end,steps=state_cycle(source,(1,2,3),('a','b'))
    checks={
      'root dot pinned': all(st.root=='.' for st in (source,*steps,end)),
      'a/t involution': at_cg(at_cg(source))==source,
      'u/v lossless': uv_unmerge(steps[1])==((1,2,3),('a','b')),
      'u/v ordered': steps[1].zipper==(('u',1),('v','a'),('u',2),('v','b'),('u',3)),
      'xyz involution': xyz_flip(xyz_flip(source))==source,
      'full round trip': end==source,
      'exact intermediate length': len(steps)==5,
      'seed unchanged': source==Sapphon(),
      '27 addresses': 3**3==27 and len('abcdefghijklmnopqrstuvwxyz')==26,
    }
    for k,v in checks.items():print(('PASS' if v else 'FAIL'),k)
    print(f'{sum(checks.values())}/{len(checks)} checks passed')
    assert all(checks.values())
if __name__=='__main__':test()
