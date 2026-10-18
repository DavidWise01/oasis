"""Z329 segmented Ed25519 checkpoint chain; research prototype only."""
import hashlib, json, math
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization

LIMIT=math.factorial(24)
def canonical(x): return json.dumps(x,sort_keys=True,separators=(',',':')).encode()
def sha(x): return hashlib.sha256(canonical(x)).hexdigest()
def pubid(pub): return pub.public_bytes(serialization.Encoding.Raw,serialization.PublicFormat.Raw).hex()
def append_segment(segment_id, ranks, previous_tip, private_key, previous_key_id, rotation_receipt=None):
    records=[]; prev=previous_tip
    for ix, rank in enumerate(ranks):
        if type(rank) is not int or not 0<=rank<LIMIT: raise ValueError('rank invalid')
        e={'segment':segment_id,'sequence':ix,'rank':rank,'prev':prev}
        records.append({**e,'hash':sha(e)});prev=records[-1]['hash']
    payload={'segment':segment_id,'count':len(records),'prev_tip':previous_tip,'tip':prev,'key_id':pubid(private_key.public_key()),'previous_key_id':previous_key_id}
    return {'records':records,'payload':payload,'signature':private_key.sign(canonical(payload)).hex(),'rotation':rotation_receipt}
def rotation_approval(oldkey,newkey):
    payload={'from':pubid(oldkey.public_key()),'to':pubid(newkey.public_key())}
    return {'payload':payload,'signature':oldkey.sign(canonical(payload)).hex()}
def verify(segments,trusted_genesis_pub,keys):
    prev='GENESIS'; active=pubid(trusted_genesis_pub)
    for i,s in enumerate(segments):
        try:
            p=s['payload']; kid=p['key_id']; rot=s['rotation']
            if p['segment']!=i or p['prev_tip']!=prev or p['previous_key_id']!=active or p['count']!=len(s['records']):return False
            if kid!=active:
                if rot is None or rot['payload']!={'from':active,'to':kid}:return False
                keys[active].verify(bytes.fromhex(rot['signature']),canonical(rot['payload']))
            elif rot is not None:return False
            keys[kid].verify(bytes.fromhex(s['signature']),canonical(p))
            h=prev
            for j,r in enumerate(s['records']):
                if set(r)!={'segment','sequence','rank','prev','hash'} or r['segment']!=i or r['sequence']!=j or type(r['rank']) is not int or not 0<=r['rank']<LIMIT or r['prev']!=h:return False
                if sha({k:r[k] for k in ('segment','sequence','rank','prev')})!=r['hash']:return False
                h=r['hash']
            if h!=p['tip']:return False
            prev=h;active=kid
        except (KeyError,ValueError,TypeError,AttributeError):return False
        except Exception:return False
    return True

k0=Ed25519PrivateKey.generate();k1=Ed25519PrivateKey.generate();rogue=Ed25519PrivateKey.generate()
keys={pubid(k.public_key()):k.public_key() for k in (k0,k1,rogue)}
s0=append_segment(0,[0,1,24,100], 'GENESIS',k0,pubid(k0.public_key()))
s1=append_segment(1,[LIMIT-1,3,18],s0['payload']['tip'],k1,pubid(k0.public_key()),rotation_approval(k0,k1))
s2=append_segment(2,[7,7,80],s1['payload']['tip'],k1,pubid(k1.public_key()))
segments=[s0,s1,s2]
from copy import deepcopy
def corrupted(i,fn):
    x=deepcopy(segments);fn(x);return not verify(x,k0.public_key(),keys)
checks={
 '24_factorial':LIMIT==620448401733239439360000,
 'three_segments':len(segments)==3,
 'ten_records':sum(len(s['records']) for s in segments)==10,
 'valid_chain':verify(segments,k0.public_key(),keys),
 'authorized_rotation':s1['rotation'] is not None and verify(segments,k0.public_key(),keys),
 'wrong_genesis_rejected':not verify(segments,rogue.public_key(),keys),
 'missing_rotation_rejected':corrupted(1,lambda x:x[1].update(rotation=None)),
 'rotation_signature_tamper':corrupted(1,lambda x:x[1]['rotation'].update(signature='00'*64)),
 'rotation_target_tamper':corrupted(1,lambda x:x[1]['rotation']['payload'].update(to=pubid(rogue.public_key()))),
 'segment_signature_tamper':corrupted(1,lambda x:x[1].update(signature='00'*64)),
 'segment_reorder_rejected':not verify([s1,s0,s2],k0.public_key(),keys),
 'segment_omission_rejected':not verify([s0,s2],k0.public_key(),keys),
 'modified_rank_rejected':corrupted(2,lambda x:x[2]['records'][0].update(rank=999)),
 'modified_tip_rejected':corrupted(2,lambda x:x[2]['payload'].update(tip='0'*64)),
 'modified_count_rejected':corrupted(0,lambda x:x[0]['payload'].update(count=5)),
 'negative_rank_rejected':corrupted(0,lambda x:x[0]['records'][0].update(rank=-1)),
 'overflow_rank_rejected':corrupted(1,lambda x:x[1]['records'][0].update(rank=LIMIT)),
 'segment_id_rejected':corrupted(2,lambda x:x[2]['payload'].update(segment=3)),
 'unsigned_rogue_rejected':not verify([s0,append_segment(1,[3],s0['payload']['tip'],rogue,pubid(k0.public_key()))],k0.public_key(),keys),
 'separate_531':(5,3,1)!=(3,1,2),
}
for k,v in checks.items(): print(('PASS' if v else 'FAIL'),k)
print(f'{sum(checks.values())}/{len(checks)} PASS')
assert all(checks.values())
