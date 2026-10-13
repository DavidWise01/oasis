#!/usr/bin/env python3
"""KET v2.0 compact executable demonstration: --+ ++- in a toroidal non-universe.

Not a physical cosmology model. 360 surface samples + 3 slow + 3 fast
register slots. Six controller addresses are read twice, not replicated.
"""
from fractions import Fraction
import json

SLOW="--+"
FAST="++-"
FIRST=SLOW+FAST
SECOND=FAST+SLOW
CHILDREN=("red","green","blue","orange","purple","green","yellow")
CARRIERS=("white","black","gray")
GREEN_CHARIOT=r"123 {{45/|\54}} 678"
RATE=Fraction(1,1)
DELTA=Fraction(1,10)       # demonstration only, NOT immutable KET constant
ADDRESSES=list(range(360,366))

def execute(word):
    v=RATE
    angle=Fraction(0)
    rates=[]
    for char in word:
        assert char in "+-"
        v+=DELTA * (+1 if char=="+" else -1)
        angle+=v
        rates.append(v)
    return v,angle,rates

def main():
    v1,angle1,rates1=execute(FIRST)
    v2,angle2,rates2=execute(SECOND)
    checks={
       "toroid_vertices":20*18==360,
       "toroid_edges":2*360==720,
       "toroid_faces":360==360,
       "euler_zero":360-720+360==0,
       "six_controls":len(ADDRESSES)==6,
       "total_addresses":360+len(ADDRESSES)==366,
       "slow_literal":SLOW=="--+",
       "fast_literal":FAST=="++-",
       "first_literal":FIRST=="--+++-",
       "second_literal":SECOND=="++---+",
       "first_signed_balance":FIRST.count("+")==FIRST.count("-"),
       "second_signed_balance":SECOND.count("+")==SECOND.count("-"),
       "first_restores_speed":v1==RATE,
       "second_restores_speed":v2==RATE,
       "first_phase_lag":angle1==Fraction(57,10),
       "second_phase_lead":angle2==Fraction(63,10),
       "sum_angles_twelve":angle1+angle2==12,
       "full_cycle_angle":angle1+angle2+348*RATE==360,
       "same_control_addresses_reused":len(ADDRESSES)==6,
       "green_twice":CHILDREN[1]==CHILDREN[5]=="green",
       "seven_amplitudes":len(CHILDREN)==7,
       "three_carriers":len(CARRIERS)==3,
       "literal_chariot":GREEN_CHARIOT==r"123 {{45/|\54}} 678",
    }
    assert all(checks.values()),[key for key,value in checks.items() if not value]
    result={
       "checks_passed":len(checks),
       "controls_slow":SLOW,"controls_fast":FAST,
       "demo_base_deg_per_tick":str(RATE),
       "demo_delta_deg_per_tick":str(DELTA),
       "first_six_rate":[str(x) for x in rates1],
       "second_six_rate":[str(x) for x in rates2],
       "first_six_angle_deg":str(angle1),
       "second_six_angle_deg":str(angle2),
       "full_360_tick_angle_deg":str(angle1+angle2+348*RATE),
       "control_addresses":ADDRESSES,
       "note":"Toy speed/phase schedule, not an astrophysical discovery."
    }
    print(json.dumps(result,indent=2))
if __name__=="__main__":main()
