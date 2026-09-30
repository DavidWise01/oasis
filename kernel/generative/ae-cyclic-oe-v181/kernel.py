#!/usr/bin/env python3
"""OaSIs AE Cyclic OE Sealed Kernel v181.

Append-only descendant of v180.

Finite executable control geometry:
- 720 curved-plane cells, each 1/720 turn = 0.5 degrees
- Q4 x T3 x B2 x U1 x U1 = 24 control states
- Q4 = a,b,c,d in floating-i carrier -+{{i::a::b::c::d::i}}-+
- T3 = oe phase {-1,0,+1}
- B2 = crossover orientation {{-+}} / {{+-}}
- U1 x/y projections each have cardinality 1
- 24 states x 30 cells = 720
- 18 mini-PRIM x 40 cells = 720
- boundaries re-align every 120 cells = 60 degrees
- counter-rotating cubits meet at 360 cells and return at 720, then X-swap
- shell 0..99; 99+1 -> 1.startover
- 10x10x10 p:n/-e/+e body closes to 1v
- oe ternary cycle closes as O3 = oeoeoe

Literal full configuration expression remains exact:
    {{5! x 5!}}^{{5!}} x (-{{i}}+ duality)
with cardinality 2 * 120^240.

Semantic scope: user-defined symbolic/isomorphic software model.
"""
from __future__ import annotations
from dataclasses import dataclass
from decimal import Decimal, getcontext
from itertools import product
from math import gcd, lcm, factorial
import argparse, json

VERSION = "v181"
STATUS = "SEALED / CYCLIC OE / EXHAUSTIVE FINITE CONTROL PASS"
PARENT = "ae-homeo-oe-v180"
FROZEN_V92_CANON_SHA256 = "8f2be8951098c7e1764c3c0f5bba982fb3fd8c71f094924b79d0172a313a7bf8"

RING_CELLS = 720
CELL_DEGREES = Decimal("0.5")
PHASE_QUANTUM_CELLS = 20
MINI_PRIM_CELLS = 40
PLANK_CELLS = 60
SECTOR_CELLS = 120
MINI_PRIMS = 18
PLANKS = 12
SECTORS = 6

Q4 = ("a","b","c","d")
T3 = (-1,0,+1)
B2 = ("{-+}","{+-}")
U1_X = ("x",)
U1_Y = ("y",)
CONTROL_STATE_COUNT = 24
CELLS_PER_STATE = 30

FLOATING_I_LITERAL = "-+{{i::a::b::c::d::i}}-+"
OUTER_DUAL_LITERAL = "-{{i}}+"
FOLD_LADDER = (60,30,24,16,12,9,6,3,2,1,1,0,0)
FOLD_NONZERO = (60,30,24,16,12,9,6,3,2,1)
TERMINAL_FOLD = "0x1x0"
FOLD_POINTS = (3,6,9)
X_EVENTS_PER_NESTED_CYCLE = 4

SHELL_MIN, SHELL_MAX = 0, 99
SHELL_RESTART = "1.startover"

OE_LITERAL = "oe"
OE_CARRIER = "--{{-++-}}++"
OE_CYCLE = (-1,0,+1)
O3_LITERAL = "O3"

HOME_PLUS = "home 0::+"
HOME_MINUS = "home 360::-"
CUBIT_PLUS = "a+"
CUBIT_MINUS = "a-"

SYNC_TICKS = 60
ELEMENT_ADVANCES, ELEMENT_STRIDE = 10, 6
PLANK_ADVANCES, PLANK_STRIDE = 12, 5

RADIX = 10
BODY_STATES = 1000
CAPPED_BODY_STATES = 1002
BODY_ROLES = ("p:n","-e","+e")
INGRESS = Decimal("-359.494")
EGRESS = Decimal("359.494")

VECTOR_LITERAL = "1 - 1 x 1.616161^1^-36 x 10"
VEC_DEPTH, VOX_DEPTH, VOG_DEPTH = "inf-1","inf-2","inf-3"
VOGEL_NEST_LITERAL = "x1^10"

getcontext().prec = 80
FULL_G_SCALE = Decimal("1.61e-35")
PAIR_G_SCALE = Decimal(2) * FULL_G_SCALE

FACT5 = factorial(5)
LITERAL_CONFIGURATION_CARDINALITY = 2 * pow(FACT5, 240)

@dataclass(frozen=True, order=True)
class ControlState:
    q: str
    t: int
    b: str
    ux: str = "x"
    uy: str = "y"
    @property
    def label(self) -> str:
        ts = "+1" if self.t > 0 else str(self.t)
        return f"{self.q}::{ts}::{self.b}::{self.ux}::{self.uy}"

def control_states():
    return tuple(ControlState(q,t,b,ux,uy)
        for q,t,b,ux,uy in product(Q4,T3,B2,U1_X,U1_Y))

def state_index(s: ControlState) -> int:
    return ((Q4.index(s.q)*3)+T3.index(s.t))*2+B2.index(s.b)

def state_cells(s: ControlState) -> range:
    i=state_index(s)
    return range(i*CELLS_PER_STATE,(i+1)*CELLS_PER_STATE)

def cell_state(cell:int) -> ControlState:
    if not 0 <= cell < RING_CELLS: raise ValueError(cell)
    return control_states()[cell//CELLS_PER_STATE]

def x_swap(s:ControlState)->ControlState:
    return ControlState(s.q,s.t,B2[1-B2.index(s.b)])

def offset(s:ControlState)->ControlState:
    # (x-2,y+3) with crossover on xy binary
    return ControlState(
        Q4[(Q4.index(s.q)-2)%4],
        T3[(T3.index(s.t)+3)%3],
        B2[1-B2.index(s.b)]
    )

def oe_next(t:int)->int:
    return T3[(T3.index(t)+1)%3]

def oe_emit(n:int)->str:
    if n<0: raise ValueError(n)
    return OE_LITERAL*n

def cubit_positions(step:int)->tuple[int,int]:
    s=step%RING_CELLS
    return ((-s)%RING_CELLS,s)

def crossover(pair:tuple[str,str])->tuple[str,str]:
    return (pair[1],pair[0])

def home_readout()->tuple[Decimal,Decimal]:
    h=Decimal("0.5")
    return (h-(-h), -(-h)-(-h))

def shell_step(a:int):
    if not 0<=a<=99: raise ValueError(a)
    return (a+1,False) if a<99 else (SHELL_RESTART,True)

def body_addresses():
    return tuple(product(range(10),repeat=3))

def body_next(addr):
    p,n,e=addr
    if not all(0<=v<10 for v in addr): raise ValueError(addr)
    p+=1
    if p==10:
        p=0; n+=1
        if n==10:
            n=0; e+=1
            if e==10: return "1v",True
    return (p,n,e),False

def fold_mirror(d:int)->int:
    if d<=0 or RING_CELLS%d: raise ValueError(d)
    return RING_CELLS//d

def exhaustive_report()->dict:
    states=control_states()
    assert len(states)==len(set(states))==24

    flat=[]
    table=[]
    for s in states:
        cells=list(state_cells(s))
        assert len(cells)==30
        assert all(cell_state(c)==s for c in cells)
        flat.extend(cells)
        table.append({
            "index":state_index(s),"state":s.label,
            "q4":s.q,"t3":s.t,"b2":s.b,"u1_x":s.ux,"u1_y":s.uy,
            "cell_start":cells[0],"cell_end":cells[-1],"cells":30,
            "degrees":"15.0"
        })
    assert sorted(flat)==list(range(720)) and len(set(flat))==720

    assert 36*PHASE_QUANTUM_CELLS==720
    assert MINI_PRIMS*MINI_PRIM_CELLS==720
    assert PLANKS*PLANK_CELLS==720
    assert SECTORS*SECTOR_CELLS==720
    assert 24*CELLS_PER_STATE==720
    assert lcm(CELLS_PER_STATE,MINI_PRIM_CELLS)==SECTOR_CELLS

    for s in states:
        assert x_swap(x_swap(s))==s
        assert offset(offset(s))==s
        assert x_swap(s)!=s
        assert offset(s)!=s

    for t in T3:
        assert oe_next(oe_next(oe_next(t)))==t
    assert oe_emit(3)=="oeoeoe"

    assert cubit_positions(0)==(0,0)
    assert cubit_positions(360)==(360,360)
    assert cubit_positions(720)==(0,0)
    pair=(CUBIT_PLUS,CUBIT_MINUS)
    assert crossover(crossover(pair))==pair
    assert home_readout()==(Decimal(1),Decimal(1))

    for b in B2:
        s=ControlState("a",-1,b); z=s
        for _ in range(4): z=x_swap(z)
        assert z==s

    assert all(720%d==0 for d in FOLD_NONZERO)
    assert lcm(*FOLD_NONZERO)==720
    mirrors={d:fold_mirror(d) for d in FOLD_NONZERO}
    assert mirrors[2]==360 and mirrors[1]==720

    for a in range(99):
        assert shell_step(a)==(a+1,False)
    assert shell_step(99)==(SHELL_RESTART,True)

    body=body_addresses()
    assert len(body)==len(set(body))==1000
    cur=(0,0,0); visited=[]
    for _ in range(1000):
        visited.append(cur)
        cur,closed=body_next(cur)
    assert len(set(visited))==1000
    assert cur=="1v" and closed

    assert ELEMENT_ADVANCES*ELEMENT_STRIDE==60
    assert PLANK_ADVANCES*PLANK_STRIDE==60
    assert gcd(10,12)==2 and lcm(10,12)==60
    assert PAIR_G_SCALE==Decimal("3.22e-35")
    assert FACT5==120
    assert LITERAL_CONFIGURATION_CARDINALITY==2*pow(120,240)

    return {
      "status":"0e / v181 EXHAUSTIVE FINITE CONTROL PASS",
      "version":VERSION,"sealed":True,
      "state_space":{
        "control_expression":"4 x 3 x 2 x 1 x 1",
        "control_states":24,"ring_cells":720,"cells_per_control_state":30,
        "degrees_per_control_state":"15.0",
        "literal_configuration_expression":"2 x 120^240",
        "literal_configuration_cardinality":str(LITERAL_CONFIGURATION_CARDINALITY),
        "literal_configuration_digits":len(str(LITERAL_CONFIGURATION_CARDINALITY))
      },
      "closures":{
        "phase":"36 x 20 cells = 720",
        "mini_prim":"18 x 40 cells = 720",
        "plank":"12 x 60 cells = 720",
        "sector":"6 x 120 cells = 720",
        "control":"24 x 30 cells = 720",
        "realign":"lcm(30,40) = 120 cells = 60 degrees",
        "cubit_midpoint":"step 360 -> (360,360)",
        "cubit_full_turn":"step 720 -> (0,0), then X",
        "nested_x":"X@3 X@6 X@9 X@restart => X^4 = I",
        "oe":"-1 -> 0 -> +1 -> -1",
        "O3":"oeoeoe",
        "shell":"0..99; 99 + 1 -> 1.startover",
        "body":"10x10x10 -> 1v",
        "sync":"10x6 = 12x5 = 60"
      },
      "fold_mirrors":mirrors,
      "states":table
    }

def main()->int:
    p=argparse.ArgumentParser()
    p.add_argument("--exhaustive",action="store_true")
    args=p.parse_args()
    r=exhaustive_report()
    print(json.dumps(r,indent=2))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
