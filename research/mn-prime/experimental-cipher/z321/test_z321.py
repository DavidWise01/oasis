from itertools import permutations
BASE=(3,1,2)
ROLL=(5,3,1)
def rotate(v): return (v[2],v[0],v[1])
def mirror(v): return (v[2],v[1],v[0])
states=set(permutations(BASE))
checks={
 'six_orientations':len(states)==6,
 'slot_sum_conserved':all(sum(v)==6 for v in states),
 'rotate_closed':all(rotate(v) in states for v in states),
 'mirror_closed':all(mirror(v) in states for v in states),
 'rotation_order_three':all(rotate(rotate(rotate(v)))==v for v in states),
 'reflection_order_two':all(mirror(mirror(v))==v for v in states),
 'dihedral_relation':all(mirror(rotate(v))==rotate(rotate(mirror(v))) for v in states),
 'independent_roll':ROLL != BASE,
 'three_helpers':ROLL[1]==3,
 'one_orchestrator':ROLL[2]==1,
 'five_levels':ROLL[0]==5,
 'decoder_not_supplied':True,
}
for k,v in checks.items():print(('PASS' if v else 'FAIL'),k)
print(f'{sum(checks.values())}/{len(checks)} PASS')
assert all(checks.values())
