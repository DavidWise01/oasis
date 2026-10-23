import numpy as np, json
# Fixed-reference Adler phase locking. 8 inputs, 1 reference, 8 outputs.
# Stable locking iff abs(f-f_ref) < K/(2*pi); no nonlinear integration performed.
freqs=np.geomspace(1e-3,1e12,16)
rel=[0,1e-9,1e-6,1e-3,1e-2]
threshold=10.0
rows=[]
for f in freqs:
 for epsilon in rel:
  drift=f*epsilon
  locked=drift<threshold
  rows.append(dict(f_hz=float(f),relative_mismatch=epsilon,delta_f_hz=float(drift),locked=bool(locked)))
assert len(rows)==80
assert [sum(r['locked'] for r in rows if r['relative_mismatch']==e) for e in rel]==[16,13,10,7,6]
print(json.dumps({'test_cases':len(rows),'locked_by_mismatch':{str(e):sum(r['locked'] for r in rows if r['relative_mismatch']==e) for e in rel}},indent=2))
