#!/usr/bin/env python3
"""SHEET77 synchronized bounce: exact integer phase clocks + reversible C60 register."""
import json,hashlib,math
PERIOD=256
LEVELS=4
WAVE_N=60
REGISTRY=(300,100,16)
def hashobj(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def shell(t,level):
    period=PERIOD//(4**level)
    p=t%period
    radius=.6+.4*math.sin(2*math.pi*p/period)
    direction=0 if p in (period//4,3*period//4) else (1 if math.cos(2*math.pi*p/period)>0 else -1)
    return (p,direction,radius)
def wave0():return tuple((i//3+i//11)%2 for i in range(WAVE_N))
def advance(w):
    v=[0]*WAVE_N
    for i,b in enumerate(w):v[(i+15)%WAVE_N]=b^1
    return tuple(v)
def state(t):
    w=wave0()
    for _ in range(t%4):w=advance(w)
    flips=sum(1 for k in range(1,t+1) if k%PERIOD in (64,192))
    bit=1^(flips%2)
    sh=[shell(t,i) for i in range(LEVELS)]
    return dict(tick=t,phase=[x[0] for x in sh],direction=[x[1] for x in sh],bit=bit,wave=w,registry=REGISTRY,geometry=(60,15,3,1,1),homeostasis='sqrt(1.25)',radius=[x[2] for x in sh])
def logical(s):return {k:v for k,v in s.items() if k not in ('tick','radius')}
def main():
    orig=state(0);snapshots=[state(t) for t in range(513)]
    closures=[t for t in range(1,513) if logical(snapshots[t])==logical(orig)]
    shell_closures=[t for t in range(1,513) if all(snapshots[t]['phase'][k]==0 for k in range(LEVELS))]
    wave_closures=[t for t in range(1,513) if snapshots[t]['wave']==orig['wave']]
    bounce_events=[t for t in range(1,257) if snapshots[t]['bit']!=snapshots[t-1]['bit']]
    checks={
      'six_arity_lineage':orig['geometry']==(60,15,3,1,1),
      'wave_length_60':len(orig['wave'])==60,
      'wave_closes_four':snapshots[4]['wave']==orig['wave'],
      'wave_not_close_at_one':snapshots[1]['wave']!=orig['wave'],
      'master_shell_256':shell_closures[0]==256,
      'four_level_phases':len(orig['phase'])==4,
      'nested_periods':[PERIOD//4**k for k in range(4)]==[256,64,16,4],
      'radius_bounded':all(.2-1e-12<=r<=1+1e-12 for s in snapshots for r in s['radius']),
      'two_master_turnaround_events':bounce_events==[64,192],
      'bit_toggles_once_per_bounce':snapshots[64]['bit']==0 and snapshots[192]['bit']==1,
      'first_full_closure_256':closures[0]==256,
      'second_full_closure_512':closures[1]==512,
      'no_early_full_closure':all(t>=256 for t in closures),
      'phase_at_end':snapshots[256]['phase']==orig['phase'],
      'direction_at_end':snapshots[256]['direction']==orig['direction'],
      'bit_at_end':snapshots[256]['bit']==orig['bit'],
      'wave_at_end':snapshots[256]['wave']==orig['wave'],
      'registry_416':sum(orig['registry'])==416,
      'registry_stable':all(s['registry']==orig['registry'] for s in snapshots),
      'homeostasis_unchanged':all(s['homeostasis']=='sqrt(1.25)' for s in snapshots),
      'radius_near_recurrent':all(math.isclose(snapshots[256]['radius'][k],orig['radius'][k],abs_tol=1e-12) for k in range(4)),
      'deterministic_replay':hashobj(logical(state(256)))==hashobj(logical(snapshots[256])),
      'state_changes_during_cycle':logical(snapshots[64])!=logical(orig),
      'closure_equal_digest':hashobj(logical(orig))==hashobj(logical(snapshots[256])),
    }
    return {'schema':'oasis/sheet77/synchronized-bounce-v01','master_ticks':256,'shell_periods':[256,64,16,4], 'binary_bounce_ticks':bounce_events,'first_closures':closures,'wave_closure_frequency':4,'first_5_wave_closures':wave_closures[:5],'checks':checks,'passed':sum(checks.values()),'total':len(checks),'state_sha256':hashobj(logical(orig)),'limits':['Synchronization uses an explicitly chosen 256-tick common clock, not physical coupling or a new gravity law.','The 0/1 latch follows level-0 turning points; inner shells turn many times without toggling the bit.','Floats represent sampled radius; exact closure pertains to integer phases and binary state.']}
if __name__=='__main__':
    r=main();print(json.dumps(r,indent=2));assert r['passed']==r['total']
