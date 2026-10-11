"""Gate 6: quantum probability conservation of a symbolic two-channel crosspipe."""
import numpy as np
X=np.array([[0,1],[1,0]],dtype=complex)
I=np.eye(2,dtype=complex)
def norm(v):return float(np.vdot(v,v).real)
def run():
    states=[np.array([1,0],complex), np.array([0,1],complex),np.array([1,1j],complex)/np.sqrt(2),np.array([np.sqrt(.3),1j*np.sqrt(.7)],complex)]
    checks={
      'crosspipe unitary':np.allclose(X.conj().T@X,I),
      'inverse equals adjoint':np.allclose(np.linalg.inv(X),X.conj().T),
      'double crosspipe restores state':all(np.allclose(X@X@s,s) for s in states),
      'probability norm retained':all(np.isclose(norm(X@s),norm(s)) for s in states),
      'complex relative phase retained':np.allclose(X@states[2],np.array([1j,1])/np.sqrt(2)),
      'linear superposition':np.allclose(X@(states[0]+1j*states[1]),X@states[0]+1j*(X@states[1])),
      'original labels exchanged':np.allclose(X@states[0],states[1]),
      'zero vector fixed':np.allclose(X@np.zeros(2),np.zeros(2)),
      'nonunitary gain detected':not np.allclose(np.diag([2,1]).conj().T@np.diag([2,1]),I),
      'phase rotation also unitary':np.allclose(np.diag([1,np.exp(1j*np.pi/12)]).conj().T@np.diag([1,np.exp(1j*np.pi/12)]),I),
    }
    for k,v in checks.items(): print(('PASS' if v else 'FAIL'),k)
    print(f'RESULT {sum(checks.values())}/{len(checks)}')
    assert all(checks.values())
if __name__=='__main__':run()
