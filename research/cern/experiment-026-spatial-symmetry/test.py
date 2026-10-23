import numpy as np,json
rng=np.random.default_rng(26026);N=100000
theta=rng.normal(0,.3,N);c=rng.normal(0,.06,N);a=rng.normal(0,.04,N)
noise=lambda:rng.normal(0,.01,N)
s1=theta+c+a+noise();ns1=c+a+noise();s2=theta+c-a+noise();ns2=c-a+noise();s3=theta+c+noise()
methods={'center':s3,'raw_symmetric':(s1+s2)/2,'internal_differential':((s1-ns1)+(s2-ns2))/2,'left_only':s1-ns1}
rmse={k:float(np.sqrt(np.mean((v-theta)**2))) for k,v in methods.items()}
M=np.array([[1,1,1],[0,1,1],[1,1,-1],[0,1,-1],[1,1,0]],float)
assert np.linalg.matrix_rank(M)==3
assert rmse['internal_differential']<rmse['center']
ns1_bad=theta+c+a+noise();ns2_bad=theta+c-a+noise()
bad=((s1-ns1_bad)+(s2-ns2_bad))/2
bad_rmse=float(np.sqrt(np.mean((bad-theta)**2)))
assert bad_rmse>rmse['center']
print(json.dumps({'register':'[-+{s1}{ns1}[(s3)]{ns2}{s2}-+]','spatials':'{{ 1s8t1u8v 001w8x1y8z }}','trials':N,'rmse':rmse,'bad_reference_rmse':bad_rmse},indent=2))
