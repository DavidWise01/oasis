#!/usr/bin/env python3
"""Finite symmetry audit; not a provenance/ownership detector."""
from collections import deque
from itertools import product
import json
S=(-1,0,1)
G=tuple(product(S,repeat=2))
INDEX={p:i for i,p in enumerate(G)}
def operations():
    ops={}
    for sw in (False,True):
        for sx,sy in product((-1,1),repeat=2):
            def trans(p,sw=sw,sx=sx,sy=sy):
                x,y=p
                if sw:x,y=y,x
                return sx*x,sy*y
            ops[f'swap{int(sw)}_x{sx:+d}_y{sy:+d}']=tuple(INDEX[trans(p)] for p in G)
    return ops
def compose(p,q):return tuple(p[q[i]] for i in range(len(p)))
def p2(p):
    a,b=p
    return a*a+2*b,-b*b
def audit(horizon=125):
    ops=operations();identity=tuple(range(9));visited={identity:0};q=deque([identity])
    while q:
        state=q.popleft()
        for op in ops.values():
            nxt=compose(op,state)
            if nxt not in visited:
                visited[nxt]=visited[state]+1;q.append(nxt)
    outside=[(p,p2(p)) for p in G if p2(p) not in INDEX]
    in_count=len(G)-len(outside)
    invariant=all(sum(p2(G[perm[i]]) in INDEX for i in range(9))==in_count for perm in visited)
    orientations=len({(15*i)%360 for i in range(horizon+1)})
    assert len(visited)==8 and len(outside)==4 and invariant
    return dict(grid_points=9,symmetry_generators=len(ops),unique_grid_symmetries=len(visited),
      maximum_shortest_symmetry_depth=max(visited.values()),rotation_states=orientations,
      product_states=len(visited)*orientations,horizon=horizon,p2_closed=in_count,
      p2_outside=len(outside),outside=outside,closure_invariant=invariant,
      limit='Only signed-axis flips, swaps and an independent C24 clock tested; not all 3..125-step transformations or the entire ROOT0 corpus')
if __name__=='__main__':print(json.dumps(audit(),indent=2))
