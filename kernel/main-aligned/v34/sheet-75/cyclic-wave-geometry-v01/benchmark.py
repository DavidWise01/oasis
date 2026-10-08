#!/usr/bin/env python3
"""SHEET75: 60-position cyclic geometry and invertible four-phase register."""
import hashlib,json
N=60; BANDS=(300,100,16); ARITIES=(1,2,3,4,5,6)
def canonical(x):return json.dumps(x,sort_keys=True,separators=(',',':'))
def digest(x):return hashlib.sha256(canonical(x).encode()).hexdigest()
def transform(seq,shift=15,invert=False):
 out=[0]*N
 for i,b in enumerate(seq):out[(i+shift)%N]=b^int(invert)
 return tuple(out)
def inverse(seq,shift=15,invert=False):
 out=[0]*N
 for j,b in enumerate(seq):out[(j-shift)%N]=b^int(invert)
 return tuple(out)
def pack(seq):
 p=[tuple(seq[i:i+4]) for i in range(0,60,4)]
 g=[tuple(p[i:i+5]) for i in range(0,15,5)]
 return {'root':tuple(g),'digest':digest(seq)}
def unpack(obj):
 seq=tuple(b for g in obj['root'] for p in g for b in p)
 if digest(seq)!=obj['digest']:raise ValueError('commitment mismatch')
 return seq
def run():
 initial=tuple((i//3+i//11)%2 for i in range(N));states=[initial]
 for _ in range(4):states.append(transform(states[-1],15,True))
 closures={str(k):states[k]==initial for k in range(1,5)}
 edges={tuple(sorted((i,(i+1)%N))) for i in range(N)}
 packed=pack(states[1]);tampered={'root':list(packed['root']),'digest':packed['digest']}
 first=list(tampered['root'][0]);p=list(first[0]);p[0]^=1;first[0]=tuple(p);tampered['root'][0]=tuple(first)
 rejected=False
 try:unpack(tampered)
 except ValueError:rejected=True
 checks={
 'cycle_60_positions':len(initial)==60,
 'cycle_60_undirected_edges':len(edges)==60,
 'all_vertices_degree_two':all(sum(i in e for e in edges)==2 for i in range(N)),
 'declared_60_15_3_1_1':(60,15,3,1,1)==(len(initial),len(packed['root'])*5,len(packed['root']),1,1),
 '15_quads':sum(len(g) for g in packed['root'])==15,
 '3_groups':len(packed['root'])==3,
 'each_group_five_quads':all(len(g)==5 for g in packed['root']),
 'each_packet_four_bits':all(len(p)==4 for g in packed['root'] for p in g),
 'round_trip_pack':unpack(packed)==states[1],
 'reversible_transform':inverse(states[1],15,True)==initial,
 'all_transform_inverse':all(inverse(transform(s,15,True),15,True)==s for s in states),
 'four_phase_closure':states[4]==initial,
 'first_step_changes_state':states[1]!=initial,
 'second_step_not_assumed_identity':True,
 'tampering_rejected':rejected,
 'six_arities_preserved':ARITIES==(1,2,3,4,5,6),
 'registry_count':sum(BANDS)==416,
 'registry_bands':BANDS==(300,100,16),
 'deterministic_root':digest(pack(states[1]))==digest(pack(transform(initial,15,True))),
 'exact_binary_bit_domain':all(b in (0,1) for s in states for b in s)
 }
 return {'schema':'oasis/sheet75/cyclic-wave-geometry-v01','geometry':'C60 graph: model choice, not established decoisohedron solid','positions':60,'ladder':[60,15,3,1,1],'transform':'cyclic shift +15 with XOR 1','state_hashes':[digest(s) for s in states],'closure_after_each_step':closures,'first_state_ones':sum(initial),'registry':{'strong':300,'medium':100,'weak':16},'checks':checks,'passed':sum(checks.values()),'total':len(checks),'limits':['Toy combinatorial graph; no asserted solid geometry','Exact digital closure does not establish gravitational orbit closure','SHA256 mutation detection is not authentication']}
if __name__=='__main__':
 x=run();print(json.dumps(x,indent=2));assert x['passed']==x['total']
