"""KET Gen0-2 phase motion; symbolic deterministic state machine."""
import json
from pathlib import Path
SIGNS = ('---','--+','-+-','-++','+--','+-+','++-','+++')
BANDS = ('H','O','N')
PHASE_BINS = 60

def advance(state, ticks=1):
    assert state['path'] in SIGNS and state['band'] in BANDS
    assert isinstance(ticks, int)
    result = dict(state)
    result['phase_bin'] = (state['phase_bin'] + ticks) % PHASE_BINS
    result['origin'] = '0vwxyz'
    result['shadow'] = 'unresolved'
    return result

def run():
    states = [{'path': s, 'band': b, 'phase_bin': 0, 'origin': '0vwxyz', 'shadow': 'unresolved'} for s in SIGNS for b in BANDS]
    assert len(states) == len({(s['path'],s['band']) for s in states}) == 24
    assert all(advance(s, 60) == s for s in states)
    assert all(advance(advance(s, 17), -17) == s for s in states)
    assert all(advance(s, 1)['phase_bin'] == 1 for s in states)
    assert all(advance(s, -1)['phase_bin'] == 59 for s in states)
    assert all(advance(s, t)['origin'] == '0vwxyz' and advance(s,t)['shadow'] == 'unresolved' for s in states for t in (-120,-1,0,1,120))
    return {'schema':'ket-gen012-phase-v2','result':'PASS','checks':5,'paths':8,'bands':3,'identities':24,'phase_bins':60,'phase_states':1440,'origin':'0vwxyz','shadow':'unresolved','phase_rule':'(phase_bin + ticks) mod 60','physics_status':'symbolic only'}

if __name__ == '__main__':
    result = run()
    Path(__file__).with_name('phase_v2_result.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result, indent=2))
