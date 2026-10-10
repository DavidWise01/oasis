"""S216: independently recompute WAL cryptographic and transaction semantic lineage."""
import hashlib,json,pathlib
class InvalidWAL(Exception):pass
ZERO='0'*64
def hash_obj(x):return hashlib.sha256(json.dumps(x,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
def validate(path,common):
    try:
        raw=pathlib.Path(path).read_bytes()
        if not raw or not raw.endswith(b'\n'):raise InvalidWAL('TORN')
        head=ZERO;pending=None;used=set();commit=None;seen=[]
        for i,line in enumerate(raw.splitlines(),1):
            r=json.loads(line)
            if type(r)!=dict or set(r)!={'seq','prev','kind','payload','hash'} or type(r['seq']) is not int or r['seq']!=i or r['prev']!=head:raise InvalidWAL('CHAIN')
            if hash_obj({k:r[k] for k in ('seq','prev','kind','payload')})!=r['hash']:raise InvalidWAL('HASH')
            p=r['payload']
            if type(p)!=dict:raise InvalidWAL('PAYLOAD')
            if r['kind']=='prepare':
                if pending is not None or set(p)!={'nonce','route','op','inputHash','resultHash','prepareHash'} or not isinstance(p['nonce'],str) or not p['nonce'] or p['nonce'] in used:raise InvalidWAL('PREPARE')
                if any(not isinstance(p[k],str) or len(p[k])!=64 for k in ('inputHash','resultHash','prepareHash')):raise InvalidWAL('DIGEST')
                if p['prepareHash']!=hash_obj({k:p[k] for k in ('nonce','route','op','inputHash','resultHash')}):raise InvalidWAL('PREPARE_HASH')
                used.add(p['nonce']);pending=p
            elif r['kind']=='commit':
                if pending is None or set(p)!={'nonce','prepareHash'} or p['nonce']!=pending['nonce'] or p['prepareHash']!=pending['prepareHash']:raise InvalidWAL('COMMIT')
                commit={'nonce':p['nonce'],'head':r['hash'],'seq':i};seen.append(commit);pending=None
            else:raise InvalidWAL('KIND')
            head=r['hash']
        if pending is not None:raise InvalidWAL('UNCOMMITTED')
        if (head,len(raw.splitlines()))!=(common['head'],common['seq']):raise InvalidWAL('HEAD')
        matched=[x for x in seen if x['nonce']==common['nonce']]
        if len(matched)!=1 or matched[0]!=commit:raise InvalidWAL('NOT_TAIL_COMMIT')
        if len(seen)<1 or len(raw.splitlines())!=2*len(seen):raise InvalidWAL('PAIR_COUNT')
        if common['previous_seq']!=common['seq']-2:raise InvalidWAL('OFFSET')
        if common['previous_head']!=(json.loads(raw.splitlines()[-2])['prev']):raise InvalidWAL('ANCESTOR')
        return commit
    except (KeyError,TypeError,ValueError,UnicodeError,json.JSONDecodeError) as e:raise InvalidWAL('MALFORMED') from e
