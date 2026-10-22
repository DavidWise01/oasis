"""Step 9: bounded file persistence and interrupted staging recovery tests.
No physical disk power-loss guarantee is claimed.
"""
import hashlib
import os
import tempfile
from pathlib import Path
from it3 import encode, decode
from voxel import encode as to_voxels, decode as from_voxels

MAGIC = b'IT3S'

def frame(timestamp: int) -> bytes:
    packet = encode(timestamp)
    return MAGIC + packet + hashlib.sha256(packet).digest()

def validate(blob: bytes) -> int:
    if len(blob) != 52 or blob[:4] != MAGIC:
        raise ValueError('invalid record length/magic')
    packet = blob[4:20]
    if hashlib.sha256(packet).digest() != blob[20:]:
        raise ValueError('digest mismatch')
    if from_voxels(to_voxels(packet)) != packet:
        raise ValueError('voxel mismatch')
    return decode(packet)

def write_sync(path: Path, content: bytes) -> None:
    with path.open('wb') as fp:
        fp.write(content)
        fp.flush()
        os.fsync(fp.fileno())

def run() -> None:
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        current, staging = root/'current.it3s', root/'pending.it3s'
        old = 2147483648
        newer = 4102444800
        original = frame(old)
        write_sync(current, original)
        assert validate(current.read_bytes()) == old
        print('PASS: committed record readback')
        with staging.open('wb') as fp:
            fp.write(frame(newer)[:13])
            fp.flush()
            os.fsync(fp.fileno())
        try:
            validate(staging.read_bytes())
            raise AssertionError('partial staging accepted')
        except ValueError:
            pass
        assert validate(current.read_bytes()) == old
        print('PASS: truncated staging rejected; committed record preserved')
        corrupt = bytearray(frame(newer))
        corrupt[9] ^= 1
        write_sync(staging, corrupt)
        try:
            validate(staging.read_bytes())
            raise AssertionError('corrupted staging accepted')
        except ValueError:
            pass
        assert validate(current.read_bytes()) == old
        print('PASS: corrupted staging rejected; committed record preserved')
        write_sync(staging, frame(newer))
        assert validate(staging.read_bytes()) == newer
        os.replace(staging, current)
        assert validate(current.read_bytes()) == newer
        print('PASS: valid staged record replaces committed record')
        assert not staging.exists()
        print('PASS: staging path consumed by replace')
        try:
            validate(original[:-1])
            raise AssertionError('truncated frame accepted')
        except ValueError:
            pass
        print('PASS: truncated committed frame rejected')
    print('RESULT: 6/6 PASS')

if __name__ == '__main__':
    run()
