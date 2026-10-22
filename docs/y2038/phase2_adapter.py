"""Phase 2: strict transport boundary to an EXTERNAL, proven linearizable Raft store.

No simulated quorum is used here. This module does not implement or launch Raft.
An operator supplies a preconfigured backend implementing Backend.submit/read.
"""
from __future__ import annotations
from dataclasses import dataclass
from hashlib import sha256
from typing import Protocol
from it3 import encode, decode

class Backend(Protocol):
    def submit(self, key: bytes, value: bytes) -> tuple[int, bytes]:
        """Return (committed_revision, readback_value) AFTER quorum commit."""
    def read(self, key: bytes) -> tuple[int, bytes]:
        """Perform a LINEARIZABLE read; return (revision,value)."""

@dataclass(frozen=True)
class Receipt:
    revision: int
    packet_sha256: str
    unix_seconds: int

class CommitNotVerified(RuntimeError):
    pass

def publish(backend: Backend, record_id: str, unix_seconds: int) -> Receipt:
    if not isinstance(record_id, str) or not (1 <= len(record_id) <= 128):
        raise ValueError("record_id length")
    if not record_id.isascii() or not all(c.isalnum() or c in "-_" for c in record_id):
        raise ValueError("record_id syntax")
    packet = encode(unix_seconds)
    key = ("it3/v1/" + record_id).encode("ascii")
    try:
        revision, committed = backend.submit(key, packet)
        if type(revision) is not int or revision < 1 or committed != packet:
            raise CommitNotVerified("backend did not confirm committed bytes")
        read_revision, read_value = backend.read(key)
        if (type(read_revision) is not int or read_revision < revision
                or read_value != packet or decode(read_value) != unix_seconds):
            raise CommitNotVerified("linearizable readback failed")
    except (OSError, TimeoutError, ConnectionError) as exc:
        raise CommitNotVerified("backend unavailable; commit outcome unknown") from exc
    return Receipt(revision, sha256(packet).hexdigest(), unix_seconds)
