"""Step 15: deterministic partition safety state-machine model, not full Raft."""
from dataclasses import dataclass, field

@dataclass
class Node:
    term: int = 0
    log: list[tuple[int, str]] = field(default_factory=list)
    commit: int = 0

class Cluster:
    def __init__(self):
        self.nodes = {name: Node() for name in 'ABC'}
        self.leader = None
        self.term = 0
        self.links = {frozenset((a,b)) for a in 'ABC' for b in 'ABC' if a!=b}

    def connected(self, a, b):
        return a == b or frozenset((a,b)) in self.links

    def partition(self, groups):
        self.links = {frozenset((a,b)) for g in groups for a in g for b in g if a != b}

    def reachable(self, a):
        return {b for b in self.nodes if self.connected(a,b)}

    def elect(self, candidate):
        reachable = self.reachable(candidate)
        if len(reachable) < 2:
            return False
        best = max((len(self.nodes[n].log), self.nodes[n].log[-1][0] if self.nodes[n].log else 0)
                   for n in reachable)
        local = self.nodes[candidate]
        position = (len(local.log), local.log[-1][0] if local.log else 0)
        if position < best:
            return False
        self.term += 1
        self.leader = candidate
        for n in reachable:
            self.nodes[n].term = self.term
        return True

    def commit(self, origin, payload):
        if origin != self.leader:
            return False
        reachable = self.reachable(origin)
        if len(reachable) < 2:
            return False
        leader = self.nodes[origin]
        if leader.term != self.term:
            return False
        prefix = leader.log[:]
        eligible = [n for n in reachable if self.nodes[n].log == prefix]
        if len(eligible) < 2:
            return False
        entry = (self.term, payload)
        for n in eligible:
            node = self.nodes[n]
            node.log.append(entry)
            node.commit = len(node.log)
        return True

    def heal(self):
        self.partition(['ABC'])

    def sync_from_leader(self):
        canonical = self.nodes[self.leader]
        for node in self.nodes.values():
            if node.log[:node.commit] != canonical.log[:node.commit]:
                raise AssertionError('committed prefix conflict')
            node.log = canonical.log[:]
            node.commit = canonical.commit
            node.term = max(node.term, self.term)

def test():
    c=Cluster()
    assert c.elect('A'); print('PASS initial leader')
    assert c.commit('A','IT3:2147483648'); print('PASS first majority commit')
    c.partition(['A','BC'])
    assert not c.commit('A','minority'); print('PASS isolated leader blocked')
    assert c.elect('B'); print('PASS majority elects new leader')
    assert not c.commit('A','stale'); print('PASS stale leader blocked')
    assert c.commit('B','IT3:4102444800'); print('PASS new majority commit')
    c.heal(); c.sync_from_leader()
    assert all(n.log == c.nodes['B'].log for n in c.nodes.values()); print('PASS healing converges')
    assert all(n.log[0][1]=='IT3:2147483648' for n in c.nodes.values()); print('PASS committed prefix unchanged')
    print('RESULT 8/8 PASS (bounded model)')

if __name__=='__main__': test()
