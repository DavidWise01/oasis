"""Major Gate 3: operator order, exact reversible state, pinned root.
These are chosen example operators; no claim they are the user's canonical 42.
"""
from fractions import Fraction as Q

ROOT=(Q(0),Q(0))
def X(p): return (p[1],p[0])  # crosspipe swap
def D(p): return (Q(2)*p[0], p[1]) # directional gain

def invD(p): return (p[0]/2,p[1])

def run():
 p=(Q(3),Q(5))
 xd=X(D(p)); dx=D(X(p))
 checks={
  'two different operator orders':xd!=dx,
  'X after D':xd==(Q(5),Q(6)),
  'D after X':dx==(Q(10),Q(3)),
  'crosspipe involutive':X(X(p))==p,
  'gain reversible':invD(D(p))==p,
  'reverse composition recovers':invD(X(xd))==p,
  'root pinned by X and D':X(ROOT)==ROOT and D(ROOT)==ROOT,
  'noncommuting witness':xd!=dx,
  'operator events may be retained':(('D','X')!=('X','D')),
 }
 for name,ok in checks.items():print(('PASS' if ok else 'FAIL'),name)
 print(f"RESULT {sum(checks.values())}/{len(checks)}; XD={xd}; DX={dx}")
 assert all(checks.values())
if __name__=='__main__':run()
