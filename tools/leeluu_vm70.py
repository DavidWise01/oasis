"""LEELUU Test070: four-core VM with exactly three backward tracks."""
import hashlib,json
ROWS='ABCDEFGHIJKLMNOP'
TRACKS=('i','u','u.s.')
SUBLANES=('identity','sequence','neighbors','symmetry','cross_core')
PHASES=('creation','life','death','recycle','repeat')
ADDRS=[f'{r}{c}' for r in ROWS for c in range(1,17)]
def address(r,c):
 return f'{ROWS[r]}{c+1}' if 0<=r<16 and 0<=c<16 else None
def run(transcription=None):
 memory={a:'.' for a in ADDRS}
 for k,v in (transcription or {}).items():
  if k not in memory or not isinstance(v,str) or not v:raise ValueError('invalid glyph transcription')
  memory[k]=v
 classes={};events=[];backwards=[]
 for idx,a in enumerate(ADDRS):
  row,col=divmod(idx,16);core=idx//64;lane=core*30+(idx%64)%30;glyph=memory[a]
  if glyph!='.' and glyph not in classes:classes[glyph]=f'χ{len(classes)+1:03d}'
  identity=classes.get(glyph,'.')
  right=memory[address(row,col+1)] if col<15 else '.'
  down=memory[address(row+1,col)] if row<15 else '.'
  mirror=memory[address(row,15-col)]
  other_core=memory[address((row+4)%16,col)]
  readings=(identity,(glyph,right),(right,down),(glyph,mirror),(glyph,other_core))
  for sublane,name in enumerate(SUBLANES):
   observed=readings[sublane]
   for explorer,mode in enumerate(('forward','reverse','transform')):
    if mode=='reverse' and isinstance(observed,tuple):value=tuple(reversed(observed))
    elif mode=='transform':value=('transformed',observed)
    else:value=observed
    events.append((a,core,lane,sublane,explorer,mode,value))
   backwards.extend([
    (a,lane,sublane,'i',identity,'isomorphic' if identity!='.' else 'unknown','intent:unassigned'),
    (a,lane,sublane,'u',int(glyph!='.' and right==glyph),'harmony:unscored','resonance:unscored'),
    (a,lane,sublane,'u.s.',PHASES[sublane],'symbolic-lifecycle')])
 result={'cores':4,'lanes':120,'sublanes':600,'explorer_slots':1800,'glyphs':256,
 'observations':len(events),'backtrack_records':len(backwards),
 'backtracks_per_cell_sublane':3,'backtrack_types':list(TRACKS),
 'known_glyphs':sum(g!='.' for g in memory.values()),
 'unique_character_classes':len(classes),'events':events,'backtracks':backwards}
 result['sha256']=hashlib.sha256(json.dumps((events,backwards),ensure_ascii=False,separators=(',',':')).encode()).hexdigest()
 return result
if __name__=='__main__':
 d=run();print(json.dumps({k:v for k,v in d.items() if k not in ('events','backtracks')},indent=2))
