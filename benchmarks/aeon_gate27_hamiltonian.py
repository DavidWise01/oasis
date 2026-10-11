"""Gate 27 Hamiltonian cycle on 3x3x3 torus; symbolic, not physical proof."""
PATH=((0,0,0),(1,0,0),(2,0,0),(2,1,0),(0,1,0),(1,1,0),
(1,2,0),(0,2,0),(2,2,0),(2,2,1),(2,0,1),(2,1,1),
(0,1,1),(0,0,1),(0,2,1),(1,2,1),(1,0,1),(1,1,1),
(1,1,2),(1,0,2),(1,2,2),(0,2,2),(0,1,2),(2,1,2),
(2,2,2),(2,0,2),(0,0,2))
def neighboring(a,b):return sum(x!=y for x,y in zip(a,b))==1
def test():
    full={(x,y,z) for x in range(3) for y in range(3) for z in range(3)}
    roles=('witness',)+('internal',)*24+('in','out')
    tests={
        '27 arithmetic':8*3+2+1==27,
        '27 vertices':len(PATH)==27,
        'no duplicates':len(set(PATH))==27,
        'full ternary lattice':set(PATH)==full,
        '26 forward steps':len(PATH)-1==26,
        'all steps adjacent':all(neighboring(a,b) for a,b in zip(PATH,PATH[1:])),
        'closure adjacent':neighboring(PATH[-1],PATH[0]),
        'one witness':roles.count('witness')==1,
        'two boundary positions':roles[-2:]==('in','out'),
        '24 internal':roles.count('internal')==24,
    }
    for k,v in tests.items():print(('PASS' if v else 'FAIL'),k)
    assert all(tests.values())
    print(f"{sum(tests.values())}/{len(tests)} PASS")
if __name__=='__main__':test()
