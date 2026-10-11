"""Gate 10: identity and lineage invariants in symbolic reproductive events.
Not a complete model of spermatogenesis, oogenesis or embryology.
"""
from dataclasses import dataclass

@dataclass(frozen=True)
class Event:
    kind: str
    parent: str
    offspring: tuple[str,...]
    chromosome_sets: tuple[int,...]

def mitosis(parent):
    return Event('mitosis',parent,(parent+'.1',parent+'.2'),(2,2))

def male_meiosis(parent):
    return Event('male_meiosis',parent,tuple(parent+'.'+str(i) for i in range(1,5)),(1,1,1,1))

def female_meiosis(parent):
    return Event('female_meiosis',parent,(parent+'.egg',parent+'.polar1',parent+'.polar2',parent+'.polar3'),(1,1,1,1))

def molt(organism,cycle):
    return Event('molt',organism,(organism,), (2,))

def run():
    origin='i'
    events=(mitosis(origin),male_meiosis('male_precursor'),female_meiosis('female_precursor'),molt('tardigrade',1),molt('tardigrade',2))
    checks={
      'two mitotic daughters':len(events[0].offspring)==2,
      'new mitotic identities':all(x!=origin for x in events[0].offspring),
      'mitosis chromosome count maintained':events[0].chromosome_sets==(2,2),
      'four male meiotic products':len(events[1].offspring)==4,
      'male meiotic products haploid':events[1].chromosome_sets==(1,)*4,
      'one functional egg from oogenesis':sum(x.endswith('.egg') for x in events[2].offspring)==1,
      'four unequal female meiotic products modeled':len(events[2].offspring)==4,
      'female products haploid':events[2].chromosome_sets==(1,)*4,
      'molt retains identity':events[3].offspring==(events[3].parent,),
      'repeat molt retains identity':events[4].offspring==events[3].offspring,
      'reproductive products unique':len(set(events[0].offspring+events[1].offspring+events[2].offspring))==10,
      'append-only immutable log':len(events)==5 and all(isinstance(e,Event) for e in events),
    }
    for k,v in checks.items():print(('PASS' if v else 'FAIL'),k)
    print(f'RESULT {sum(checks.values())}/{len(checks)}')
    assert all(checks.values())
if __name__=='__main__':run()
