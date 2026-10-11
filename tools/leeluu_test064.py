#!/usr/bin/env python3
"""LEELUU Test 064: byte/source verification and five-layer crop manifest.
Usage:
  python tools/leeluu_test064.py --commons The_Engine_Gulliver.png --original lagado_16x16_source.png --out test064
No image is claimed independent solely because its byte hash differs.
"""
import argparse, hashlib, json
from pathlib import Path
from PIL import Image, ImageChops

targets=["K8","L8","M8","N8","M9","N9"]

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def crop_grid(img, cell, box):
    # Manual registration points are mandatory; do not infer plate bounds silently
    col=int(cell[1:])-1
    row=ord(cell[0])-ord("A")
    x0,y0,x1,y1=box
    return img.crop((round(x0+(x1-x0)*col/16),round(y0+(y1-y0)*row/16),
        round(x0+(x1-x0)*(col+1)/16),round(y0+(y1-y0)*(row+1)/16)))

def code16(im, threshold=128):
    # 4x4 binary occupancy approximates frozen v52 representation;
    # NOT claimed bit-identical without comparison to frozen extractor.
    im=im.convert("L").resize((4,4),Image.Resampling.BOX)
    return ''.join('1' if x < threshold else '0' for x in im.getdata())

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--commons",required=True)
    p.add_argument("--original",required=True)
    p.add_argument("--out",default="test064")
    p.add_argument("--commons-box",nargs=4,type=float,required=True,help="left top right bottom grid edges")
    p.add_argument("--original-box",nargs=4,type=float,required=True,help="left top right bottom grid edges")
    a=p.parse_args()
    out=Path(a.out);out.mkdir(exist_ok=True,parents=True)
    ims={}
    for name,path,box in [("commons",a.commons,a.commons_box),("original",a.original,a.original_box)]:
        im=Image.open(path)
        ims[name]=im
        print(name,"size",im.size,"sha256",sha(path))
    d={}
    for cell in targets:
        row={}
        for name,img in ims.items():
            box=a.commons_box if name=="commons" else a.original_box
            crop=crop_grid(img,cell,box)
            crop.save(out / f"{name}_{cell}.png")
            row[name]=code16(crop)
        row["hamming_exploratory"]=sum(x!=y for x,y in zip(row["commons"],row["original"]))
        d[cell]=row
    report={"warning":"Exploratory only: human-set grid coordinates, not frozen v52 extraction; independent photographic provenance unverified.", "source_hashes":{"commons":sha(a.commons),"original":sha(a.original)},"cells":d}
    (out/"report.json").write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(report,indent=2))

if __name__=="__main__":
    main()
