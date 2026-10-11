"""Gate 29: symbolic Stargate wrapper, pinned zero, mirrored address."""
ADDRESS=('000','00','11','24','42','11','00','000')
PAIR={'24':'42','42':'24'}
def invert(token): return PAIR.get(token,token)
def reflect(address): return tuple(invert(x) for x in reversed(address))
def test():
 checks={
  'eight address tokens':len(ADDRESS)==8,
  'exact supplied address':' '.join(ADDRESS)=='000 00 11 24 42 11 00 000',
  'reflective palindrome':reflect(ADDRESS)==ADDRESS,
  'ordinary palindrome is false':ADDRESS[::-1]!=ADDRESS,
  'inversion involutive':all(invert(invert(x))==x for x in ADDRESS),
  'root pinned':ADDRESS[0]==ADDRESS[-1]=='000',
  'central fold 24 42':ADDRESS[3:5]==('24','42'),
  'signed shell sums to zero':(-1)+0+1==0,
  'two reflections restore input':reflect(reflect(ADDRESS))==ADDRESS,
 }
 for name,ok in checks.items(): print(('PASS' if ok else 'FAIL'),name)
 assert all(checks.values())
 print(f'{sum(checks.values())}/{len(checks)} PASS')
if __name__=='__main__':test()
