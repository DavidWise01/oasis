"""U02: typed composition, fail-closed preflight and immutable execution."""
from dataclasses import dataclass
from fractions import Fraction as F
class ContractError(Exception): pass
@dataclass(frozen=True)
class Operator:
    name: str
    domain: str
    codomain: str
    inverse: str | None
OPS={
    'X':Operator('X','pair','pair','X'),
    'D':Operator('D','pair','pair','D_INV'),
    'D_INV':Operator('D_INV','pair','pair','D'),
    'ENC':Operator('ENC','pair','ledger',None),
}
def preflight(chain,input_type='pair',require_reversible=False):
    kind=input_type
    for name in chain:
        spec=OPS.get(name)
        if spec is None:raise ContractError(f'UNRESOLVED {name}')
        if kind!=spec.domain:raise ContractError(f'TYPE {name}: expected {spec.domain}, got {kind}')
        if require_reversible and (spec.inverse is None or spec.inverse not in OPS):
            raise ContractError(f'NONINVERTIBLE {name}')
        kind=spec.codomain
    return kind
def execute(chain,state,require_reversible=False):
    preflight(chain,require_reversible=require_reversible)
    if not isinstance(state,tuple) or len(state)!=2 or not all(isinstance(v,F) for v in state):
        raise ContractError('INPUT pair[Fraction, Fraction] required')
    events=()
    current=state
    for name in chain:
        if name=='X':current=(current[1],current[0])
        elif name=='D':current=(2*current[0],current[1])
        elif name=='D_INV':current=(current[0]/2,current[1])
        elif name=='ENC':
            events+=((name,current),)
            return current,events
        events+=((name,current),)
    return current,events
def invert(chain):
    preflight(chain,require_reversible=True)
    return tuple(OPS[name].inverse for name in reversed(chain))
def run():
    start=(F(3,4),F(3,8))
    result,ledger=execute(('D','X'),start,True)
    recovered,_=execute(invert(('D','X')),result,True)
    checks={
      'typed compose accepted':preflight(('D','X'))=='pair',
      'typed output reported':preflight(('X','ENC'))=='ledger',
      'operation order encoded':result==(F(3,8),F(3,2)),
      'inverse chain restores exactly':recovered==start,
      'noncommuting orders distinguished':execute(('X','D'),start)[0]!=result,
      'ledger two immutable events':len(ledger)==2 and isinstance(ledger,tuple),
      'start preserved':start==(F(3,4),F(3,8)),
      'root pinned':execute(('D','X'),(F(0),F(0)))[0]==(F(0),F(0)),
    }
    for label,chain,kwargs in [
      ('unresolved rejected',('pending_01',),{}),
      ('type mismatch rejected',('ENC','X'),{}),
      ('noninvertible rejected',('ENC',),{'require_reversible':True}),
    ]:
        try:preflight(chain,**kwargs)
        except ContractError:checks[label]=True
        else:checks[label]=False
    try:execute(('X','pending_01'),start)
    except ContractError:checks['atomic preflight prevents partial execution']=start==(F(3,4),F(3,8))
    else:checks['atomic preflight prevents partial execution']=False
    for name,ok in checks.items():print(('PASS' if ok else 'FAIL'),name)
    print(f'RESULT {sum(checks.values())}/{len(checks)}')
    assert all(checks.values())
if __name__=='__main__':run()
