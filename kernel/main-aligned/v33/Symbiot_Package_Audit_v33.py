#!/usr/bin/env python3
"""Symbiot package audit v33."""
import hashlib, pathlib, struct, sys
ROOT=pathlib.Path(sys.argv[1] if len(sys.argv)>1 else ".").resolve()
def git_blob_sha(data):
    return hashlib.sha1(("blob %d\0"%len(data)).encode()+data).hexdigest()
def check_boot(path):
    b=path.read_bytes()
    si=int.from_bytes(b[1:3],"little")-0x7c00 if len(b)>=3 and b[0]==0xBE else None
    lod=3 if len(b)>3 and b[3]==0xAC else None
    j=next((i for i in range(3,min(24,len(b)-1)) if b[i]==0xEB),None)
    target=None
    if j is not None:
        target=j+2+struct.unpack("b",bytes([b[j+1]]))[0]
    return {"bytes":len(b),"sha256":hashlib.sha256(b).hexdigest(),"git_blob":git_blob_sha(b),"55aa":b[-2:]==b"\x55\xaa","si_offset":si,"lodsb_offset":lod,"loop_target":target}
for name in ["symbiosis_boot.bin","symbiosis_boot_FIXED.bin","symbiosis_boot(1).bin","symbiosis_boot_FIXED(1).bin"]:
    p=ROOT/name
    if p.exists():
        x=check_boot(p); print(name,x); print("  loop returns to LODSB:",x["loop_target"]==x["lodsb_offset"])
def effective_hz(freq):
    return 1000/max(25,100000/freq)
for f in (100,1000,10000,50000):
    print("requested",f,"Hz -> JS timer",effective_hz(f),"Hz")
