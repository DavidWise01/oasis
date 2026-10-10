"""Gate 18: exact 26-expression cipher: local closure vs global closure."""
import re
WORDS='''a+b-
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
-z+y'''.splitlines()
def test():
    parsed=[]
    for word in WORDS:
        m=re.fullmatch(r'(-?)([a-z])\+([a-z])(-?)',word)
        assert m is not None,word
        parsed.append((m.group(2),m.group(3)))
    graph={x:set() for x in 'abcdefghijklmnopqrstuvwxyz'}
    for a,b in parsed:graph[a].add(b);graph[b].add(a)
    unseen=set(graph); components=[]
    while unseen:
        stack=[min(unseen)]; group=set()
        while stack:
            x=stack.pop()
            if x in group:continue
            group.add(x);stack.extend(graph[x]-group)
        unseen-=group;components.append(''.join(sorted(group)))
    checks={
     '26 expressions':len(parsed)==26,
     'first 19 forward':all(parsed[i]==(chr(97+i),chr(98+i)) for i in range(19)),
     'four local return pairs':all(parsed[j]==tuple(reversed(parsed[j-1])) for j in (19,21,23,25)),
     'return pairs retain endpoints':all(set(parsed[j])==set(parsed[j-1]) for j in (19,21,23,25)),
     'all 26 letters':set(''.join(a+b for a,b in parsed))==set('abcdefghijklmnopqrstuvwxyz'),
     'dot is not a letter transition':all('.' not in x for x in WORDS),
     'not globally closed':parsed[-1][1]!=parsed[0][0],
     'four components':components==['abcdefghijklmnopqrst','uv','wx','yz']
    }
    for name,ok in checks.items():print('PASS' if ok else 'FAIL',name)
    print('components:',components,'global closure:',parsed[-1][1]==parsed[0][0])
    assert all(checks.values())
if __name__=='__main__':test()
