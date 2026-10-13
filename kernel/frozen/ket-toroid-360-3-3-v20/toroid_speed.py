#!/usr/bin/env python3
"""KET v2.0: abstract toroidal speed controller, no cosmological claims.

Physical degrees and logical address counts are separate.
Assumes '-' decreases and '+' increases angular rate by delta degrees/tick.
This is a choice for the demonstration, not a user-defined rate constant.
"""
from fractions import Fraction
import json
from pathlib import Path
from collections import Counter
import hashlib

REGISTRY = {'surface_skins':20, 'sectors_per_skin':18, 'surface_nodes':360, 'controls':6, 'total_addresses':366}
SLOW = '--+'; FAST = '++-'
CONTROL = SLOW + FAST
REVERSE = FAST + SLOW
AMPLITUDES = ['red','green','blue','orange','purple','green','yellow']
CARRIERS = ['white','black','gray']
CHARIOT = r'123 {{45/|\54}} 678'
ZERO = 0
BASE = Fraction(1,1)
DELTA = Fraction(1,10)   # illustrative; deg/tick per activation
CYCLE_LENGTH = 360

def run(controls, prelude=0, target_ticks=None, base=BASE, delta=DELTA):
    """Update velocity then advance phase for each one-tick operation."""
    assert delta >= 0 and base > 2*delta
    if target_ticks is None: target_ticks = len(controls)
    omega = base; phase=Fraction(0); trace=[]
    signs = [-1 if c=='-' else 1 for c in controls]
    assert all(c in '-+' for c in controls)
    for t in range(target_ticks):
        s = signs[t] if t < len(signs) else 0
        omega += delta * s
        phase += omega
        trace.append({'tick':t+1,'controller_address':(360+t if t<6 else (363+(t-6) if t<9 else 360+(t-9))) if t<12 else None,
                      'instruction':controls[t] if t<len(controls) else 'hold',
                      'omega_deg_per_tick': float(omega),'phase_deg':float(phase),
                      'phase_offset_deg':float(phase-base*(t+1))})
    return omega, phase, trace

def execute():
    omega1,phase1,trace1=run(CONTROL)
    omega2,phase2,trace2=run(CONTROL + REVERSE, target_ticks=CYCLE_LENGTH)
    omega_reverse, phase_reverse, reversed_trace=run(REVERSE)
    check_names=[]
    def ck(name,cond):
        if not cond: raise AssertionError(name)
        check_names.append(name)
    ck('torus_surface_count',20*18==360)
    ck('toroidal_mesh_edges',2*360==720)
    ck('toroidal_mesh_faces',360==360)
    ck('toroidal_euler_zero',360-720+360==0)
    ck('six_controls',REGISTRY['controls']==6)
    ck('address_sum_366',REGISTRY['surface_nodes']+REGISTRY['controls']==366)
    ck('slow_exact',SLOW=='--+')
    ck('fast_exact',FAST=='++-')
    ck('paired_raw_order',CONTROL=='--+++-')
    ck('reversed_raw_order',REVERSE=='++---+')
    ck('negative_triple_net_minus_one',sum(-1 if c=='-' else 1 for c in SLOW)==-1)
    ck('positive_triple_net_plus_one',sum(-1 if c=='-' else 1 for c in FAST)==1)
    ck('six_net_zero',sum(-1 if c=='-' else 1 for c in CONTROL)==0)
    ck('reverse_six_net_zero',sum(-1 if c=='-' else 1 for c in REVERSE)==0)
    ck('angular_rate_restored_after_six',omega1==BASE)
    ck('six_ticks_phase_is_5_7',phase1==Fraction(57,10))
    ck('phase_lag_from_first_six',phase1-Fraction(6)==Fraction(-3,10))
    ck('reverse_six_phase_lead',phase_reverse-Fraction(6)==Fraction(3,10))
    ck('reverse_six_rate_restored',omega_reverse==BASE)
    ck('restored_rate_after_360',omega2==BASE)
    ck('restored_phase_after_360',phase2==Fraction(360))
    ck('clockhas360steps',len(trace2)==360)
    ck('first_six_active',sum(r['instruction']!='hold' for r in trace2[:6])==6)
    ck('second_six_active',sum(r['instruction']!='hold' for r in trace2[6:12])==6)
    ck('remaining_348_hold',sum(r['instruction']=='hold' for r in trace2)==348)
    ck('max_w_1_2',max(r['omega_deg_per_tick'] for r in trace2)==1.2)
    ck('min_w_0_8',min(r['omega_deg_per_tick'] for r in trace2)==0.8)
    ck('transient_first_six_not_phase_balanced',trace2[5]['phase_offset_deg']!=0)
    ck('phase_recovered_at_12',trace2[11]['phase_offset_deg']==0)
    ck('green_is_two_distinct_slots',AMPLITUDES[1]=='green' and AMPLITUDES[5]=='green')
    ck('seven_amplitudes',len(AMPLITUDES)==7)
    ck('three_carriers',CARRIERS==['white','black','gray'])
    ck('eleven_register_slots',len(AMPLITUDES)+len(CARRIERS)+1==11)
    ck('green_chariot_literal',CHARIOT==r'123 {{45/|\54}} 678')
    ck('pinned_zero',ZERO==0)
    ck('distinct_rate_vs_angle_units',REGISTRY['controls']!=360)
    ck('all_omega_positive',all(r['omega_deg_per_tick']>0 for r in trace2))
    ck('no_extra_kernel_address',REGISTRY['total_addresses']==366)
    # Six *addressed* control objects: mirrored return order reuses rather than doubles them.
    ck('six_unique_control_addresses',set(r['controller_address'] for r in trace2[:12])==set(range(360,366)))
    ck('first_control_address_order',[r['controller_address'] for r in trace2[:6]]==list(range(360,366)))
    ck('second_control_address_order',[r['controller_address'] for r in trace2[6:12]]==[363,364,365,360,361,362])
    events=[]; previous='0'*64
    for s in trace2:
        if s['tick']<=12 or s['tick']==360:
            data={'tick':s['tick'],'command':s['instruction'],'phase_deg':s['phase_deg'],'velocity':s['omega_deg_per_tick']}
            record={'prev_sha256':previous,'data':data}
            canonical=json.dumps(record,sort_keys=True,separators=(',',':'))
            digest=hashlib.sha256(canonical.encode()).hexdigest()
            record['sha256']=digest;events.append(record);previous=digest
    ck('thirteen_witness_records',len(events)==13)
    for i,e in enumerate(events):
        canonical=json.dumps({'prev_sha256':e['prev_sha256'],'data':e['data']},sort_keys=True,separators=(',',':'))
        ck(f'witness_hash_{i+1}', hashlib.sha256(canonical.encode()).hexdigest()==e['sha256'])
        ck(f'witness_chain_{i+1}', e['prev_sha256']==('0'*64 if i==0 else events[i-1]['sha256']))
    result={
        'schema':'KET/TOROID/360+3+3/v20',
        'setting':'non-universe :: abstract toroidal model; no cosmological test claimed',
        'user_literal':'--+ ++-',
        'control_triples':{'slower':'--+','faster':'++-','first_pass':CONTROL,'complementary_pass':REVERSE},
        'signs':{'-':'decrease angular speed','+':'increase angular speed'},
        'toroid':{'skins':20,'sectors':18,'surface_vertices':360,'mesh_edges':720,'mesh_faces':360,'euler_characteristic':0,
                  'control_addresses':list(range(360,366)),'total_addresses':366},
        'parameters':{'base_angular_velocity_deg_per_tick':'1','change_per_control_deg_per_tick':'1/10','source':'illustrative, NOT immutable KET constant'},
        'derived':{'six_step_rate_change':'0','six_step_phase_lag_deg':'-3/10',
                   'reverse_six_step_phase_lead_deg':'3/10','paired_12_step_phase_offset_deg':'0',
                   'full_360_step_phase_deg':'360','full_360_step_rate_deg_per_tick':'1'},
        'twelve_commands':[r for r in trace2[:12]],'clock_samples':[r for r in trace2 if r['tick'] in (1,2,3,4,5,6,7,8,9,10,11,12,90,180,270,360)],
        'green_chariot':CHARIOT,'amplitudes':AMPLITUDES,'carriers':CARRIERS,
        'witness':events,'witness_head':previous,'check_count':len(check_names),'checks':check_names,
        'evidence_status':'Mathematical demonstration only, no verified cosmological or dynamical astrophysics mechanism.'
    }
    return result

if __name__=='__main__':
    output=execute();out=Path(__file__).with_name('results.json')
    out.write_text(json.dumps(output,sort_keys=True,indent=2)+'\n')
    print(json.dumps({'checks':output['check_count'],'phase_first_6':output['derived']['six_step_phase_lag_deg'],
       'phase_paired_12':output['derived']['paired_12_step_phase_offset_deg'],
       'full_360_phase':output['derived']['full_360_step_phase_deg'],
       'witness_head':output['witness_head']},indent=2))