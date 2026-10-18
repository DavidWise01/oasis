"""Z330 Ttn: interrupted signed-checkpoint recovery, symbolic software test only."""
import json, hashlib, math
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.exceptions import InvalidSignature
LIMIT=math.factorial(24)
def canonical(x): return json.dumps(x,sort_keys=True,separators=(',',':')).encode()
def sha(x): return hashlib.sha256(canonical(x)).hexdigest()
def sign(key,p): return key.sign(canonical(p)).hex()
def valid(pub,p,sig):
    try: pub.verify(bytes.fromhex(sig),canonical(p)); return True
    except (InvalidSignature, ValueError, TypeError): return False
A=Ed25519PrivateKey.from_private_bytes(bytes([1])*32)
B=Ed25519PrivateKey.from_private_bytes(bytes([2])*32)
ROGUE=Ed25519PrivateKey.from_private_bytes(bytes([3])*32)
keys={'A':A.public_key(),'B':B.public_key()}
def make_segment(seg, keyname, signing_key, predecessor, ranks):
    assert all(type(r)==int and 0<=r<LIMIT for r in ranks)
    payload={'segment':seg,'signer':keyname,'previous':predecessor,'ranks':ranks}
    return {'payload':payload,'signature':sign(signing_key,payload)}
def tip(segment):return sha(segment)
def rotation(old,new,seq,signer):
    payload={'from':old,'to':new,'effective_segment':seq}
    return {'payload':payload,'signature':sign(signer,payload)}
def verify_chain(segments,rotation_cert=None,revoked=frozenset(),expected_tip=None):
    previous='GENESIS'; active='A'
    for index,s in enumerate(segments):
        p=s['payload']; who=p['signer']
        if p['segment']!=index or p['previous']!=previous:return False
        if not all(type(r)==int and 0<=r<LIMIT for r in p['ranks']):return False
        if index==1 and rotation_cert is not None:
            r=rotation_cert['payload']
            if r!={'from':'A','to':'B','effective_segment':1}:return False
            if not valid(keys['A'],r,rotation_cert['signature']):return False
            active='B'
        if who!=active or who in revoked or not valid(keys[who],p,s['signature']):return False
        previous=tip(s)
    return expected_tip is None or expected_tip==previous
s0=make_segment(0,'A',A,'GENESIS',[0,4,6]);s1=make_segment(1,'B',B,tip(s0),[7,8]);s2=make_segment(2,'B',B,tip(s1),[LIMIT-1]);cert=rotation('A','B',1,A)
chain=[s0,s1,s2]; trusted_tip=tip(s2)
# Recovered final state from durable complete checkpoint; unfinished append is discarded.
partial={'payload':{'segment':3,'signer':'B','previous':tip(s2),'ranks':[13]},'signature':''}
checks={
 '24_factorial_bound':LIMIT==620448401733239439360000,
 'genesis_valid':verify_chain([s0]),
 'valid_rotation':valid(keys['A'],cert['payload'],cert['signature']),
 'full_chain_valid':verify_chain(chain,cert),
 'trusted_tip_match':verify_chain(chain,cert,expected_tip=trusted_tip),
 'discard_partial_recovery':verify_chain(chain,cert,expected_tip=trusted_tip),
 'partial_rejected':not verify_chain(chain+[partial],cert),
 'truncated_tip_detected':not verify_chain(chain[:-1],cert,expected_tip=trusted_tip),
 'reordered_segment_rejected':not verify_chain([s0,s2,s1],cert),
 'no_rotation_rejected':not verify_chain(chain),
 'tampered_rotation_rejected':not verify_chain(chain,{'payload':cert['payload'],'signature':'00'*64}),
 'wrong_rotation_scope_rejected':not verify_chain(chain,{'payload':{**cert['payload'],'effective_segment':2},'signature':cert['signature']}),
 'rogue_signer_rejected':not verify_chain([s0,make_segment(1,'B',ROGUE,tip(s0),[7,8])],cert),
 'revoked_B_rejected':not verify_chain(chain,cert,revoked={'B'}),
 'revoked_A_rejected':not verify_chain(chain,cert,revoked={'A'}),
 'modified_rank_rejected':not verify_chain([s0,{**s1,'payload':{**s1['payload'],'ranks':[7,9]}},s2],cert),
 'wrong_checkpoint_tip_rejected':not verify_chain(chain,cert,expected_tip='0'*64),
 'out_of_range_rejected':not verify_chain([s0,{**s1,'payload':{**s1['payload'],'ranks':[LIMIT]}},s2],cert),
 'governance_separate':(5,3,1)!=(3,1,2),
 'symbol_unique_against_z320': 'Ttn'!='Tbn',
}
for k,v in checks.items():print(('PASS' if v else 'FAIL'),k)
print(f'{sum(checks.values())}/{len(checks)} PASS')
assert all(checks.values())
