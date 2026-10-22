# Step 7 — reverse traversal /vogel/voxel/vector/sda/{drive}

[Interactive Step 7](step7-reverse.html) · [Step 6](step6-isomorphic.html)

Read the given stack backwards starting at {drive}:

```text
{drive} -> sda -> vector -> voxel -> vogel
```

Canonical datum is the IT3/v1 16-byte timestamp payload. We preserve the packet exactly.

- **{drive}**: immutable logical byte payload; no physical disk access.
- **sda**: ordered byte offsets in a logical sector-neutral storage view; not Linux device I/O.
- **vector**: 16 ordered pairs (index, byte).
- **voxel**: deterministic 4x4 mapping (x=index%4, y=index//4, z=byte), with index recoverable as 4*y+x.
- **vogel**: visual tessellation/projection of those cells, preserving the original coordinates and z; geometry is not an alternative authoritative wire encoding.

Inverse: read z from voxel at x,y, store in packet[4*y+x], then invoke IT3 decoder; reject invalid header, parity, reserved bits, range. Note that reconstituting bytes alone is lossless, while a 2D perspective rendering alone is not uniquely invertible.

This is a symbolic geometry and educational transport view, not an operating system disk driver and not a physical model of spacetime.
