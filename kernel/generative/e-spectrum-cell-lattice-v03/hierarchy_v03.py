from dataclasses import dataclass, replace

PRIM = ("-E","-E","+E","+E","+P","+P")
FORCES = ("weak","medium","strong")
NEST_FACTOR = 16
SUBSTRATES = 3
LATTICE_CAPACITY = "99.9∞"
GRID = "x∞ × y∞ × z∞"
VIEWS = ("vector","voxel","vogel")

@dataclass(slots=True)
class Cell:
    id: int
    generation: int = 0
    t: int = -1
    g: int = 1
    occupancy_milli: int = 0
    active: bool = True
    center: tuple[int,int,int] = (0,0,0)
    tag: str = "sqrt6-homeo"
    tick_count: int = 0

def realize(c: Cell) -> Cell:
    c = replace(c, t=0)
    c = replace(c, occupancy_milli=999)
    c = replace(c, t=1)
    return c

def ready(c: Cell) -> bool:
    return (
        c.active and c.g == 1 and c.t == 1 and
        c.occupancy_milli == 999 and c.center == (0,0,0) and
        c.tag == "sqrt6-homeo"
    )

def mitosis(c: Cell):
    assert ready(c)
    return (
        Cell(id=2*c.id, generation=c.generation+1),
        Cell(id=2*c.id+1, generation=c.generation+1)
    )

def global_tick(cells):
    for c in cells:
        if c.active:
            c.tick_count += 1

def run_alignment():
    decorated = len(PRIM) * len(FORCES)
    per_substrate = decorated * NEST_FACTOR
    on_spine = per_substrate * SUBSTRATES

    parent = realize(Cell(id=0))
    assert ready(parent)
    daughters = mitosis(parent)
    assert len(daughters) == 2
    assert all(d.generation == 1 and d.t == -1 and d.g == 1 for d in daughters)

    cells = [Cell(i) for i in range(4096)]
    global_tick(cells)
    assert all(c.tick_count == 1 for c in cells)
    for _ in range(99):
        global_tick(cells)
    assert all(c.tick_count == 100 for c in cells)

    return {
        "prim": len(PRIM),
        "forces": len(FORCES),
        "decorated": decorated,
        "nest_factor": NEST_FACTOR,
        "leaves_per_substrate": per_substrate,
        "leaves_on_spine": on_spine,
        "cell": "sqrt6-homeo",
        "lattice": LATTICE_CAPACITY,
        "grid": GRID,
        "views": VIEWS,
        "global_tick_cells_checked": len(cells),
        "global_tick_cycles_checked": 100,
        "daughters": 2,
    }

if __name__ == "__main__":
    result = run_alignment()
    print("0e / CELL-LATTICE HIERARCHY v03 PASS")
    print(result)
