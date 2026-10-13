#!/usr/bin/env python3
"""KET exact GREEN CHARIOT mnemonic; independent of physics or life claims."""
import json
from collections import Counter
AMPLITUDES=("red","green","blue","orange","purple","green","yellow")
CARRIERS=("white","black","gray")
GLYPH=r"123 {{45/|\54}} 678"
HINGE=chr(47)+chr(124)+chr(92)
def registry():
    return {
      "schema":"KET/GREEN_CHARIOT/v16",
      "lineage_root":"LEVIATHAN::0root",
      "pinned_zero":0,
      "amplitudes":[{"id":"A"+str(i+1),"color":c} for i,c in enumerate(AMPLITUDES)],
      "carriers":[{"id":"C"+str(i+1),"color":c} for i,c in enumerate(CARRIERS)],
      "chariot":{"name":"GREEN","literal":GLYPH,"left_green_id":"A2",
        "right_green_id":"A6","wing_left":[1,2,3],"inner_left":[4,5],
        "hinge":HINGE,"inner_right":[5,4],"wing_right":[6,7,8],
        "stations_unique":list(range(1,9)),
        "merges_green_ids":False,
        "physical_semantics":"not assigned"},
      "operators":["gravity","expansion","compression","containment","explosion"],
      "local_budget":366,"parent_budget":6006}
def validate(d):
    c=d["chariot"]
    assert d["pinned_zero"]==0
    assert len(d["amplitudes"])==7 and len(d["carriers"])==3
    assert [x["color"] for x in d["amplitudes"]]==list(AMPLITUDES)
    assert Counter(AMPLITUDES)["green"]==2
    assert c["left_green_id"]=="A2" and c["right_green_id"]=="A6"
    assert c["left_green_id"]!=c["right_green_id"]
    assert c["literal"]==GLYPH
    assert c["inner_left"]==[4,5] and c["inner_right"]==[5,4]
    assert c["hinge"]==HINGE
    assert sorted(set(c["wing_left"]+c["inner_left"]+c["inner_right"]+c["wing_right"]))==list(range(1,9))
    assert c["merges_green_ids"] is False
    assert d["local_budget"]==250+110+6
    assert d["parent_budget"]==100*3*20+6
    return True
if __name__=="__main__":
    data=registry()
    assert validate(data)
    print(json.dumps(data,sort_keys=True,indent=2))
