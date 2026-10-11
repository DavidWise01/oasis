"""LEELUU Test068: deterministic four-core glyph reader; glyphs are data, not instructions."""
import hashlib,json
ROWS="ABCDEFGHIJKLMNOP"
def run(transcription=None,ticks=64):
 if not isinstance(ticks,int) or not 0<=ticks<=64:raise ValueError("ticks")
 memory={f"{r}{c}":"." for r in ROWS for c in range(1,17)}
 for address,glyph in (transcription or {}).items():
  if address not in memory or not isinstance(glyph,str) or not glyph:raise ValueError("glyph")
  memory[address]=glyph
 classes={};events=[]
 for t in range(ticks):
  for core in range(4):
   address=f"{ROWS[core*4+t//16]}{t%16+1}";glyph=memory[address]
   if glyph!="." and glyph not in classes:classes[glyph]=f"χ{len(classes)+1:03d}"
   char=classes.get(glyph,".")
   events.append({"tick":t,"core":core,"address":address,"glyph":glyph,"character":char,"instruction":"READ" if char!="." else "HOLD"})
 result={"cores":4,"cells":256,"ticks":ticks,"processed":len(events),"known":sum(e["instruction"]=="READ" for e in events),"unknown":sum(e["instruction"]=="HOLD" for e in events),"events":events}
 result["trace_sha256"]=hashlib.sha256(json.dumps(result,sort_keys=True,ensure_ascii=False).encode()).hexdigest()
 return result
if __name__=="__main__":
 r=run();print(json.dumps({k:v for k,v in r.items() if k!="events"},indent=2))
