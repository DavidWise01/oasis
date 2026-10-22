"""Lossless 16-byte IT3 packet <-> ordered 4x4 voxel registry."""
from dataclasses import dataclass

@dataclass(frozen=True)
class Voxel:
    x: int
    y: int
    z: int

def encode(packet: bytes) -> tuple[Voxel, ...]:
    if len(packet) != 16:
        raise ValueError("exactly 16 bytes required")
    return tuple(Voxel(i % 4, i // 4, b) for i, b in enumerate(packet))

def decode(voxels) -> bytes:
    result = bytearray(16)
    seen = set()
    items = tuple(voxels)
    if len(items) != 16:
        raise ValueError("exactly 16 voxels required")
    for v in items:
        if type(v.x) is not int or type(v.y) is not int or type(v.z) is not int:
            raise ValueError("integer coordinates required")
        if not (0 <= v.x < 4 and 0 <= v.y < 4 and 0 <= v.z <= 255):
            raise ValueError("voxel out of range")
        index = 4 * v.y + v.x
        if index in seen:
            raise ValueError("duplicate coordinate")
        seen.add(index)
        result[index] = v.z
    return bytes(result)
