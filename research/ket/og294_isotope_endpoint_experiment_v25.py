"""Experiment 25: scale KET's 27-slot symbolic primitive to Og-294."""
from pathlib import Path
import json
argon=". . | | . . | . . . . | | |".split()
calcium=argon+". . . . | .".split()
expanded=calcium+". . . . | . .".split()
assert (len(argon),len(calcium),len(expanded))==(14,20,27)
assert (expanded.count("."),expanded.count("|"))==(19,8)
Z,A=118,294
N=A-Z
assert (Z,N)==(118,176)
assert 98+20==Z and 249+48==A+3
assert (249-98)+(48-20)==N+3
register=[{'address':a,'pass':(a-1)//27,'slot':(a-1)%27+1,
           'operator':expanded[(a-1)%27]} for a in range(1,A+1)]
assert len(register)==294 and register[-1]['slot']==24
print('PASS: Og-294; 118p,176n; 10 full 27-slot cycles + 24 slots')
print('PASS: 249Cf + 48Ca -> 294Og + 3n conservation')
print('CAUTION: symbolic addresses != experimentally confirmed nuclides')
if __name__=='__main__':
    Path('og294_symbolic_register.json').write_text(json.dumps(register,indent=2))
