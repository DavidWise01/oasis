"""BIFROST V8: twin observers, deterministic receipt reconciliation (simulation)."""
import hashlib,json
from decimal import Decimal
ENVELOPE="[bifrost(d<| -+5{0}S+- |>d)]"
EDGES=[(i,i+1) for a,b in ((122,125),(140,145),(360,366)) for i in range(a,b)]
def canonical(x): return json.dumps(x,sort_keys=True,separators=(',',':'))
def hashof(x): return hashlib.sha256(canonical(x).encode()).hexdigest()
def propose(seq,prev,amount,observer):
    a,b=EDGES[seq]
    core={"envelope":ENVELOPE,"seq":seq,"src":a,"dst":b,"amount":str(amount),"prev":prev,"origin":"0vwxyz"}
    return {**core,"observer":observer,"digest":hashof(core)}
def run():
    balance={n:Decimal(100) for n in range(1,367)}
    chain=[];prev="0"*64
    for i,(a,b) in enumerate(EDGES):
        amount=balance[a]*Decimal("0.025")
        left=propose(i,prev,amount,"d-left")
        right=propose(i,prev,amount,"d-right")
        assert left["digest"]==right["digest"]
        assert hashof({k:v for k,v in left.items() if k not in ("observer","digest")})==left["digest"]
        chain.append(left)
        balance[a]-=amount;balance[b]+=amount;prev=left["digest"]
    assert len(chain)==14
    assert sum(balance.values())==Decimal(36600)
    assert len({x["digest"] for x in chain})==14
    last=chain[-1]
    assert propose(13,last["prev"],Decimal(last["amount"]),"d-right")["digest"]==last["digest"]
    assert propose(13,last["prev"],Decimal(last["amount"])+1,"d-right")["digest"]!=last["digest"]
    assert all(chain[i]["prev"]==chain[i-1]["digest"] for i in range(1,14))
    assert len(ENVELOPE)>0 and ENVELOPE=="[bifrost(d<| -+5{0}S+- |>d)]"
    return {"status":"PASS","checks":8,"receipts":14,"observers":2,"balances":"36600","root":"0vwxyz","envelope":ENVELOPE,"head":prev,"limitations":"two simulated observers on same ordered stream; no distributed consensus or live network"}
if __name__=="__main__":print(json.dumps(run(),indent=2))
