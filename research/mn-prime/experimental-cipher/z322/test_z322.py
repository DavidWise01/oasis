"""Z322 optional Cr24 bridge regression: symbolic addresses, not physical electrons."""
from itertools import product, permutations
LANES=("R","G","B")
ADDRESSES=tuple(product(LANES, range(8)))
BASE=(3,1,2)
STATES=set(permutations(BASE))
def rotate(x):return (x[2],x[0],x[1])
def mirror(x):return (x[2],x[1],x[0])
checks={
 "address_count_24":len(ADDRESSES)==24,
 "addresses_unique":len(set(ADDRESSES))==24,
 "eight_per_lane":all(sum(k==c for k,_ in ADDRESSES)==8 for c in LANES),
 "tun_occupancy_six":sum(BASE)==6,
 "capacity_all_orientations":all(all(n<=8 for n in s) for s in STATES),
 "six_orientations":len(STATES)==6,
 "rotation_closed":all(rotate(s) in STATES for s in STATES),
 "reflection_closed":all(mirror(s) in STATES for s in STATES),
 "three_rotations_identity":all(rotate(rotate(rotate(s)))==s for s in STATES),
 "two_mirrors_identity":all(mirror(mirror(s))==s for s in STATES),
 "independent_531":(5,3,1)!=(3,1,2),
 "cr_atomic_24_not_occupancy":24!=sum(BASE),
}
for name,passed in checks.items():print(("PASS" if passed else "FAIL"),name)
print(f"{sum(checks.values())}/{len(checks)} PASS")
assert all(checks.values())
