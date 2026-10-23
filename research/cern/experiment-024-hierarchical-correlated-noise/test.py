import numpy as np, json
rng=np.random.default_rng(24024)
trials=4096
sigma=.06
rho_values=[0,.01,.1,.5,1.]
rows=[]
for d in range(11):
 n=2**d
 shared=rng.normal(size=(trials,1))
 independent=rng.normal(size=(trials,n))
 for rho in rho_values:
  level=sigma*(np.sqrt(rho)*shared+np.sqrt(1-rho)*independent)
  messages=0
  while level.shape[1]>1:
   level=(level[:,::2]+level[:,1::2])/2
   messages+=level.shape[1]*2
  rmse=float(np.sqrt(np.mean(level[:,0]**2)))
  theoretical=float(sigma*np.sqrt(rho+(1-rho)/n))
  rows.append(dict(depth=d,leaves=n,rho=rho,rmse_rad=rmse,expected_rmse_rad=theoretical,messages_per_trial=messages))
assert len(rows)==55
assert all(x["messages_per_trial"]==2*(x["leaves"]-1) for x in rows)
assert all(abs(x["rmse_rad"]/x["expected_rmse_rad"]-1)<.055 for x in rows)
print(json.dumps([r for r in rows if r["depth"]==10],indent=2))
