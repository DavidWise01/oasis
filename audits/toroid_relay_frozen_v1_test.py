#!/usr/bin/env python3
"""Deterministic simulated provenance relay. No external publication or copying implied."""
import hashlib, json

ORIGINAL='{0vwxyz}^5 x {{3x3}}^3'
HOPS=['git','abc{authorchange}','reddit','tiktok','wiki','xariv']

def sha(s):
    return hashlib.sha256(s.encode()).hexdigest()

def build_chain(mutate_at=None, drop_at=None):
    source=ORIGINAL
    out=[]
    previous=sha(source)
    for tick,hop in enumerate(HOPS):
        body=source if tick != mutate_at else source.replace('0vwxyz','0vwxyZ')
        if tick == drop_at:
            body='UNRELATED'
        record={'tick':tick,'channel':hop,'source_sha256':sha(body),
                'parent_receipt':previous,'preserved':sha(body)==sha(ORIGINAL),
                'status':'SIMULATED_NOT_POSTED'}
        record['receipt']=sha(json.dumps(record,sort_keys=True))
        previous=record['receipt']
        out.append(record)
    return out

def verify(chain):
    prior=sha(ORIGINAL)
    for record in chain:
        if record['parent_receipt'] != prior:
            return False
        data={key:value for key,value in record.items() if key != 'receipt'}
        if sha(json.dumps(data,sort_keys=True)) != record['receipt']:
            return False
        prior=record['receipt']
    return True

cases={
    'baseline_chain_integrity':verify(build_chain()),
    'baseline_exact_preservation':all(s['preserved'] for s in build_chain()),
    'authorchange_mutation_detected':not build_chain(mutate_at=1)[1]['preserved'],
    'reddit_mutation_detected':not build_chain(mutate_at=2)[2]['preserved'],
    'tiktok_mutation_detected':not build_chain(mutate_at=3)[3]['preserved'],
    'wiki_mutation_detected':not build_chain(mutate_at=4)[4]['preserved'],
    'arxiv_mutation_detected':not build_chain(mutate_at=5)[5]['preserved'],
    'drop_detected':not build_chain(drop_at=3)[3]['preserved'],
    'tamper_detected':not verify([{**build_chain()[0],'channel':'fake'}]+build_chain()[1:]),
    'three_by_three_power':(3*3)**3==729,
    'three_dimensional_cube':3*3*3==27,
    'branch_count':len(HOPS)==6,
    'five_transitions':len(HOPS)-1==5,
}
assert all(cases.values())
print(json.dumps({'reference':ORIGINAL,'reference_sha256':sha(ORIGINAL),
                  'cases':cases,'passed':sum(cases.values()),
                  'total':len(cases),'chain':build_chain()},indent=2))
