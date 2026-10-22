# Step 8 — Formal voxel transport for {{i}}

Canonical traversal (read from right): `/vogel/voxel/vector/sda/{drive}`.

A packet is exactly 16 octets `b[0..15]`. The canonical voxel set comprises precisely sixteen records `(x,y,z)` such that `x=i mod 4`, `y=floor(i/4)`, `z=b[i]`. Decoder requires exactly one voxel for each `(x,y)` in `[0,3]²`, each z an integer in `[0,255]`, and rejects out-of-domain, missing or duplicate coordinates.

Reconstruction is `b[4*y+x]=z`. The voxel sequence order is *not* authoritative: coordinates are. This makes it invariant to transport order, but not to changes in data. The rendering under `vogel` is lossy and must not be used as the byte source.

## Invariant

For any `b ∈ {0..255}^16`: `voxel_decode(voxel_encode(b)) = b`.

For an IT3-valid packet `b`: `IT3_decode(voxel_decode(voxel_encode(b))) = IT3_decode(b)`.

## Verification

```sh
cd docs/y2038
python3 check_voxel.py
```

The standalone check covers eight pinned IT3 packets, 10,000 fixed-seed arbitrary byte sequences, permutation invariance, and five malformed voxel layouts. It does **not** claim that arbitrary 16-byte payloads are IT3-valid. The decoder enforces spatial validity; `it3.decode` enforces timestamp packet validity.

An interactive browser visualization is available in [Step 7](step7-reverse.html). This Step 8 artifact is the formal, independent serializer implementation.
