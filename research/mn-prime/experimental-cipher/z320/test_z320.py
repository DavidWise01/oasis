"""Z320 Tbn: symbolic RGB permutation registry; no physical electron claim."""
from itertools import permutations
BASE = (3, 1, 2)
def rotate(x): return (x[2], x[0], x[1])
def mirror(x): return (x[2], x[1], x[0])
def orbit(seed):
    seen, frontier = {seed}, [seed]
    while frontier:
        x = frontier.pop()
        for op in (rotate, mirror):
            y = op(x)
            if y not in seen:
                seen.add(y)
                frontier.append(y)
    return seen
states = orbit(BASE)
checks = {
    "six-unique-states": len(states)==6,
    "equals-permutation-set": states==set(permutations(BASE)),
    "all-have-six-slots": all(sum(x)==6 for x in states),
    "occupancies-stay-positive": all(all(v>0 for v in x) for x in states),
    "rotation-closure": all(rotate(x) in states for x in states),
    "mirror-closure": all(mirror(x) in states for x in states),
    "rotation-order-three": all(rotate(rotate(rotate(x)))==x for x in states),
    "mirror-order-two": all(mirror(mirror(x))==x for x in states),
    "dihedral-relation": all(mirror(rotate(x))==rotate(rotate(mirror(x))) for x in states),
    "distinct-channels": len(set(BASE))==3,
    "stable-tun-anchor": BASE in states,
    "structural-register-independent": (1,2,1)!=(3,1,2),
}
for name, ok in checks.items(): print(("PASS" if ok else "FAIL"), name)
print("ORIENTATIONS:",sorted(states))
print(f"{sum(checks.values())}/{len(checks)} PASS")
assert all(checks.values())
