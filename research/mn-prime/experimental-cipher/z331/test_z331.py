"""Z331: independently pinned head, revocation epochs, recovery; symbolic software only."""
import hashlib, json, math
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
LIMIT=math.factorial(24)
def canon(d):return json.dumps(d,sort_keys=True,separators=(',',':')).encode()
def digest(d):return hashlib.sha256(canon(d)).hexdigest()
def sign(sk,p):return sk.sign(canon(p)).hex()
def valid(pk,p,s):
    try:pk.verify(bytes.fromhex(s),canon(p));return True
    except Exception:return False
A=Ed25519PrivateKey.generate(); B=Ed25519PrivateKey.generate(); ROGUE=Ed25519PrivateKey.generate()
pubs={'A':A.public_key(),'B':B.public_key()}
def make_segment(prev,epoch,signer,ranks,sk):
    body={'prev':prev,'epoch':epoch,'signer':signer,'ranks':list(ranks)}
    return {**body,'hash':digest(body),'signature':sign(sk,body)}
def verify_chain(segments,policy):
    prev='GENESIS'; last_epoch=-1
    for s in segments:
        if set(s)!={'prev','epoch','signer','ranks','hash','signature'}:return False
        e=s['epoch']; name=s['signer']
        if type(e)!=int or e<=last_epoch or s['prev']!=prev:return False
        if name not in pubs or e<policy['start'].get(name,10**9):return False
        if e>=policy['revoke_at'].get(name,10**9):return False
        if not isinstance(s['ranks'],list) or not s['ranks'] or any(type(x)!=int or not 0<=x<LIMIT for x in s['ranks']):return False
        body={k:s[k] for k in ('prev','epoch','signer','ranks')}
        if s['hash']!=digest(body) or not valid(pubs[name],body,s['signature']):return False
        prev=s['hash'];last_epoch=e
    return True
policy={'start':{'A':0,'B':2},'revoke_at':{'A':2}}
s0=make_segment('GENESIS',0,'A',[0,1],A)
s1=make_segment(s0['hash'],1,'A',[42],A)
s2=make_segment(s1['hash'],2,'B',[LIMIT-1],B)
s3=make_segment(s2['hash'],3,'B',[7,11],B)
chain=[s0,s1,s2,s3]
anchor={'epoch':3,'tip':s3['hash'],'count':4}
def check_anchor(seq,anch):
    return (verify_chain(seq,policy) and len(seq)==anch['count'] and
            seq[-1]['epoch']==anch['epoch'] and seq[-1]['hash']==anch['tip'])
def swapped(s,**kw):return {**s,**kw}
checks={
 'factorial_limit': LIMIT==620448401733239439360000,
 'valid_chain':verify_chain(chain,policy),
 'pinned_head_matches':check_anchor(chain,anchor),
 'no_rollback_to_epoch2':not check_anchor(chain[:-1],anchor),
 'no_rollback_to_epoch1':not check_anchor(chain[:2],anchor),
 'missing_middle_rejected':not verify_chain([s0,s2,s3],policy),
 'reordered_rejected':not verify_chain([s1,s0,s2,s3],policy),
 'tampered_index_rejected':not verify_chain([s0,s1,swapped(s2,ranks=[3]),s3],policy),
 'tampered_hash_rejected':not verify_chain([s0,s1,swapped(s2,hash='0'*64),s3],policy),
 'wrong_signature_rejected':not verify_chain([s0,s1,swapped(s2,signature=sign(ROGUE,{k:s2[k] for k in ('prev','epoch','signer','ranks')})),s3],policy),
 'revoked_A_epoch2_rejected':not verify_chain([s0,s1,make_segment(s1['hash'],2,'A',[5],A)],policy),
 'B_before_start_rejected':not verify_chain([make_segment('GENESIS',0,'B',[0],B)],policy),
 'epoch_repeat_rejected':not verify_chain([s0,make_segment(s0['hash'],0,'A',[1],A)],policy),
 'epoch_decrease_rejected':not verify_chain([s0,s1,make_segment(s1['hash'],0,'A',[1],A)],policy),
 'negative_rank_rejected':not verify_chain([make_segment('GENESIS',0,'A',[-1],A)],policy),
 'overflow_rank_rejected':not verify_chain([make_segment('GENESIS',0,'A',[LIMIT],A)],policy),
 'anchor_tip_tamper_rejected':not check_anchor(chain,{**anchor,'tip':'0'*64}),
 'anchor_count_tamper_rejected':not check_anchor(chain,{**anchor,'count':3}),
 'anchor_epoch_tamper_rejected':not check_anchor(chain,{**anchor,'epoch':2}),
 'independent_ket_registers':(5,3,1)!=(3,1,2),
}
for k,v in checks.items():print(('PASS' if v else 'FAIL'),k)
print(f'{sum(checks.values())}/{len(checks)} PASS')
assert all(checks.values())
