import itertools,math,json
from pathlib import Path
phases=[(s,o,15*(s*8+o)) for s in range(3) for o in range(8)]
assert len(phases)==len(set(phases))==24
vertices=list(itertools.product((-1,1),repeat=4))
edges=[(a,b) for i,a in enumerate(vertices) for b in vertices[i+1:] if sum(x!=y for x,y in zip(a,b))==1]
faces=[(axes,sign) for axes in itertools.combinations(range(4),2) for sign in itertools.product((-1,1),repeat=2)]
assert (len(vertices),len(edges),len(faces))==(16,32,24)
mapping=dict(zip(range(24),faces))
inverse={f:i for i,f in mapping.items()}
assert all(inverse[mapping[i]]==i for i in range(24))
inner_cube=list(itertools.product((-1,1),repeat=3))
assert len(inner_cube)==8
R,r=2,.5
torus=[((R+r*math.cos(v))*math.cos(u),(R+r*math.cos(v))*math.sin(u),r*math.sin(v)) for u in [i*math.pi/12 for i in range(24)] for v in [j*math.pi/4 for j in range(8)]]
assert len(torus)==192 and all(math.hypot(x,y)>=R-r-1e-12 for x,y,z in torus)
print(json.dumps(dict(status="PASS",phases=24,tesseract_faces=24,vertices=16,edges=32,cubic_cells=8,core_cube_vertices=8,toroid_samples=192,geometry="symbolic mapping only"),indent=2))
