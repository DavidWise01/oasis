#!/usr/bin/env python3
"""AETHER-145 original failure: self-consistent forged reference. Preserved.
Execute the exact locally tested original from aether145-evidence.zip.
"""
import json
def first_contract(dut,reference,limit=.025):
    return bool(dut.get('signed') and reference.get('signed') and
                dut['reported']==reference['measured'] and reference['measured']<=limit)
if __name__=='__main__':
    a=dict(signed=True,reported=.005)
    b=dict(signed=True,measured=.005)
    print(json.dumps(dict(bound='AETHER-145',status='FAIL',
      fabricated_reference_passes=first_contract(a,b),
      real_risk=.045,unsafe_action=first_contract(a,b) and .045>.025,
      note='Signed agreement alone is circular and cannot prove reference accuracy')))
