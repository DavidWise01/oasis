"""RESTITUTION-56: adversarial fixed-history qualification. .dlw"""
import copy, json, sys, hashlib
from restitution55_verify import verify

def rehash(rows):
    h=bytes.fromhex(rows[0]["digest"])
    for row in rows[1:-1]:
        row["previous"]=h.hex()
        h=hashlib.sha256(b"RESTITUTION54/ROW/v1"+h+bytes.fromhex(row["payload"])).digest()
        row["digest"]=h.hex()
    rows[-1]["digest"]=h.hex()

def qualify(rows):
    result=verify(rows)
    cases={}
    def reject(name, mutate):
        trial=copy.deepcopy(rows)
        mutate(trial)
        try:
            verify(trial)
        except ValueError:
            cases[name]="REJECTED"
        else:
            raise RuntimeError("accepted adversarial history: "+name)
    reject("truncation",lambda x:x.pop(180))
    reject("duplicate",lambda x:x.insert(180,copy.deepcopy(x[179])))
    reject("reordering",lambda x:x.__setitem__(slice(1,3),[x[2],x[1]]))
    reject("forged_predecessor",lambda x:x[180].update(previous="00"*32))
    reject("forged_terminal",lambda x:x[-1].update(digest="00"*32))
    reject("false_transaction_count",lambda x:x[-1].update(actual_transactions=1))
    reject("forged_genesis",lambda x:x[0].update(digest="00"*32))
    for field,index in [("input",1),("opening_arrears",22),("closing_arrears",40),("current_payment",44),("unmet_resource",46)]:
        def mutate(x,index=index):
            b=bytearray.fromhex(x[180]["payload"])
            b[index*8+7]^=1
            x[180]["payload"]=b.hex()
            rehash(x)
        reject("fully_rehashed_"+field,mutate)
    return {"status":"PASS","terminal_digest":result["digest"],"rejected":len(cases),"cases":cases}

if __name__=="__main__":
    with open(sys.argv[1],encoding="utf-8") as f:
        rows=[json.loads(line) for line in f]
    print(json.dumps(qualify(rows),sort_keys=True))
