"""Step 8: golden IT3 + deterministic voxel round trips, including mutations."""
import json
import random
from pathlib import Path
from voxel import Voxel, encode, decode
from it3 import decode as decode_it3

vectors = json.loads(Path(__file__).with_name("it3-vectors.json").read_text())
assert len(vectors) == 8
for v in vectors:
    packet = bytes.fromhex(v["hex"])
    voxels = encode(packet)
    assert decode(voxels) == packet
    assert decode_it3(decode(voxels)) == int(v["seconds"])
    shuffled = list(voxels)
    random.Random(5).shuffle(shuffled)
    assert decode(shuffled) == packet

rng = random.Random(2038)
for _ in range(10000):
    packet = rng.randbytes(16)
    assert decode(encode(packet)) == packet

voxels = list(encode(bytes(range(16))))
malformed = [
    voxels[:-1],
    voxels + [voxels[0]],
    voxels[:1] + [voxels[0]] + voxels[2:],
    [Voxel(4,0,1)] + voxels[1:],
    [Voxel(0,0,256)] + voxels[1:],
]
for candidate in malformed:
    try:
        decode(candidate)
    except ValueError:
        pass
    else:
        raise AssertionError("malformed voxel layout accepted")
print("PASS: 8 IT3 golden packets, 10000 deterministic arbitrary byte payloads, shuffled ordering, 5 malformed layouts")
