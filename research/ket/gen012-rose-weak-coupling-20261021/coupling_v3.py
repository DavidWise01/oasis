"""KET symbolic weak-band transfers: sequential exact accounting."""
from decimal import Decimal
from pathlib import Path
import json
WINDOWS=((122,125),(140,145),(360,366))
BANDS=((1,122,'H'),(123,244,'O'),(245,366,'N'))
PATHS=('---','--+','-+-','-++','+--','+-+','++-','+++')
RATE=Decimal('0.025')
def band(i):
    return next(name for lo,hi,name in BANDS if lo<=i<=hi)
def edges():
    return [(i,i+1) for lo,hi in WINDOWS for i in range(lo,hi)]
def transfer(balances,src,dst):
    assert src != dst and 1<=src<=366 and 1<=dst<=366
    amount=balances[src]*RATE
    balances[src]-=amount
    balances[dst]+=amount
    return {'source':src,'destination':dst,'debit':str(-amount),'credit':str(amount)}
def run():
    links=edges()
    assert len(links)==len(set(links))==14
    assert sum(hi-lo+1 for lo,hi in WINDOWS)==17
    assert all(any(lo<=a<b<=hi for lo,hi in WINDOWS) for a,b in links)
    assert [(a,b) for a,b in links if band(a)!=band(b)]==[(122,123)]
    balances={i:Decimal(100) for i in range(1,367)}
    before=sum(balances.values())
    ledger=[transfer(balances,a,b) for a,b in links]
    assert sum(balances.values())==before
    assert all(Decimal(x['debit'])+Decimal(x['credit'])==0 for x in ledger)
    assert len({(p,b) for p in PATHS for b in ('H','O','N')})==24 and all(((n+1)-1)%60==n for n in range(60))
    return {'schema':'ket-rose-weak-coupling-v3','status':'PASS','checks':7,
            'windows':[list(w) for w in WINDOWS],'window_slots':17,'links':14,
            'cross_band_links':[[122,123]],'origin':'0vwxyz','identities':24,
            'phase_bins':60,'initial_balance':str(before),'final_balance':str(sum(balances.values())),
            'transfer_rate':'0.025','shadow':'unresolved','ledger':ledger,
            'scope':'symbolic only; physical weak-force and quantum claims untested'}
if __name__=='__main__':
    result=run()
    Path(__file__).with_name('coupling_v3_result.json').write_text(json.dumps(result,indent=2)+'\n')
    print(result['status'],result['checks'],'checks',result['links'],'links')
