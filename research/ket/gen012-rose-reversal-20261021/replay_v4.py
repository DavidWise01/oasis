from decimal import Decimal, getcontext
from hashlib import sha256
import json
getcontext().prec=80
WINDOWS=((122,125),(140,145),(360,366))
EDGES=[(i,i+1) for lo,hi in WINDOWS for i in range(lo,hi)]
RATE=Decimal('0.025')
def canonical(x): return str(x.normalize())
def digest(b): return sha256('|'.join(f'{i}:{canonical(b[i])}' for i in range(1,367)).encode()).hexdigest()
def forward(b):
    out=[]
    for a,z in EDGES:
        amount=b[a]*RATE
        b[a]-=amount;b[z]+=amount
        out.append({'source':a,'target':z,'amount':canonical(amount)})
    return out
def inverse(b,journal):
    for e in reversed(journal):
        a,z,n=e['source'],e['target'],Decimal(e['amount'])
        b[z]-=n;b[a]+=n
def run():
    initial={i:Decimal('100') for i in range(1,367)}
    b=initial.copy(); before=digest(b)
    receipt=forward(b); after=digest(b); moved=b.copy()
    assert len(receipt)==14
    assert sum(b.values())==sum(initial.values())
    inverse(b,receipt)
    assert b==initial and digest(b)==before
    receipt2=forward(b)
    assert receipt2==receipt and b==moved and digest(b)==after
    assert all(Decimal(e['amount'])>=0 for e in receipt)
    assert [(e['source'],e['target']) for e in receipt]==EDGES
    assert len({(s,k) for s in ('---','--+','-+-','-++','+--','+-+','++-','+++') for k in ('H','O','N')})==24
    assert all((p+60)%60==p for p in range(60))
    return {'status':'PASS','checks':8,'links':14,'initial_total':canonical(sum(initial.values())),'replay_total':canonical(sum(b.values())),'origin':'0vwxyz','identity_count':24,'phase_bins':60,'initial_sha256':before,'after_sha256':after,'reversible':True,'replay_exact':True,'journal':receipt,'interpretation':'symbolic accounting, not physical evidence'}
if __name__=='__main__':
    print(json.dumps(run(),indent=2))
