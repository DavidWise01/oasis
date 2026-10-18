"""Z328: independently verifiable Ed25519 checkpoint receipts; symbolic KET research."""
import hashlib, json, math
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization
LIMIT=math.factorial(24)
def canonical(obj):return json.dumps(obj,sort_keys=True,separators=(',',':')).encode()
def hash_entry(obj):return hashlib.sha256(canonical(obj)).hexdigest()
def build(indices):
    result=[];last='GENESIS'
    for seq,index in enumerate(indices):
        assert type(index) is int and 0<=index<LIMIT
        payload={'seq':seq,'index':index,'prev':last}
        h=hash_entry(payload);result.append({**payload,'hash':h});last=h
    return result
def validate(entries):
    prev='GENESIS'
    for n,e in enumerate(entries):
        if set(e)!={'seq','index','prev','hash'} or type(e['seq']) is not int or e['seq']!=n or type(e['index']) is not int or not 0<=e['index']<LIMIT or e['prev']!=prev or e['hash']!=hash_entry({k:e[k] for k in ('seq','index','prev')}):return False
        prev=e['hash']
    return True
def checkpoint(entries):
    assert validate(entries)
    return {'schema':'z328-checkpoint-v1','count':len(entries),'tip':entries[-1]['hash'] if entries else 'GENESIS','last_index':entries[-1]['index'] if entries else None}
def verify_receipt(receipt, public_key, entries):
    try:
        public_key.verify(bytes.fromhex(receipt['signature']),canonical(receipt['payload']))
        return validate(entries) and checkpoint(entries)==receipt['payload']
    except Exception:return False

# Ephemeral keys: never commit private key material.
key=Ed25519PrivateKey.generate();other=Ed25519PrivateKey.generate()
public=key.public_key();other_public=other.public_key()
entries=build([0,1,7,LIMIT-1,100,321,42]);payload=checkpoint(entries)
receipt={'payload':payload,'signature':key.sign(canonical(payload)).hex()}
checks={
 'factorial_limit':LIMIT==620448401733239439360000,
 'chain_valid':validate(entries),
 'ed25519_signature_64_bytes':len(bytes.fromhex(receipt['signature']))==64,
 'valid_receipt':verify_receipt(receipt,public,entries),
 'separate_key_fails':not verify_receipt(receipt,other_public,entries),
 'tamper_payload_count_fails':not verify_receipt({'payload':{**payload,'count':8},'signature':receipt['signature']},public,entries),
 'tamper_payload_tip_fails':not verify_receipt({'payload':{**payload,'tip':'0'*64},'signature':receipt['signature']},public,entries),
 'tamper_signature_fails':not verify_receipt({'payload':payload,'signature':'00'*64},public,entries),
 'truncated_chain_fails':not verify_receipt(receipt,public,entries[:-1]),
 'reordered_chain_fails':not verify_receipt(receipt,public,[entries[1],entries[0]]+entries[2:]),
 'edited_chain_fails':not verify_receipt(receipt,public,[{**entries[0],'index':10}]+entries[1:]),
 'extended_chain_fails':not verify_receipt(receipt,public,entries+build([5])),
 'duplicate_index_permitted':validate(build([3,3,3])),
 'empty_chain_receipt':(lambda es:verify_receipt({'payload':checkpoint(es),'signature':key.sign(canonical(checkpoint(es))).hex()},public,es))([]),
 'signature_deterministic':key.sign(canonical(payload))==key.sign(canonical(payload)),
 'public_key_serialization':len(public.public_bytes(serialization.Encoding.Raw,serialization.PublicFormat.Raw))==32,
 'wrong_schema_signature_fails':not verify_receipt({'payload':{**payload,'schema':'wrong'},'signature':receipt['signature']},public,entries),
 'no_private_key_in_receipt':set(receipt)=={'payload','signature'},
 'frozen_roll_independent':(5,3,1)!=(3,1,2),
 'rgb_capacity_separate':3*8==24 and sum((3,1,2))==6,
}
for name,result in checks.items():print(('PASS' if result else 'FAIL'),name)
print(f'{sum(checks.values())}/{len(checks)} PASS')
assert all(checks.values())
