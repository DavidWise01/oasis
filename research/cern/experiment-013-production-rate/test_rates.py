"""CERN Experiment 013: benchmark event yield arithmetic, not production predictions."""
import math
import json
L_FB=138.0
BR=0.25
EFF=0.10
def n_events(sigma_pb, luminosity_fb=L_FB, branching=BR, efficiency=EFF):
    if min(sigma_pb,luminosity_fb,branching,efficiency)<0 or branching>1 or efficiency>1:
        raise ValueError("bad parameter")
    return 1000*sigma_pb*luminosity_fb*branching*efficiency
assert n_events(.1)==345
assert n_events(.001)==3.45
assert n_events(0)==0
assert n_events(.1,efficiency=0)==0
assert math.isclose(n_events(.3)/n_events(.1),3)
try:
    n_events(.1,branching=1.2)
    raise AssertionError("missing validation")
except ValueError:
    pass
assert math.isclose(n_events(.1)/(.25*.1),13800)
rows=[{"sigma_pb":s,"N_produced":1000*L_FB*s,"N_selected_tH":n_events(s)} for s in [0,.001,.01,.03,.1,.3,1]]
print(json.dumps(rows,indent=2))
print("7/7 arithmetic assertions passed; no cross-section predicted.")
