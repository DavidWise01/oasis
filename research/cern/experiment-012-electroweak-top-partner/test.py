import numpy as np
import json
v=246.0; mt0=173.0; M=1200.0
assert abs(-1/6-1/2+2/3)<1e-12
assert abs(-2/3+2/3)<1e-12
rows=[]
for lam in [0,.1,.3,.5,1.0]:
    A=np.array([[mt0,lam*v/np.sqrt(2)],[0,M]])
    U,s,Vh=np.linalg.svd(A)
    order=np.argsort(s);s=s[order];U=U[:,order];Vh=Vh[order,:]
    assert np.allclose(U@np.diag(s)@Vh,A)
    assert np.allclose(U.T@U,np.eye(2))
    assert 0<s[0]<s[1]
    rows.append({"lambda":lam,"light_GeV":float(s[0]),"heavy_GeV":float(s[1]),"mixing_L":float(abs(U[0,1]))})
assert rows[0]["mixing_L"]==0
assert abs(.3/.25-1.2)<1e-12
print(json.dumps(rows,indent=2))
print("Checks passed. Toy model; no cross-section prediction.")
