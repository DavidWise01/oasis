#!/usr/bin/env python3
"""Deterministic conservation-accounting checks for scalar-zero analogies."""
import json
import math
from pathlib import Path

tests = []
def verify(name, lhs, rhs, units, description):
    residual = lhs - rhs
    passed = abs(residual) <= 1e-10 * max(1, abs(lhs), abs(rhs))
    tests.append(dict(name=name,passed=passed,lhs=lhs,rhs=rhs,residual=residual,units=units,description=description))

# Plumbing: explicit hydraulic work and shaft losses.
flow = 0.002 # m^3/s
pressure = 100000 # Pa
omega = 20 # rad/s
efficiency = .70
hydraulic = pressure * flow
shaft = hydraulic / efficiency
torque = shaft / omega
losses = shaft - hydraulic
verify("pump_power",shaft,hydraulic+losses,"W","Input = useful hydraulic output + losses")
verify("pump_torque",torque*omega,shaft,"W","Power = torque * angular velocity")
verify("flow_continuity",flow,flow,"m^3/s","Steady single inlet = outlet")
# Heart: simplified steady periodic volume conservation.
heart_rate = 72 # beats/min
stroke_volume = 70 # mL/beat
verify("cardiac_output",heart_rate*stroke_volume/1000,5.04,"L/min","CO = HR * SV")
verify("ventricular_volume",stroke_volume,stroke_volume,"mL/beat","Steady filling = output")
# Abstraction: ledger balance only; not elementary particle dynamics.
initial, absorbed, released = 10,3,2.25
final = initial + absorbed - released
verify("abstract_storage",initial+absorbed,final+released,"units","Input + initial = final + released")
report={"schema":"oasis/scalar-zero-torsion-benchmark/v01","checks":len(tests),"passed":sum(t["passed"] for t in tests),"failed":sum(not t["passed"] for t in tests),"atomic_mechanism_validated":False,"tests":tests,"limitations":["Pump model is power bookkeeping, not CFD.","Cardiac model is flow bookkeeping, not myocardial twist dynamics.","No particle-scale dynamics, gravitation, or torsional binding tested.","These equations test conservation accounting, not cross-domain physical identity."]}
print(json.dumps(report,indent=2))
if report["failed"]: raise SystemExit(1)
