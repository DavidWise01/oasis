"""KET five-layer hanging-dot propagation: reproducible symbolic test."""
from collections import deque
import csv
from pathlib import Path
LAYERS=[5,4,3,2,1]
DOT_STATES=2**3*(3*3)**3
BITS="stuvwxyz"
nodes=[(layer,pos) for layer,n in enumerate(LAYERS) for pos in range(n)]
parents={(layer,pos):(layer+1,min(LAYERS[layer+1]-1,pos*LAYERS[layer+1]//n)) for layer,n in enumerate(LAYERS[:-1]) for pos in range(n)}
children={node:[] for node in nodes}
for child,parent in parents.items():children[parent].append(child)
root=(4,0);depth={root:0};queue=deque([root])
while queue:
    for child in children[queue[0]]:
        assert child not in depth
        depth[child]=depth[queue[0]]+1
        queue.append(child)
    queue.popleft()
assert len(nodes)==15 and len(parents)==14 and len(depth)==15
assert DOT_STATES==5832 and len(BITS)==8
def encode(value):
    assert 0<=value<256
    selector=value%8
    nested=(value//8)%729
    return selector,nested,selector*729+nested
rows=[]
for value in range(256):
    selector,nested,address=encode(value)
    for layer,pos in nodes:rows.append((value,f"{value:08b}",layer+1,pos+1,depth[(layer,pos)],0,selector,nested,address))
assert len(rows)==3840 and max(r[4] for r in rows)==4
assert all(r[-1]<DOT_STATES for r in rows)
dest=Path(__file__).with_name("five_layer_results.csv")
with dest.open("w",newline="") as file:
    writer=csv.writer(file)
    writer.writerow(["choice","stuvwxyz","layer","dot","hop_arrival","shared_state_arrival","selector8","nested729","address"])
    writer.writerows(rows)
print("PASS: 15 nodes, 14 links, 5832 states/dot; all 256 root choices; 0..4 hop depths")
print("CAUTION: shared reads at zero modeled hops are not instantaneous physical signals or quantum entanglement.")
