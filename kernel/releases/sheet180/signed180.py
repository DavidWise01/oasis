"""S180 signed atomic target head and conservative recovery reconciliation."""
from cryptography.exceptions import InvalidSignature
from atomic179 import append,audit,reconcile,Denied,canonical
class Quarantine(Denied):pass
def signed_head(db,private_key,resource):
    if not resource:raise Denied('RESOURCE_REQUIRED')
    s=audit(db)
    message={'schema':'oasis.sheet180.target-head.v1','resource':resource,'epoch':s['epoch'],'owner':s['owner'],'cursor':s['cursor'],'head':s['head']}
    return {'body':message,'signature':private_key.sign(canonical(message)).hex()}
def verify_head(head,pubkey,resource):
    if not isinstance(head,dict) or not isinstance(head.get('body'),dict):raise Quarantine('BAD_HEAD')
    b=head['body']
    if b.get('schema')!='oasis.sheet180.target-head.v1' or b.get('resource')!=resource:raise Quarantine('WRONG_RESOURCE')
    try:pubkey.verify(bytes.fromhex(head['signature']),canonical(b))
    except (InvalidSignature,ValueError,KeyError,TypeError):raise Quarantine('INVALID_HEAD_SIGNATURE')
    if not isinstance(b.get('cursor'),int) or isinstance(b['cursor'],bool) or b['cursor']<0 or not isinstance(b.get('epoch'),int) or b['epoch']<0:raise Quarantine('BAD_HEAD_NUMBERS')
    return b
def verify_against_target(db,head,pubkey,resource):
    b=verify_head(head,pubkey,resource)
    s=audit(db)
    if any(s[k]!=b[k] for k in ['epoch','owner','cursor','head']):raise Quarantine('TARGET_HEAD_MISMATCH')
    return b
def reconcile_triplet(db,wal,anchor,pubkey,resource,request=None):
    b=verify_against_target(db,anchor,pubkey,resource)
    if not isinstance(wal,dict) or wal.get('resource')!=resource:raise Quarantine('WAL_RESOURCE')
    if wal.get('pending'):raise Quarantine('WAL_UNCERTAIN_PREPARE')
    if wal.get('cursor')!=b['cursor'] or wal.get('head')!=b['head']:raise Quarantine('WAL_TARGET_DIVERGENCE')
    if request is not None:
        status=reconcile(db,request['id'],request['index'],request['payload'])
        if status!='COMMITTED':raise Quarantine('REQUEST_'+status)
    return {'status':'VERIFIED','cursor':b['cursor'],'head':b['head']}
def append_verified(db,owner,epoch,request_id,index,payload,resource,signing_key):
    result=append(db,owner,epoch,request_id,index,payload)
    return {'target':result,'signed':signed_head(db,signing_key,resource)}
