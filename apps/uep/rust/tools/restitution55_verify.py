"""RESTITUTION-55 independent fixed-scenario JSONL verifier. .dlw"""
import hashlib
import json
import struct
import sys

def require(ok, msg):
    if not ok:
        raise ValueError(msg)

def digest(b):
    return hashlib.sha256(b).digest()

def pack(values):
    return struct.pack(">" + "Q"*len(values), *values)

def verify(lines):
    require(len(lines)==362, "record count")
    root=[6]+[90]*4+[80]*4+[70]*4+[6,17,400,326,15]
    h=digest(b"RESTITUTION54/GENESIS/v1"+pack(root))
    require(lines[0]=={"type":"genesis","digest":h.hex()}, "genesis")
    s=root
    p=[20,20,400,10,1,1000]
    for i,row in enumerate(lines[1:-1]):
        stock=[]; unmet=[]
        for k,v in enumerate(s[1:13]):
            available=min(100,v+p[0]+(s[17] if k==0 else 0))
            delivered=min(p[1],max(0,available-5))
            stock.append(available-delivered)
            unmet.append(p[1]-delivered)
        due=s[13]*100
        paid=min(due,p[2])
        back=min(s[15],p[2]-paid)
        t=[s[0]+1]+stock+[s[13],s[14]+p[4],s[15]-back+due-paid,s[16]+p[3],s[17]-(s[17]*p[5]+9999)//10000]
        b=pack([i]+p+s+t+[due,paid,back]+unmet)
        require(len(b)==464,"payload width")
        nxt=digest(b"RESTITUTION54/ROW/v1"+h+b)
        require(row=={"type":"row","index":i,"previous":h.hex(),"payload":b.hex(),"digest":nxt.hex()},f"row {i}")
        h=nxt;s=t
    require(lines[-1]=={"type":"terminal","count":360,"digest":h.hex(),"actual_transactions":0},"terminal")
    return {"status":"PASS","count":360,"digest":h.hex(),"terminal_state":s}

if __name__=="__main__":
    with open(sys.argv[1],encoding="utf-8") as f:
        rows=[json.loads(line) for line in f]
    print(json.dumps(verify(rows),sort_keys=True))
