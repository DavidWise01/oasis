"""SAPPHON U03 deterministic hash-linked, append-only ledger.
Provisional typed operators X/D/D_INV only; not canonical 42-operator physics.
"""
import hashlib,json
from fractions import Fraction as F
from dataclasses import dataclass

ROOT='0'*64
class LedgerError(ValueError):pass

def encode(state):return [[v.numerator,v.denominator] for v in state]
def decode(data):return tuple(F(a,b) for a,b in data)
def digest(obj):return hashlib.sha256(json.dumps(obj,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def apply(op,state):
    if op=='X':return state[::-1]
    if op=='D':return (state[0]*2,state[1])
    if op=='D_INV':return (state[0]/2,state[1])
    raise LedgerError('unresolved operator: '+op)

@dataclass(frozen=True)
class Ledger:
    initial:tuple
    events:tuple=()
    def state(self):return decode(self.events[-1]['after']) if self.events else self.initial
    def append(self,ops):
        # Atomic: all ops validated and evaluated before any new Ledger is built.
        current=self.state(); prepared=[]
        for op in ops:
            nxt=apply(op,current)
            prepared.append((op,current,nxt));current=nxt
        chain=list(self.events)
        for op,before,after in prepared:
            payload={'seq':len(chain),'op':op,'before':encode(before),'after':encode(after),'prev':chain[-1]['hash'] if chain else ROOT}
            chain.append({**payload,'hash':digest(payload)})
        return Ledger(self.initial,tuple(chain))
    def verify(self):
        previous=ROOT;state=self.initial
        for i,e in enumerate(self.events):
            payload={k:v for k,v in e.items() if k!='hash'}
            if e['seq']!=i or e['prev']!=previous or e['before']!=encode(state) or digest(payload)!=e['hash']:
                raise LedgerError('history mismatch at event '+str(i))
            state=apply(e['op'],state)
            if e['after']!=encode(state):raise LedgerError('transition mismatch at event '+str(i))
            previous=e['hash']
        return state

def tests():
    original=Ledger((F(3,4),F(3,8)))
    a=original.append(('D','X','X','D_INV'))
    b=original.append(('D','X','X','D_INV'))
    checks={
        'replay exact':a.verify()==original.initial,
        'deterministic hash chain':a.events==b.events,
        'four ordered events':len(a.events)==4,
        'parent unchanged':len(original.events)==0,
        'link chain':all(e['prev']==(a.events[i-1]['hash'] if i else ROOT) for i,e in enumerate(a.events)),
        'all hashes match':all(e['hash']==digest({k:v for k,v in e.items() if k!='hash'}) for e in a.events),
        'zero fixed':Ledger((F(0),F(0))).append(('D','X')).verify()==(F(0),F(0)),
        'exact rational restoration':a.state()==original.initial,
    }
    for label,change in [
        ('tampered payload rejected',{'after':[[99,1],[3,8]]}),
        ('tampered previous hash rejected',{'prev':'f'*64}),
        ('tampered operation rejected',{'op':'X'}),
    ]:
        ev=[dict(e) for e in a.events];ev[0].update(change)
        try:Ledger(a.initial,tuple(ev)).verify();checks[label]=False
        except LedgerError:checks[label]=True
    try:original.append(('X','pending_01','D'));checks['failed batch atomic']=False
    except LedgerError:checks['failed batch atomic']=original.events==()
    for k,v in checks.items():print(('PASS' if v else 'FAIL'),k)
    print(f'RESULT {sum(checks.values())}/{len(checks)}')
    assert all(checks.values())
if __name__=='__main__':tests()
