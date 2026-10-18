"""Z323: lossless RGB occupancy address encoding, Layer-1 symbolic only."""
from itertools import permutations

LANES = ('R', 'G', 'B')
BASE = (3, 1, 2)
CAPACITY = 8

def encode(counts):
    assert len(counts) == 3 and all(isinstance(n, int) and 0 <= n <= CAPACITY for n in counts)
    return tuple((lane, slot) for lane, n in zip(LANES, counts) for slot in range(n))

def decode(addresses):
    assert len(addresses) == len(set(addresses))
    assert all(lane in LANES and isinstance(slot, int) and 0 <= slot < CAPACITY for lane, slot in addresses)
    counts = tuple(sum(lane == name for lane, _ in addresses) for name in LANES)
    assert set(addresses) == set(encode(counts)), 'noncanonical/noncontiguous address layout'
    return counts

def rotate(counts): return (counts[2], counts[0], counts[1])
def mirror(counts): return (counts[2], counts[1], counts[0])

states = tuple(sorted(set(permutations(BASE))))
checks = {
    '24_available_addresses': len(LANES)*CAPACITY == 24,
    'six_unique_states': len(states) == 6,
    'tun_identity': decode(encode(BASE)) == BASE,
    'six_markers': len(encode(BASE)) == 6,
    'roundtrip_all_six': all(decode(encode(s)) == s for s in states),
    'unique_addresses_all_states': all(len(encode(s)) == len(set(encode(s))) for s in states),
    'within_lane_capacity': all(all(n <= CAPACITY for n in s) for s in states),
    'rotation_roundtrip': all(decode(encode(rotate(s))) == rotate(s) for s in states),
    'mirror_roundtrip': all(decode(encode(mirror(s))) == mirror(s) for s in states),
    'three_rotations_restore': all(rotate(rotate(rotate(s))) == s for s in states),
    'two_mirrors_restore': all(mirror(mirror(s)) == s for s in states),
    'structural_121_independent': BASE != (1,2,1),
    'governance_531_independent': BASE != (5,3,1),
    'reject_duplicate_address': False,
    'reject_noncanonical_gap': False,
}
for key, bad in [('reject_duplicate_address', (('R',0),('R',0))), ('reject_noncanonical_gap', (('R',1),))]:
    try:
        decode(bad)
    except AssertionError:
        checks[key] = True
for key, passed in checks.items():
    print(('PASS' if passed else 'FAIL'), key)
print(f'{sum(checks.values())}/{len(checks)} PASS')
assert all(checks.values())
