import numpy as np,json
rng=np.random.default_rng(25025);T=6000;sigma=.06;n=64;rows=[]
for rho in [0,.01,.1,.5,1.]:
 common=rng.normal(size=(T,1))*sigma*np.sqrt(rho)
 independent=rng.normal(size=(T,n))*sigma*np.sqrt(1-rho)
 signal=rng.uniform(-np.pi/2,np.pi/2,size=(T,1))
 observed=signal+common+independent
 error=observed.mean(axis=1)-signal[:,0]
 for reference_noise in [None,.005,.02]:
  if reference_noise is None: residual=error;name='no_reference'
  else:
   residual=error-(common[:,0]+rng.normal(size=T)*reference_noise)
   name='reference_'+str(reference_noise)
  rows.append(dict(rho=rho,method=name,rmse_rad=float(np.sqrt(np.mean(residual**2)))))
 assert np.allclose(observed[:,0]-observed[:,1],independent[:,0]-independent[:,1])
assert len(rows)==15
for rho in [.1,.5,1.]:
 assert next(r['rmse_rad'] for r in rows if r['rho']==rho and r['method']=='reference_0.005') < next(r['rmse_rad'] for r in rows if r['rho']==rho and r['method']=='no_reference')
print(json.dumps(rows,indent=2))
