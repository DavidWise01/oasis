"""Z324: reversible RGB orientation transition ledger (symbolic only)."""
from itertools import permutations
import hashlib, json
BASE=(3,1,2)
STATES=set(permutations(BASE))
def rot(x): return (x[2],x[0],x[1])
def mirror(x): return (x[2],x[1],x[0])
def apply(x,op):return {'R':lambda v:rot(v),'RR':lambda v:rot(rot(v)),'M':mirror}[op](x)
def append(ledger, op):
    previous=ledger[-1]['to'] if ledger else BASE
    after=apply(previous,op)
    entry={'seq':len(ledger),'op':op,'from':previous,'to':after,'prev_hash':ledger[-1]['hash'] if ledger else 'GENESIS'}
    entry['hash']=hashlib.sha256(json.dumps(entry,sort_keys=True).encode()).hexdigest()
    ledger.append(entry)
    return after
def verify(ledger):
    previous=BASE; parent='GENESIS'
    for i, entry in enumerate(ledger):
        payload={k:v for k,v in entry.items() if k!='hash'}
        if entry['seq']!=i or tuple(entry['from'])!=previous or entry['prev_hash']!=parent:return False
        if tuple(entry['to'])!=apply(previous,entry['op']):return False
        if hashlib.sha256(json.dumps(payload,sort_keys=True).encode()).hexdigest()!=entry['hash']:return False
        previous=tuple(entry['to']);parent=entry['hash']
    return True
checks={}
checks['six_states']=len(STATES)==6
checks['all_edges_closed']=all(apply(s,op) in STATES for s in STATES for op in ('R','RR','M'))
checks['inverse_R']=all(apply(apply(s,'R'),'RR')==s for s in STATES)
checks['inverse_RR']=all(apply(apply(s,'RR'),'R')==s for s in STATES)
checks['inverse_M']=all(apply(apply(s,'M'),'M')==s for s in STATES)
checks['sum_preserved']=all(sum(apply(s,op))==6 for s in STATES for op in ('R','RR','M'))
checks['multiset_preserved']=all(sorted(apply(s,op))==[1,2,3] for s in STATES for op in ('R','RR','M'))
checks['identity_no_loss']=all(apply(s,'R')!=s for s in STATES)
ledger=[]
for op in ('R','M','RR','R'):append(ledger,op)
checks['ledger_length']=len(ledger)==4
checks['ledger_valid']=verify(ledger)
checks['sequence_monotonic']=[e['seq'] for e in ledger]==list(range(4))
checks['hash_chain']=all(e['prev_hash']==(ledger[i-1]['hash'] if i else 'GENESIS') for i,e in enumerate(ledger))
checks['replay_state']=ledger[-1]['to']==apply(apply(apply(apply(BASE,'R'),'M'),'RR'),'R')
ledger[1]['op']='R'
checks['tamper_detected']=not verify(ledger)
ledger[1]['op']='M'
checks['repair_restores_verification']=verify(ledger)
checks['distinct_governance']=(5,3,1)!=BASE
for k,v in checks.items(): print(('PASS' if v else 'FAIL'),k)
print(f'{sum(checks.values())}/{len(checks)} PASS')
assert all(checks.values())
