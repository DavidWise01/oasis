#!/usr/bin/env python3
"""A.I.O.N. v1.4 synthetic pulse-response spectroscopy.

Reduced-order synthetic readout experiment extending v1.2/v1.3 assumed trap
populations. Not a direct MOS current or measured ALON/Si response. An RC
readout resets to zero at release; the instrument's impulse response is
convolved with the released trap charge. Correlated Gaussian noise is modeled
by a specified covariance. No physical materials claims.
"""
from __future__ import annotations
import csv, json, math, pathlib
import numpy as np
from scipy.linalg import solve_triangular
from scipy.optimize import least_squares

ROOT=pathlib.Path(__file__).resolve().parent
SEED=20261012+14
RNG=np.random.default_rng(SEED)
FAST={'capture_s':.03,'release_s':.15,'fraction':.35}
SLOW={'capture_s':.22,'release_s':1.60,'fraction':.65}
WIDTHS=np.array([.02,.08,.30,1.20,4.0])
TRAIN_WIDTHS=(.02,.30,4.0)
HOLDOUT_WIDTHS=(.08,1.20)
TIMES=np.array([.006,.012,.02,.035,.055,.08,.12,.18,.27,.40,.60,.90,1.30,2.,3.,4.5,6.5,9.])
SIGMA=.004
RHO=.55
NOISE_TAU_S=.12
TAU_GRID=np.exp(np.linspace(np.log(.008),np.log(40.),91))
REPEATS=2
PROTOCOLS={
  'fast_20ms':{'instrument_tau_s':.02,'dead_time_s':.006,'training_widths':TRAIN_WIDTHS},
  'moderate_60ms':{'instrument_tau_s':.06,'dead_time_s':.06,'training_widths':TRAIN_WIDTHS},
  'slow_frontend_180ms':{'instrument_tau_s':.18,'dead_time_s':.08,'training_widths':TRAIN_WIDTHS},
  'late_480ms':{'instrument_tau_s':.02,'dead_time_s':.48,'training_widths':TRAIN_WIDTHS},
  'single_pulse':{'instrument_tau_s':.02,'dead_time_s':.006,'training_widths':(4.0,)},
}

def convolution(times, tau_release, tau_instrument):
    """(exp(-t/tau_release) * causal RC unit-area kernel)(t), zero IC."""
    t=np.asarray(times,dtype=float)
    r=np.asarray(tau_release,dtype=float)
    i=float(tau_instrument)
    # use expm1 for stability near equal time constants
    delta=1./i-1./r
    with np.errstate(divide='ignore', invalid='ignore'):
        raw=(np.exp(-t/r)-np.exp(-t/i))/(i*delta)
    return np.where(np.abs(delta)<1e-9, (t/i)*np.exp(-t/i),raw)

def primitive_response(width,t,instrument,cap,release):
    return -np.expm1(-width/cap)*convolution(t,release,instrument)

def truth_response(width,t,instrument):
    return (FAST['fraction']*primitive_response(width,t,instrument,FAST['capture_s'],FAST['release_s'])+
            SLOW['fraction']*primitive_response(width,t,instrument,SLOW['capture_s'],SLOW['release_s']))

def model_single(theta,w,t,inst):
    amp,lc,lr=theta
    return amp*primitive_response(w,t,inst,np.exp(lc),np.exp(lr))

def model_dual(theta,w,t,inst):
    amp,f,lcf,d_cap,lrf,d_release=theta
    cf=np.exp(lcf);cs=cf*np.exp(d_cap)
    rf=np.exp(lrf);rs=rf*np.exp(d_release)
    return amp*(f*primitive_response(w,t,inst,cf,rf)+(1-f)*primitive_response(w,t,inst,cs,rs))

def model_spectrum(theta,w,t,inst):
    amp,mu,lsigma,lscale,alpha=theta
    taus=TAU_GRID
    sigma=np.exp(lsigma)
    weights=np.exp(-.5*((np.log(taus)-mu)/sigma)**2)
    weights/=np.sum(weights)
    caps=np.exp(lscale)*taus**alpha
    # atom/readout kernel basis; array transposed to shape [time, tau]
    f=-np.expm1(-w/caps)
    resp=convolution(np.asarray(t)[:,None],taus[None,:],inst)
    return amp*((resp*f)@weights)

SPECS={
 'single':(model_single,[.1,np.log(.006),np.log(.008)],[2.,np.log(5.),np.log(40.)],
            [[1,np.log(.1),np.log(1.)],[1,np.log(.05),np.log(.3)]]),
 'dual':(model_dual,[.1,.01,np.log(.004),np.log(1.05),np.log(.008),np.log(1.05)],
          [2.,.99,np.log(2.),np.log(70.),np.log(4.),np.log(150.)],
          [[1,.35,np.log(.03),np.log(.22/.03),np.log(.15),np.log(1.6/.15)],
           [1,.5,np.log(.08),np.log(4.),np.log(.10),np.log(8.)],
           [1,.2,np.log(.02),np.log(12.),np.log(.2),np.log(12.)]]),
 'spectrum':(model_spectrum,[.1,np.log(.009),np.log(.07),np.log(.002),0.],
             [2.,np.log(30.),np.log(3.),np.log(6.),2.],
             [[1,np.log(.6),np.log(1.),np.log(.18),.9],
              [1,np.log(.3),np.log(.7),np.log(.16),1.],
              [1,np.log(.9),np.log(1.2),np.log(.14),.8]]),
}

def covariance(t):
    dt=np.abs(np.asarray(t)[:,None]-np.asarray(t)[None,:])
    return SIGMA**2*((1.-RHO)*np.eye(len(t))+RHO*np.exp(-dt/NOISE_TAU_S))

def make_data(protocol):
    cfg=PROTOCOLS[protocol]
    t=TIMES[TIMES>=cfg['dead_time_s']]
    cov=covariance(t)
    L=np.linalg.cholesky(cov)
    shots=[]
    for w in WIDTHS:
        for rep in range(REPEATS):
            true=truth_response(w,t,cfg['instrument_tau_s'])
            measured=true+L@RNG.standard_normal(len(t))
            shots.append({'width_s':float(w),'replicate':rep,'t':t.copy(),'true':true,
                          'measured':measured,'L':L})
    return shots

def residual(model_name,theta,shots,inst):
    pred=SPECS[model_name][0]
    return np.concatenate([solve_triangular(s['L'],pred(theta,s['width_s'],s['t'],inst)-s['measured'],lower=True,check_finite=False) for s in shots])

def fit(name,shots,inst):
    func,lo,hi,initials=SPECS[name]
    best=None
    for theta in initials:
        res=least_squares(lambda z: residual(name,z,shots,inst),np.array(theta,dtype=float),bounds=(lo,hi),max_nfev=350,
                          ftol=1e-9,gtol=1e-9,xtol=1e-9)
        if best is None or res.cost<best.cost:
            best=res
    return best

def describe(name,x):
    if name=='dual':
        A,f,lcf,gc,lrf,gr=x
        return {'amplitude':float(A),'fast_fraction':float(f),'fast_capture_s':float(np.exp(lcf)),
                'slow_capture_s':float(np.exp(lcf+gc)),'fast_release_s':float(np.exp(lrf)),
                'slow_release_s':float(np.exp(lrf+gr))}
    if name=='single':
        return {'amplitude':float(x[0]),'capture_s':float(np.exp(x[1])),'release_s':float(np.exp(x[2]))}
    return {'amplitude':float(x[0]),'median_release_s':float(np.exp(x[1])),
            'log_release_width':float(np.exp(x[2])),'capture_scale':float(np.exp(x[3])),'capture_exponent':float(x[4])}

def csvout(name,rows):
    with (ROOT/name).open('w',newline='',encoding='utf-8') as fh:
        w=csv.DictWriter(fh,list(rows[0].keys()));w.writeheader();w.writerows(rows)

def run():
    # Analytical invariants for two-trap causal readout
    assert abs(convolution(np.array([0.]),.15,.02)[0])<1e-12
    assert np.all(convolution(np.array([.1,.5,2.]),.15,.02)>=0)
    assert abs(float(truth_response(4.,np.array([.5]),.02)[0])-float(model_dual(SPECS['dual'][3][0],4.,np.array([.5]),.02)[0]))<1e-12
    assert all(np.linalg.eigvalsh(covariance(TIMES))>0)
    measures=[];fitrows=[];predict=[];results={}; checks=4
    for p,cfg in PROTOCOLS.items():
        inst=cfg['instrument_tau_s'];shots=make_data(p)
        training=[s for s in shots if s['width_s'] in cfg['training_widths']]
        validation=[s for s in shots if s['width_s'] not in cfg['training_widths']]
        t=shots[0]['t'];ntrain=sum(len(s['t']) for s in training)
        assert ntrain>2*len(SPECS['dual'][1]);checks+=1
        for s in shots:
            for tt,y,z in zip(s['t'],s['measured'],s['true']):
                measures.append({'protocol':p,'pulse_width_s':s['width_s'],'replicate':s['replicate'],
                                 'readout_time_s':float(tt),'synthetic_observed_charge':float(y),
                                 'noiseless_truth':float(z),'sigma_fraction':SIGMA,
                                 'instrument_tau_s':inst,'first_record_time_s':cfg['dead_time_s']})
        ranked=[]
        for name in SPECS:
            z=fit(name,training,inst)
            rr=residual(name,z.x,training,inst)
            chi2=float(rr@rr)
            k=len(z.x)
            bic=chi2+k*np.log(ntrain) # shared covariance with known sigma; constants suppressed
            yval=np.concatenate([s['measured'] for s in validation])
            yhat=np.concatenate([SPECS[name][0](z.x,s['width_s'],s['t'],inst) for s in validation])
            val_rmse=float(np.sqrt(np.mean((yval-yhat)**2)))
            record={'protocol':p,'model':name,'n_training':ntrain,'n_validation':len(yval),
                    'parameters':k,'whitened_chi2':chi2,'relative_BIC':float(bic),
                    'holdout_rmse':val_rmse,'success':bool(z.success),'parameter_json':json.dumps(describe(name,z.x))}
            fitrows.append(record);ranked.append(record)
            assert np.all(np.isfinite(z.x)) and np.isfinite(bic) and np.isfinite(val_rmse)
            checks+=1
            for s in shots:
                for tt,y,y0 in zip(s['t'],s['measured'],s['true']):
                    predict.append({'protocol':p,'model':name,'pulse_width_s':s['width_s'],
                                    'replicate':s['replicate'],'readout_time_s':float(tt),
                                    'observed':float(y),'noiseless_truth':float(y0),
                                    'prediction':float(SPECS[name][0](z.x,s['width_s'],np.array([tt]),inst)[0])})
        winner=min(ranked,key=lambda r:r['relative_BIC'])
        results[p]={'instrument_tau_s':inst,'dead_time_s':cfg['dead_time_s'],'training_pulses_s':cfg['training_widths'],
                    'holdout_pulses_s':[w for w in WIDTHS if w not in cfg['training_widths']],
                    'winner_by_BIC':winner['model'],
                    'BICs':{r['model']:r['relative_BIC'] for r in ranked},
                    'holdout_rmse':{r['model']:r['holdout_rmse'] for r in ranked},
                    'dual_estimates':json.loads(next(r for r in ranked if r['model']=='dual')['parameter_json'])}
    csvout('aion-v14-synthetic-pulses.csv',measures)
    csvout('aion-v14-fit-ranking.csv',fitrows)
    csvout('aion-v14-model-predictions.csv',predict)
    report={
        'schema':'aion.v1.4.pulse-identifiability.v1',
        'classification':'SYNTHETIC, REDUCED-ORDER TRAP READOUT AND MODEL-SELECTION TEST; not actual ALON/Si data',
        'material_reference':'Al23O27N5 unrelaxed ALON dielectric; separate Si-like channel; no iodine',
        'inheritance':'Uses nominal 300 K time constants/fractions from A.I.O.N. v1.2, compares v1.3 model families; adds pulse charging, instrument response, correlated noise, held-out widths',
        'truth':{'fast':FAST,'slow':SLOW,'T_K':300},
        'noise':{'sigma_relative_charge':SIGMA,'correlation_fraction':RHO,'decay_time_s':NOISE_TAU_S,
                 'covariance':'sigma²*((1-rho)*I+rho*exp(-abs(dt)/tau_corr))'},
        'instrument':'causal first-order low-pass, reset to zero at release; effects convolved exactly with each exponential before noise; dead time excludes earlier measurements',
        'measured_quantity':'normalized charge recovery proxy, not current, energy, capacitance or electrical measurement',
        'pulse_widths_s':list(WIDTHS),'sampling_times_s':list(TIMES),'replicates_per_width':REPEATS,
        'protocols':results,
        'fit_objective':'known-covariance Gaussian generalized least squares; same instrument model across fitted candidates',
        'BIC':'chi2+k*ln(n), Gaussian constants common within each protocol omitted; lower better; do not compare scores across different sampling protocols',
        'cross_validation':'held-out pulse widths, validation RMSE on noisy synthetic charge; not an independent experimental data set',
        'verification_assertions':checks,
        'limitations':['Synthetic generator has two traps by construction; selecting two traps does not demonstrate discrete material defects',
            'Readout response is a single-pole RC model; physical instrument responses must be measured separately',
            'Specified noise covariance is known during fitting; real noise must be estimated from replicate measurements',
            'The continuous alternative is a unimodal lognormal tau distribution with coupled capture scales, not every possible distributed model',
            'Nonlinear bounds and finite sampling may impair parameter identifiability',
            'No measured ALON/Si charge traps, absolute current or validated tunneling constants',
            'No DFT, device fabrication, field qualification, breakdown or nonvolatile retention evidence'],
        'next_experiment':'Acquire bias-dependent time-domain charge or CV/Gw data with independent instrument calibration and separately measured noise; blind fit and hold out pulse widths.'
    }
    (ROOT/'aion-v14-results.json').write_text(json.dumps(report,indent=2))
    print(json.dumps({'protocols':results,'total_observations':len(measures),'fit_runs':len(fitrows),'assertions':checks},indent=2))
    return report

if __name__=='__main__':run()
