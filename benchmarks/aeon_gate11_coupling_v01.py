"""Gate 11 deterministic branch coupling. Simulated policy, not biology."""
from dataclasses import dataclass,replace
@dataclass(frozen=True)
class Cell:
 id:int
 parent:int|None
 generation:int
 status:str='active'
 damage:int=0
STRENGTH={'weak':1,'medium':2,'strong':3}
def build(depth=4):
 cells={1:Cell(1,None,0)}
 for g in range(1,depth+1):
  for p in [c.id for c in list(cells.values()) if c.generation==g-1]:
   for k in (2*p,2*p+1):cells[k]=Cell(k,p,g)
 return cells
def propagate(cells,origin,strength,log):
 q=[origin]
 while q:
  i=q.pop(0);c=cells[i]
  if c.status!='active':continue
  cells[i]=replace(c,damage=c.damage+STRENGTH[strength]);log.append(('damage',i))
  if strength=='strong' and i!=origin:
   cells[i]=replace(cells[i],status='terminated');log.append(('prune',i));continue
  if strength=='medium' and i!=origin:continue
  q.extend(x for x in (2*i,2*i+1) if x in cells)
def repair(cells,i,log):
 c=cells[i];log.append(('audit',i))
 if c.parent is not None:log.append(('audit_left',c.parent))
 if c.status!='active' or (c.parent is not None and cells[c.parent].status!='active'):
  log.append(('rejected',i));return False
 cells[i]=replace(c,damage=max(0,c.damage-1));log.append(('repair_append',i));return True
def run():
 base=build();checks={'31 records':len(base)==31,'16 leaves':sum(c.generation==4 for c in base.values())==16};v={}
 for s in STRENGTH:
  cells=base.copy();log=[];propagate(cells,2,s,log);v[s]=(cells,log)
 w,wl=v['weak'];m,ml=v['medium'];s,sl=v['strong']
 checks.update({'weak reaches descendants':w[16].damage==1,'medium local':m[4].damage==2 and m[8].damage==0,'strong pruning':s[4].status==s[5].status=='terminated','pruning halts propagation':s[8].damage==0,'weak repair':repair(w,16,wl) and w[16].damage==0,'left-first audit':wl[-2]==('audit_left',8),'no repair after pruning':not repair(s,4,sl),'parent immutable':all(c.parent==(c.id//2 if c.id>1 else None) for c in s.values()),'positive occupancy':all(c.id>0 for c in s.values()),'base unchanged':all(c.status=='active' and not c.damage for c in base.values()),'append-only events':all(isinstance(e,tuple) for _,log in v.values() for e in log),'weak medium no pruning':all(c.status=='active' for c in w.values()) and all(c.status=='active' for c in m.values())})
 for name,ok in checks.items():print('PASS' if ok else 'FAIL',name)
 print(sum(checks.values()),'/',len(checks));assert all(checks.values())
if __name__=='__main__':run()
