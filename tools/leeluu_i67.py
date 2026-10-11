#!/usr/bin/env python3
"""LEELUU Test067: symbol inference i-pass; never manufactures transcriptions."""
import json,argparse
ROWS="ABCDEFGHIJKLMNOP"
def grid():return {f"{r}{c}":"." for r in ROWS for c in range(1,17)}
def ipass(chars):
    assert set(chars)==set(grid())
    readings={};symbols={}
    for addr,glyph in chars.items():
        if glyph!=".":symbols.setdefault(glyph,f"χ{len(symbols)+1:03d}")
        readings[addr]=symbols.get(glyph,".")
    edges=[]
    for ri,r in enumerate(ROWS):
        for c in range(1,17):
            a=f"{r}{c}"
            for b in ([f"{r}{c+1}"] if c<16 else [])+([f"{ROWS[ri+1]}{c}"] if ri<15 else []):
                edges.append((a,b))
    return {"cells":256,"resolved":sum(v!="." for v in readings.values()),
      "distinct_characters":len(symbols),"unresolved":sum(v=="." for v in readings.values()),
      "candidate_pairs":len(edges),
      "resolved_pairs":sum(readings[a]!="." and readings[b]!="." for a,b in edges),
      "motifs":{k:[readings[x] for x in seq] for k,seq in {
       "C8-C9":["C8","C9"],"A8-B8":["A8","B8"],
       "K8-L8":["K8","L8"],"M-square":["M8","N8","M9","N9"]}.items()},
      "dictionary":symbols}
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--transcription");a=p.parse_args()
    chars=grid()
    if a.transcription:
        src=json.load(open(a.transcription,encoding="utf8"))
        if not isinstance(src,dict) or set(src)-set(chars):raise ValueError("Invalid transcription")
        for addr,sym in src.items():
            if not isinstance(sym,str) or not sym:raise ValueError("Invalid glyph")
            chars[addr]=sym
    print(json.dumps(ipass(chars),ensure_ascii=False,indent=2))
