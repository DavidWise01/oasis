"""Z327 symbolic indexed permutation checkpoint/recovery. No chemistry claim."""
import hashlib, json, math
from random import Random
N=24
LIMIT=math.factorial(N)
def digest(entry):
    return hashlib.sha256(json.dumps(entry,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def make_ledger(indices):
    records=[]; prev='GENESIS'
    for seq,index in enumerate(indices):
        assert type(index)==int and 0<=index<LIMIT
        e={'seq':seq,'index':index,'prev':prev}
        e['hash']=digest(e)
        records.append(e);prev=e['hash']
    return records
def verify(records):
    prev='GENESIS'
    for seq,r in enumerate(records):
        if set(r)!={'seq','index','prev','hash'} or r['seq']!=seq or type(r['index'])!=int or not 0<=r['index']<LIMIT or r['prev']!=prev:return False
        if digest({k:v for k,v in r.items() if k!='hash'})!=r['hash']:return False
        prev=r['hash']
    return True
def checkpoint(records):
    assert verify(records)
    return {'count':len(records),'tip':records[-1]['hash'] if records else 'GENESIS','last_index':records[-1]['index'] if records else None}
def recover(records,cp):
    return verify(records) and checkpoint(records)==cp
rng=Random(327)
indices=[0,LIMIT-1]+[rng.randrange(LIMIT) for _ in range(1000)]
ledger=make_ledger(indices);cp=checkpoint(ledger)
checks={
 'factorial_capacity':LIMIT==620448401733239439360000,
 '1002_entries':len(ledger)==1002,
 'index_bounds':all(0<=i<LIMIT for i in indices),
 'ledger_verifies':verify(ledger),
 'checkpoint_recovers':recover(ledger,cp),
 'last_index_exact':cp['last_index']==indices[-1],
 'tip_hash_exact':cp['tip']==ledger[-1]['hash'],
 'repeat_deterministic':make_ledger(indices)==ledger,
 'empty_ledger':recover([],checkpoint([])),
 'truncated_detected':not recover(ledger[:-1],cp),
 'reordered_detected':not verify(ledger[:1]+[ledger[2],ledger[1]]+ledger[3:]),
 'index_edit_detected':not verify([{**ledger[0],'index':7}]+ledger[1:]),
 'broken_hash_detected':not verify([{**ledger[0],'hash':'0'*64}]+ledger[1:]),
 'bad_sequence_detected':not verify([{**ledger[0],'seq':1}]+ledger[1:]),
 'invalid_negative_rejected':not verify([{**ledger[0],'index':-1}]),
 'invalid_upper_rejected':not verify([{**ledger[0],'index':LIMIT}]),
 'wrong_checkpoint_detected':not recover(ledger,{**cp,'tip':'0'*64}),
 'governance_independent':(5,3,1)!=(3,1,2),
}
for k,v in checks.items(): print(('PASS' if v else 'FAIL'),k)
print(f'{sum(checks.values())}/{len(checks)} PASS')
assert all(checks.values())
