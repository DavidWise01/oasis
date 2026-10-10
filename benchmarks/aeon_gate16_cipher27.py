"""Gate 16 literal 3^3 cipher audit. Preserve all 26 user transitions verbatim."""
EDGES = """a+b-
-b+c
c+d
-d+e
e+f
-f+g
g+h
-h+i
i+j
-j+k
k+l
-l+m
m+n
-n+o
o+p
-p+q
q+r
-r+s
s+t
-t+s
u+v
-v+u
w+x
-x+w
y+z
-z+y""".splitlines()
def audit():
    assert len(EDGES)==26
    assert 3**3==27
    assert len(set(EDGES))==26
    assert EDGES[0]=="a+b-" and EDGES[19]=="-t+s"
    assert EDGES[21]=="-v+u" and EDGES[23]=="-x+w" and EDGES[25]=="-z+y"
    print("PASS: 26 literal expressions / 27 ternary-address positions")
    print("Unresolved boundaries: trailing '-' at a+b-, -t+s, and disjoint u/v, w/x, y/z blocks")
    print("No inference of one connected chain; no automatic spelling repair")
if __name__=="__main__":audit()
