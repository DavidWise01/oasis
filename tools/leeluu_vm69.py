"""LEELUU Test069: deterministic 4-core, 120-lane, 600-sublane, 1800-explorer VM."""
import hashlib,json
from collections import Counter
ROWS="ABCDEFGHIJKLMNOP"
CELLS=[f"{r}{c}" for r in ROWS for c in range(1,17)]
def run(transcription=None):
 memory={addr:"." for addr in CELLS}
 for address,glyph in (transcription or {}).items():
  if address not in memory or not isinstance(glyph,str) or not glyph:raise ValueError("invalid glyph entry")
  memory[address]=glyph
 assignments=[]
 for index,address in enumerate(CELLS):
  core=index//64;lane=core*30+(index%64)%30
  assignments.append((address,core,lane))
 observations=[]
 for address,core,lane in assignments:
  glyph=memory[address];ri=ROWS.index(address[0]);ci=int(address[1:])-1
  right=f"{ROWS[ri]}{ci+2}" if ci<15 else None
  below=f"{ROWS[ri+1]}{ci+1}" if ri<15 else None
  neighbors=[memory[a] for a in (right,below) if a]
  for sublane in range(5):
   for explorer in range(3):
    if explorer==0:finding=glyph
    elif explorer==1:finding=int(glyph!="." and any(n==glyph for n in neighbors))
    else:finding=int(glyph!="." and len(neighbors)==2 and all(n!="." for n in neighbors))
    observations.append((address,core,lane,sublane,explorer,finding))
 digest=hashlib.sha256(json.dumps(observations,ensure_ascii=False,separators=(",",":")).encode()).hexdigest()
 loads=Counter(x[2] for x in assignments)
 return {"cores":4,"lanes":120,"sublanes":600,"explorers":1800,"cells":256,
 "assignments":len(assignments),"observations":len(observations),
 "known_cells":sum(v!="." for v in memory.values()),
 "covered_cells":len({x[0] for x in assignments}),
 "lane_min_load":min(loads.values()),"lane_max_load":max(loads.values()),
 "repeat_findings":sum(x[5]==1 for x in observations if x[4]==1),
 "trace_sha256":digest,"assignments_trace":assignments,"observations_trace":observations}
if __name__=="__main__":
 r=run();print(json.dumps({k:v for k,v in r.items() if not k.endswith("_trace")},indent=2))
