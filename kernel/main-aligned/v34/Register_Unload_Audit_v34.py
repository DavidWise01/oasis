#!/usr/bin/env python3
"""Reproduce the boots-on-unload 8D register self-test and animation drift."""
import math

N=8
BASE=[0.62,0.18,0.85,0.34,0.71,0.09,0.55,0.28]
ANGLES=[[0,1,0.7],[2,3,-0.9],[4,5,1.1],[6,7,-0.6],
        [1,2,0.8],[3,4,-1.0],[5,6,0.5],[0,7,0.95],
        [2,5,-0.75],[1,6,0.65]]

def eye(n): return [[1.0 if i==j else 0.0 for j in range(n)] for i in range(n)]
def mm(A,B): return [[sum(A[i][k]*B[k][j] for k in range(len(B))) for j in range(len(B[0]))] for i in range(len(A))]
def tr(A): return [list(x) for x in zip(*A)]
def mv(A,v): return [sum(A[i][j]*v[j] for j in range(len(v))) for i in range(len(A))]
def givens(n,i,j,t):
    M=eye(n); c=math.cos(t); s=math.sin(t)
    M[i][i]=c; M[j][j]=c; M[i][j]=-s; M[j][i]=s
    return M
def norm(v): return math.sqrt(sum(x*x for x in v))
def mad(a,b): return max(abs(x-y) for x,y in zip(a,b))

R=eye(N)
for i,j,t in ANGLES: R=mm(givens(N,i,j,t),R)
RT=tr(R); REG=mv(R,BASE); UNL=mv(RT,REG)
RtR=mm(RT,R)
orth=max(abs(RtR[i][j]-(1 if i==j else 0)) for i in range(N) for j in range(N))
unload=mad(UNL,BASE)
endpoint=abs(norm(REG)-norm(BASE))
moved=mad(REG,BASE)

dev=(0,None,None)
for k in range(1001):
    t=k/1000
    surf=[BASE[i]+(REG[i]-BASE[i])*t for i in range(N)]
    d=abs(norm(surf)-norm(BASE))
    if d>dev[0]: dev=(d,t,norm(surf))

print("orthogonality max error",orth)
print("unload max error",unload)
print("endpoint norm error",endpoint)
print("max component movement",moved)
print("animation max norm deviation",dev)
print("mean collision", (30+70)/2, (10+90)/2)
raise SystemExit(0 if orth<1e-10 and unload<1e-10 and endpoint<1e-10 and moved>0.05 else 1)
