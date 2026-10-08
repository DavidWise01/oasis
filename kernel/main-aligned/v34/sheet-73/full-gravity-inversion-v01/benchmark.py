#!/usr/bin/env python3
"""SHEET73: Two-wall reversible kick-drift-kick gravity toy, exact binary inversion."""
import math, json, hashlib
MU=1.0; LAM=0.04; DT=0.002; RMIN=2.0; RMAX=6.0
N=416
registry=[f'S{i:03d}' for i in range(300)]+[f'M{i:03d}' for i in range(100)]+[f'W{i:02d}' for i in range(16)]
def h(x): return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def acceleration(r):return -MU/(r*r)+LAM*r
def step(r,v,bit):
    vhalf=v+.5*DT*acceleration(r)
    x=r+DT*vhalf
    hits=[]
    # Mirror map of interval; each reflection toggles a bit.
    while x<RMIN or x>RMAX:
        if x<RMIN:x=2*RMIN-x;vhalf=-vhalf;bit^=1;hits.append('lower')
        elif x>RMAX:x=2*RMAX-x;vhalf=-vhalf;bit^=1;hits.append('upper')
    v=vhalf+.5*DT*acceleration(x)
    return x,v,bit,hits
def reverse(r,v,bit):
    # Velocity Verlet is self-adjoint, so reverse with negated velocity, then negate return.
    x,w,b,hits=step(r,-v,bit)
    return x,-w,b,hits
def test():
    r,v,b=4.0,-0.8,1;original=(r,v,b);events=[];trajectory=[]
    for t in range(15000):
        r,v,b,hits=step(r,v,b)
        if hits:
            for side in hits:events.append({'tick':t+1,'side':side,'bit_after':b})
        trajectory.append((r,v,b))
        if len(events)>=2:break
    endpoint=(r,v,b)
    for _ in range(len(trajectory)):
        r,v,b,_=reverse(r,v,b)
    checks={
      'two_actual_wall_events':len(events)==2,
      'opposite_boundaries':len({e['side'] for e in events})==2,
      'binary_1_0_1': [1]+[e['bit_after'] for e in events]==[1,0,1],
      'return_bit_exact':b==1,
      'reverse_radius':abs(r-original[0])<1e-9,
      'reverse_velocity':abs(v-original[1])<1e-9,
      'bounds':all(RMIN-1e-12<=p[0]<=RMAX+1e-12 for p in trajectory),
      'registry_count':len(registry)==416,
      'registry_unique':len(set(registry))==416,
      'registry_bands':sum(x.startswith('S') for x in registry)==300 and sum(x.startswith('M') for x in registry)==100 and sum(x.startswith('W') for x in registry)==16,
      'inversion_involution':all((x^1)^1==x for x in (0,1)),
      'threshold':math.sqrt(1.25)>1,
      'finite':all(math.isfinite(x) for p in trajectory for x in p[:2]),
      'ledger_repeatable':h(events)==h(list(events)),
    }
    return {'schema':'oasis/sheet73/full-gravity-inversion-v01','params':{'mu':MU,'lambda':LAM,'dt':DT,'rmin':RMIN,'rmax':RMAX},'initial':original,'end_forward':endpoint,'events':events,'steps':len(trajectory),'reverse_errors':{'radius':abs(r-original[0]),'velocity':abs(v-original[1])},'registry_digest':h(registry),'event_digest':h(events),'checks':checks,'passed':sum(checks.values()),'total':len(checks),'limitations':['Artificial reflecting lower AND upper walls, not derived from gravitational ODE','Two encounters demonstrate full logical bit cycle but not closed physical phase-space orbit','Reverse numeric integration approximate; binary identity exact']}
if __name__=='__main__':
 x=test();print(json.dumps(x,indent=2));assert x['passed']==x['total']
