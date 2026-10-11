"""Gate 31: exact nested crosspipe grammar (8 paired channels)."""
import re
SOURCE='{{u24u{u42u{d24{d42{l24{l42{r24{r42{b24{b42{a24{a42{sel24{sel42{star24{star42}}}}}}}}}}}}}}}}}'
TOKENS=('u24u','u42u','d24','d42','l24','l42','r24','r42','b24','b42','a24','a42','sel24','sel42','star24','star42')
def parse(s):
 depth=0;labels=[];levels=[]
 for token in re.findall(r'\{|\}|[^{}]+',s):
  if token=='{':depth+=1
  elif token=='}':
   depth-=1
   if depth<0:raise ValueError('premature close')
  else:
   if token not in TOKENS:raise ValueError('unknown token')
   labels.append(token);levels.append(depth)
 if depth:raise ValueError('unclosed')
 return tuple(labels),tuple(levels)
def test():
 tokens,levels=parse(SOURCE)
 checks={
  '16 tokens':tokens==TOKENS,
  '17 balanced braces':SOURCE.count('{')==SOURCE.count('}')==17,
  'nested levels':levels==tuple(range(2,18)),
  'eight pairs':len(tokens)//2==8,
  'u spelling preserved':tokens[:2]==('u24u','u42u'),
  'repeatable parse':parse(SOURCE)==(tokens,levels),
  'non-palindrome':tokens!=tokens[::-1],
  'star endpoint':tokens[-2:]==('star24','star42')}
 for k,v in checks.items():print(('PASS' if v else 'FAIL'),k)
 assert all(checks.values())
 print(f'{sum(checks.values())}/{len(checks)} PASS')
if __name__=='__main__':test()
