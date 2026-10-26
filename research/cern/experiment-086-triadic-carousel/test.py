import sqlite3,tempfile,hashlib,json,itertools
from pathlib import Path
PATS=['[{()}]','{[()]}','([{}])','({[]})','[({})]','{([])}']
ANCHOR={'A1':'(0,0,0)','B1':'(0,0,i)','C1':'(-1,0,+1)'}
PAIR={'[':']','{':'}','(':')'}
def validate(s):
 stack=[]
 for x in s:
  if x in PAIR:stack.append(x)
  elif not stack or PAIR[stack.pop()]!=x:return False
 return not stack
assert all(validate(p) for p in PATS)
assert not validate('[({}])]')
def digest(x):return hashlib.sha256(json.dumps(x,sort_keys=True).encode()).hexdigest()
checks=0
with tempfile.TemporaryDirectory() as temp:
 def db(n):
  c=sqlite3.connect(str(Path(temp)/(n+'.db')),isolation_level=None)
  c.execute('PRAGMA journal_mode=WAL');c.execute('PRAGMA synchronous=FULL')
  c.execute('CREATE TABLE IF NOT EXISTS tether(id TEXT PRIMARY KEY,anchor TEXT)')
  c.execute('CREATE TABLE IF NOT EXISTS inbox(id TEXT PRIMARY KEY,body TEXT)')
  c.execute('INSERT OR IGNORE INTO tether VALUES (?,?)',(n,ANCHOR[n]))
  return c
 for idx,p in enumerate(PATS):
  for a,b in itertools.permutations(ANCHOR,2):
   key=f'{a}>{b}:{idx}';obj={'src':a,'dst':b,'pattern':p,'winding':idx,'beat':idx,'cell':idx}
   h=digest(obj);c=db(b)
   assert c.execute('SELECT anchor FROM tether').fetchone()[0]==ANCHOR[b];checks+=1
   c.execute('INSERT INTO inbox VALUES (?,?)',(key,json.dumps(obj,sort_keys=True)));c.close()
   c=db(b);assert c.execute('SELECT body FROM inbox WHERE id=?',(key,)).fetchone()[0]==json.dumps(obj,sort_keys=True);checks+=1
   assert digest(obj)==h;checks+=1
   try:c.execute('INSERT INTO inbox VALUES (?,?)',(key,json.dumps(obj,sort_keys=True)));raise AssertionError('duplicate')
   except sqlite3.IntegrityError:checks+=1
   assert validate(p);checks+=1
   c.close()
 for n in ANCHOR:
  c=db(n);assert c.execute('SELECT COUNT(*) FROM inbox').fetchone()[0]==12;checks+=1
  assert c.execute('SELECT anchor FROM tether').fetchone()[0]==ANCHOR[n];checks+=1
  c.close()
assert checks==186
print('PASS',checks,'checks; 36 routes; 12 receipts per journal')
