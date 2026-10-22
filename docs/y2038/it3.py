"""Independent Python codec for the proposed IT3/v1 time envelope."""
import struct
DAY = 86400
MIN64 = -(1 << 63)
MAX64 = (1 << 63) - 1

def encode(seconds: int) -> bytes:
    if not isinstance(seconds, int) or not MIN64 <= seconds <= MAX64:
        raise ValueError("signed int64 seconds required")
    turns, phase = divmod(seconds, DAY)
    field = ((turns & 1) << 31) | phase
    return b"IT3\x01" + struct.pack(">qI", turns, field)

def decode(packet: bytes) -> int:
    if len(packet) != 16 or packet[:4] != b"IT3\x01":
        raise ValueError("invalid header or length")
    turns, field = struct.unpack(">qI", packet[4:])
    if field & 0x7FFE0000:
        raise ValueError("reserved bits set")
    phase = field & 0x1FFFF
    if phase >= DAY or (field >> 31) != (turns & 1):
        raise ValueError("invalid phase or parity")
    seconds = turns * DAY + phase
    if not MIN64 <= seconds <= MAX64:
        raise ValueError("decoded time outside int64")
    return seconds

if __name__ == "__main__":
    for t in [MIN64, -2147483649, -1, 0, 2147483647,
              2147483648, 4102444800, MAX64]:
        wire = encode(t)
        assert decode(wire) == t
        broken = bytearray(wire)
        broken[12] ^= 0x40
        try:
            decode(broken)
        except ValueError:
            pass
        else:
            raise AssertionError("corrupted packet accepted")
        print(t, wire.hex(" ").upper(), "PASS")
