"""Phase 2.4: retry-safe create-only IT3 writes against a linearizable backend."""
from dataclasses import dataclass
from hashlib import sha256
from it3 import encode, decode
from phase2_etcd import EtcdConflict

class UncertainCommit(RuntimeError): pass
class IdentityConflict(RuntimeError): pass
@dataclass(frozen=True)
class Receipt:
    revision: int
    unix_seconds: int
    sha256: str
    outcome: str

def publish_once(backend, record_id, seconds):
    if not isinstance(record_id,str) or not 1 <= len(record_id) <= 128 or not record_id.isascii() or not all(c.isalnum() or c in '-_' for c in record_id):
        raise ValueError("invalid record id")
    packet=encode(seconds)
    key=('it3/v1/'+record_id).encode('ascii')
    outcome='created'
    revision=None
    try:
        revision, written=backend.submit(key,packet)
        if written!=packet or type(revision) is not int or revision<1:
            raise UncertainCommit("unverified write response")
    except EtcdConflict:
        outcome='existing'
    except (OSError,ConnectionError,TimeoutError):
        outcome='uncertain'
    try:
        read_revision,actual=backend.read(key)
    except (OSError,ConnectionError,TimeoutError,ValueError) as exc:
        raise UncertainCommit('linearizable read unavailable; no receipt') from exc
    if actual!=packet:
        raise IdentityConflict('existing key has different payload')
    if type(read_revision) is not int or read_revision<1 or (revision is not None and read_revision<revision):
        raise UncertainCommit('invalid/older read revision')
    if decode(actual)!=seconds:
        raise IdentityConflict('decoded identity mismatched')
    return Receipt(read_revision,seconds,sha256(packet).hexdigest(),outcome)
