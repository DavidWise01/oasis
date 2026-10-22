"""Deterministic 3-replica quorum-ledger model, not a deployed consensus protocol."""
from dataclasses import dataclass
from hashlib import sha256
from struct import pack
NODES = ('a', 'b', 'c')
GENESIS = bytes(32)
def digest(term, index, prior, payload):
    if len(payload) != 16 or len(prior) != 32: raise ValueError('invalid record')
    return sha256(b'IT3L1' + pack('>QQ', term, index) + prior + payload).digest()
@dataclass(frozen=True)
class Entry:
    term: int
    index: int
    prior: bytes
    payload: bytes
    hash: bytes
class Model:
    def __init__(self):
        self.logs = {node: [] for node in NODES}
        self.committed = []
        self.term = 1
    def append(self, payload, acknowledgers):
        if len(payload) != 16 or payload[:4] != b'IT3\x01':
            raise ValueError('invalid packet header')
        prior = self.committed[-1].hash if self.committed else GENESIS
        entry = Entry(self.term, len(self.committed)+1, prior, payload,
                      digest(self.term, len(self.committed)+1, prior, payload))
        voters = set(acknowledgers)
        if not voters <= set(NODES): raise ValueError('unknown replica')
        ready = {node for node in voters if self.logs[node] == self.committed}
        for node in ready: self.logs[node].append(entry)
        if len(ready) >= 2:
            self.committed.append(entry)
            return True
        return False
    def repair(self, node):
        self.logs[node] = self.committed.copy()
    def verify(self):
        prior = GENESIS
        for index, entry in enumerate(self.committed, 1):
            assert entry.index == index and entry.prior == prior
            assert digest(entry.term, entry.index, prior, entry.payload) == entry.hash
            prior = entry.hash
def packet(seconds):
    import struct
    q,p = divmod(seconds,86400)
    return b'IT3\x01' + struct.pack('>qI',q,((q&1)<<31)|p)
def test():
    m = Model()
    assert m.append(packet(2147483648),['a','b'])
    print('PASS majority commit')
    assert not m.append(packet(4102444800),['a'])
    assert len(m.committed)==1
    print('PASS minority not committed')
    m.repair('a');m.repair('b');m.repair('c')
    assert m.append(packet(4102444800),['b','c'])
    print('PASS recovered majority')
    m.verify()
    print('PASS hash chain')
    e=m.committed[-1]
    assert digest(e.term,e.index,e.prior,packet(0)) != e.hash
    print('PASS tamper detection')
    m.repair('a'); assert m.logs['a']==m.committed
    print('PASS replica catch-up')
    print('RESULT: 6/6 PASS (in-memory model)')
if __name__=='__main__':test()
