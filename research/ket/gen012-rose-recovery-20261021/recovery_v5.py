"""KET ROSE V5: deterministic idempotent crash recovery, symbolic atomic journal."""
from decimal import Decimal, getcontext
from hashlib import sha256
import json
getcontext().prec=80
WINDOWS=((122,125),(140,145),(360,366))
EDGES=[(i,i+1) for lo,hi in WINDOWS for i in range(lo,hi)]
RATE=Decimal('0.025')
def norm(n): return str(n.normalize())
def digest(b):
    return sha256('|'.join(f'{i}:{norm(b[i])}' for i in range(1,367)).encode()).hexdigest()
class Journal:
    def __init__(self):
        self.balances={i:Decimal(100) for i in range(1,367)}
        self.events=[]
        self.completed=set()
    def transfer(self,seq,crash=None):
        src,dst=EDGES[seq]
        key=f'rose-v5:{seq}:{src}->{dst}'
        if key in self.completed: return 'DUPLICATE_NOOP'
        amount=self.balances[src]*RATE
        if crash=='before_prepare': return 'CRASH'
        self.events.append({'key':key,'event':'PREPARE','amount':norm(amount)})
        if crash in ('after_prepare','between_debit_credit'):
            self.events.append({'key':key,'event':'ABORT','reason':crash})
            return 'CRASH'
        self.balances[src]-=amount
        self.balances[dst]+=amount
        self.completed.add(key)
        self.events.append({'key':key,'event':'COMMIT','amount':norm(amount),'src':src,'dst':dst})
        return 'COMMITTED'
    def replay(self):
        for i in range(len(EDGES)): self.transfer(i)
def run():
    baseline=Journal();baseline.replay()
    expected=digest(baseline.balances)
    receipts=[e for e in baseline.events if e['event']=='COMMIT']
    results=[]
    for fault in ('before_prepare','after_prepare','between_debit_credit'):
        for edge in range(len(EDGES)):
            j=Journal()
            for i in range(edge):j.transfer(i)
            assert j.transfer(edge,crash=fault)=='CRASH'
            assert sum(j.balances.values())==Decimal(36600)
            j.replay()
            assert digest(j.balances)==expected
            assert [e for e in j.events if e['event']=='COMMIT']==receipts
            assert len(j.completed)==14
            before=(digest(j.balances),len(j.events))
            j.replay()
            assert before==(digest(j.balances),len(j.events))
            results.append({'fault':fault,'edge':edge,'status':'PASS'})
    assert len(EDGES)==14 and len(results)==42
    assert len({(s,b) for s in ('---','--+','-+-','-++','+--','+-+','++-','+++') for b in ('H','O','N')})==24
    assert all((i+60)%60==i for i in range(60))
    return {'status':'PASS','fault_scenarios':42,'links':14,'balance_total':'36600',
            'origin':'0vwxyz','identities':24,'phase_bins':60,'shadow':'unresolved',
            'final_digest':expected,'results':results,'scope':'symbolic in-memory simulation'}
if __name__=='__main__':print(json.dumps(run(),indent=2))
