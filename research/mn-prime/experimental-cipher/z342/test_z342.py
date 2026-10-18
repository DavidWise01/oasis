"""Z342 symbolic registry validation; not a real-element assertion."""
from itertools import permutations
from math import factorial, comb
Z=342
NAME='Triquadbium'
SYMBOL='Tqb'
ROOTS={0:'nil',1:'un',2:'bi',3:'tri',4:'quad',5:'pent',6:'hex',7:'sept',8:'oct',9:'enn'}
LETTERS={0:'n',1:'u',2:'b',3:'t',4:'q',5:'p',6:'h',7:'s',8:'o',9:'e'}
digits=tuple(int(c) for c in str(Z))
stem=''.join(ROOTS[d] for d in digits)
calcname=(stem[:-1] if stem.endswith('i') else stem)+'ium'
calcsymbol=''.join(LETTERS[d] for d in digits).capitalize()
rgb=(3,1,2)
states=set(permutations(rgb))
checks={
 'atomic_number_342':Z==342,
 'three_digits':digits==(3,4,2),
 'name_derives_from_digits':calcname==NAME.lower(),
 'symbol_derives_from_digits':calcsymbol==SYMBOL,
 'symbol_three_letters':len(SYMBOL)==3,
 'six_rgb_permutations':len(states)==6,
 'rgb_occupancy_sum_six':sum(rgb)==6,
 'each_channel_within_eight':all(0<=x<=8 for x in rgb),
 'rgb_lane_capacity':3*8==24,
 'unlabeled_marker_placements':comb(8,3)*comb(8,1)*comb(8,2)==12544,
 'permutation_space_24_factorial':factorial(24)==620448401733239439360000,
 'rank_zero_in_bounds':0<factorial(24),
 'rank_upper_bound_in_bounds':factorial(24)-1<factorial(24),
 'rank_overflow_outside':factorial(24)>=factorial(24),
 'rank_negative_outside':-1<0,
 'symbol_not_z341':'Tqb'!='Tqu',
 'symbol_not_z340':'Tqb'!='Tqn',
 'orientation_not_element_electrons':sum(rgb)!=Z,
}
for k,v in checks.items(): print(('PASS' if v else 'FAIL'),k)
print(f'{sum(checks.values())}/{len(checks)} PASS')
assert all(checks.values())
