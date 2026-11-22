#!/usr/bin/env python3
"""AETHER-096B: conservative validation-based context detection, fresh test seeds.
Requires numpy, scipy, scikit-learn. Reproduces the diagnostic CSVs.
"""
from pathlib import Path
import csv,json
import numpy as np
from scipy.stats import beta
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import confusion_matrix
OUT=Path(__file__).resolve().parent
REGIMES=('stable','step','ramp','burst','asymmetric_burst','oscillatory_shift')
TRAIN=range(96001,96033);VALID=range(96101,96125);TEST=range(96301,96341)
T=72;AUD=140;SENT=80;ACT=150;WINDOW=5;CONTEXT=12
UB={n:np.array([1. if f==n else beta.ppf(.95,f+1,n-f) for f in range(n+1)]) for n in (140,280,420,560,700)}
def upper(f,n):return UB[n][int(f)]
def save(name,rows):
 with (OUT/name).open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def environment(seed,g):
 offsets=dict(stable=0,step=10000,ramp=20000,burst=30000,asymmetric_burst=40000,oscillatory_shift=50000)
 rng=np.random.default_rng(seed+offsets[g]);start=int(rng.integers(15,39));duration=int(rng.integers(14,26));peak=float(rng.uniform(.022,.055))
 risk=[]
 for t in range(T):
  j=t-start
  if g=='stable':p=.003
  elif g=='step':p=peak if 0<=j<duration else .003
  elif g=='ramp':p=.003+(peak-.003)*min(1.,max(0,j/10)) if 0<=j<duration else .003
  elif g=='burst':p=peak if 0<=j<duration and j%6<3 else .003
  elif g=='asymmetric_burst':p=.11 if 0<=j<duration and j%7==0 else (.012 if 0<=j<duration else .003)
  else:p=.003+(peak-.003)*(.5+.5*np.sin(j*.9)) if 0<=j<duration else .003
  risk.append(p)
 r=np.array(risk)
 return r,rng.binomial(AUD,r),rng.binomial(SENT,r),rng.binomial(ACT,r)
def features(audit,tick):
 a=np.asarray(audit[max(0,tick-CONTEXT+1):tick+1],dtype=float)
 b=np.pad(a,(CONTEXT-len(a),0));dif=np.diff(b)
 return np.r_[b,[b.mean(),b.std(),b.max(),np.mean(b>3),np.mean(b>7),np.mean(abs(dif)),np.sum(np.maximum(0,b-3)),np.mean(b[-4:]),np.mean(b[:4]),np.mean(b[-4:])-np.mean(b[:4])]]
def dataset(seeds):
 X=[];Y=[]
 for g in REGIMES:
  for seed in seeds:
   _,audit,_,_=environment(seed,g)
   for t in range(T):
    X.append(features(audit,t));Y.append(int(g=='burst'))
 return np.array(X),np.array(Y)
tx,ty=dataset(TRAIN);vx,vy=dataset(VALID)
model=RandomForestClassifier(n_estimators=100,max_depth=7,min_samples_leaf=25,max_features='sqrt',random_state=96096,n_jobs=1,class_weight='balanced_subsample')
model.fit(tx,ty);vprob=model.predict_proba(vx)[:,1]
# Predeclared validation-only screen: <=0.5% false promotions, >=3% burst recall.
threshold=1.01
for q in np.arange(.65,.991,.01):
 fp=int(np.sum((vprob>=q)&(vy==0)))
 tp=int(np.sum((vprob>=q)&(vy==1)))
 if fp/np.sum(vy==0)<=.005 and tp/np.sum(vy==1)>=.03:
  threshold=round(float(q),4);break
hx,hy=dataset(TEST);prob=model.predict_proba(hx)[:,1]
conf=confusion_matrix(hy,prob>=threshold,labels=[0,1])
N0=int(conf[0].sum());FP=int(conf[0,1]);N1=int(conf[1].sum());TP=int(conf[1,1])
rows=[];position=0
for g in REGIMES:
 for seed in TEST:
  risk,audit,sentinel,actions=environment(seed,g)
  pred=prob[position:position+T];position+=T
  for policy in ('rolling','context_gate','oracle_burst'):
   active=True;recovery=[];wrong=held=labels=authorized=probes=promotions=false_promotions=0
   for tick in range(T):
    a=audit[max(0,tick-WINDOW+1):tick+1]
    bound=upper(a.sum(),len(a)*AUD)
    feature='denied' if bound>.04 else ('uncertain' if bound>.022 or audit[tick]>=2 else 'quiet')
    context_accept=(pred[tick]>=threshold if policy=='context_gate' else (g=='burst' if policy=='oracle_burst' else False))
    probe=bool(context_accept and feature=='uncertain')
    alarm=bool(probe and sentinel[tick]>=3)
    if alarm:active=False;recovery=[]
    if not active:
     recovery=(recovery+[int(audit[tick])])[-WINDOW:]
     if len(recovery)==WINDOW and upper(sum(recovery),AUD*WINDOW)<=.02 and not alarm:active=True
    allow=bool(bound<=.02 and active and not alarm)
    wrong+=int(actions[tick]) if allow else 0;held+=0 if allow else ACT
    labels+=AUD+SENT*int(probe);authorized+=int(allow);probes+=int(probe)
    promotions+=int(context_accept);false_promotions+=int(context_accept and g!='burst')
   cost=10*wrong+.05*held+.01*labels
   rows.append(dict(regime=g,seed=seed,policy=policy,wrong=wrong,withheld=held,labels=labels,authorized_ticks=authorized,probes=probes,promotions=promotions,false_promotions=false_promotions,cost=round(cost,2)))
save('seed_results.csv',rows)
summary=[]
for g in (*REGIMES,'ALL'):
 for policy in ('rolling','context_gate','oracle_burst'):
  z=[r for r in rows if r['policy']==policy and (g=='ALL' or g==r['regime'])]
  summary.append(dict(regime=g,policy=policy,cases=len(z),cost=round(sum(r['cost'] for r in z),2),wrong=sum(r['wrong'] for r in z),withheld=sum(r['withheld'] for r in z),labels=sum(r['labels'] for r in z),authorized_ticks=sum(r['authorized_ticks'] for r in z),probes=sum(r['probes'] for r in z),promotion_ticks=sum(r['promotions'] for r in z),false_promotion_ticks=sum(r['false_promotions'] for r in z)))
save('results.csv',summary)
save('context_confusion.csv',[dict(class_name='nonburst',total=N0,classified_burst=FP,classification_rate=round(FP/N0,6)),dict(class_name='burst',total=N1,classified_burst=TP,classification_rate=round(TP/N1,6))])
passed=bool(FP/N0<=.01 and TP/N1>=.03 and next(r['cost'] for r in summary if r['regime']=='ALL' and r['policy']=='context_gate')<=next(r['cost'] for r in summary if r['regime']=='ALL' and r['policy']=='rolling'))
manifest=dict(bound='AETHER-096B',phase='II',status='PASSED' if passed else 'FAILED_PROMOTION_GATE',phase_completion_pct=12.5 if passed else 0,train_seeds=[96001,96032],validation_seeds=[96101,96124],test_seeds=[96301,96340],contexts=list(REGIMES),threshold=round(threshold,4),validation_false_promotion_budget=.005,acceptance={'max_test_false_promotions':.01,'min_test_burst_recall':.03,'max_cost_increase':0},false_promotion_rate=round(FP/N0,6),burst_recall=round(TP/N1,6),caveat='Only observed audit labels are on-line features. Hidden true labels are for supervised training and test reporting; oracle comparator is unavailable at runtime. No anytime-risk guarantee.')
(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps(dict(manifest=manifest,summary=[r for r in summary if r['regime']=='ALL']),indent=2))
