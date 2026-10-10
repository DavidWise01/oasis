"""Gate17: unary/binary repeated rule audit against literal 3^3 cipher."""
RAW='''a+b-
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
LETTERS='abcdefghijklmnopqrstuvwxyz'
def proposed(k):
    if k >= 25:return None
    return ('' if k%2==0 else '-')+LETTERS[k]+'+'+LETTERS[k+1]
def run():
    differences=[(j+1,v,proposed(j)) for j,v in enumerate(RAW) if v != proposed(j)]
    initial=sum(v.rstrip('-')==proposed(j) for j,v in enumerate(RAW[:19]))
    assert len(RAW)==26 and initial==19
    assert [x[0] for x in differences]==[1,20,22,24,26]
    assert RAW[19::2]==['-t+s','-v+u','-x+w','-z+y']
    print('PASS: first 19 normalized transitions reproduce repeated unary/binary construction')
    print('Exact full matches:',len(RAW)-len(differences),'/',len(RAW))
    print('Differences:',differences)
    print('Conclusion: forward expansion changes to local reflection at transition 20')
if __name__=='__main__':run()
