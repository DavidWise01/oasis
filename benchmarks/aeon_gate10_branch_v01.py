"""AEON Gate10: deterministic branching lineage. Symbolic root, not biological ancestry."""
from dataclasses import dataclass
ANCHOR="TUT_SYMBOLIC_PLUS"
@dataclass(frozen=True)
class Cell:
    id:int
    parent:int|None
    generation:int
    role:str
    anchor:str
def run(max_generations=4):
    assert max_generations>=1
    cells={1:Cell(1,None,0,"seed",ANCHOR)}
    events=[(0,1,"birth")]
    current=[1];dead=set();next_id=2
    for gen in range(1,max_generations+1):
        upcoming=[]
        for parent in current:
            for role in ("repair","specialized"):
                kid=Cell(next_id,parent,gen,role,ANCHOR)
                cells[next_id]=kid
                events.append((gen,next_id,"birth"))
                events.append((gen,next_id,"differentiate:"+role))
                if role=="repair":events.append((gen,next_id,"repair_audit"))
                upcoming.append(next_id);next_id+=1
            dead.add(parent)
            events.append((gen,parent,"death"))
            events.append((gen,parent,"recycle_material"))
        current=upcoming
    assert len(cells)==2**(max_generations+1)-1
    assert len(current)==2**max_generations
    assert len(dead)==2**max_generations-1
    assert all(c.id>0 and c.anchor==ANCHOR for c in cells.values())
    assert all(c.parent is None or (c.parent in cells and cells[c.parent].generation==c.generation-1) for c in cells.values())
    assert sum(x[2]=="birth" for x in events)==len(cells)
    assert sum(x[2]=="recycle_material" for x in events)==len(dead)
    assert all(i not in dead for i in current)
    assert events==sorted(events,key=lambda x:x[0])
    a,b=1,1
    for _ in range(90):a,b=b,a+b
    for _ in range(90):a,b=b-a,a
    assert (a,b)==(1,1)
    print(f"PASS Gate10: {len(cells)} cell records, {len(current)} living leaves, {len(dead)} terminated, {len(events)} events")
    for gen in range(max_generations+1):
        print(f"generation {gen}: {sum(c.generation==gen for c in cells.values())}")
    return cells,events
if __name__=="__main__":run()
