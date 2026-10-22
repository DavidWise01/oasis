"""Step 13: deterministic Raft election/log-matching model; no network or durable consensus."""
from dataclasses import dataclass,field
@dataclass(frozen=True)
class Entry:
    term:int
    data:bytes
@dataclass
class Node:
    name:str
    term:int=0
    voted_for:str|None=None
    log:list[Entry]=field(default_factory=list)
    role:str='follower'
    def last(self):
        return (len(self.log),self.log[-1].term if self.log else 0)
    def request_vote(self,term,candidate,last_index,last_term):
        if term<self.term:return False
        if term>self.term:self.term,self.voted_for,self.role=term,None,'follower'
        idx,tm=self.last()
        if (last_term,last_index)>=(tm,idx) and self.voted_for in (None,candidate):
            self.voted_for=candidate
            return True
        return False
    def append_entries(self,term,leader,prev_index,prev_term,entries):
        if term<self.term:return False
        if term>self.term:self.term,self.voted_for=term,None
        self.role='follower'
        if prev_index>len(self.log):return False
        if prev_index and self.log[prev_index-1].term!=prev_term:return False
        pos=prev_index
        for entry in entries:
            if pos<len(self.log) and self.log[pos]!=entry:del self.log[pos:]
            if pos==len(self.log):self.log.append(entry)
            pos+=1
        return True
class Cluster:
    def __init__(self):
        self.nodes={name:Node(name) for name in 'abc'}
        self.leader=None
    def elect(self,name,reachable):
        candidate=self.nodes[name]
        term=max(n.term for n in self.nodes.values())+1
        idx,last_term=candidate.last()
        votes=sum(self.nodes[n].request_vote(term,name,idx,last_term) for n in reachable)
        if votes>=2 and name in reachable:
            candidate.role='leader';self.leader=name
            return True
        self.leader=None
        return False
    def propose(self,name,data,reachable):
        leader=self.nodes[name]
        if self.leader!=name or leader.role!='leader' or len(reachable)<2 or name not in reachable:return False
        index=len(leader.log)
        prev_term=leader.log[-1].term if index else 0
        entry=Entry(leader.term,data);ok=1
        for follower in reachable:
            if follower!=name and self.nodes[follower].append_entries(leader.term,name,index,prev_term,[entry]):ok+=1
        if ok<2:return False
        leader.log.append(entry)
        return True
def test():
    c=Cluster()
    assert c.elect('a',{'a','b','c'});print('PASS initial majority election')
    assert c.propose('a',b'IT3\x01',{'a','b'}) and len(c.nodes['a'].log)==len(c.nodes['b'].log)==1
    print('PASS majority log propagation')
    assert not c.elect('c',{'b','c'});print('PASS stale-log candidate rejected')
    assert c.elect('b',{'b','c'});print('PASS up-to-date candidate elected')
    assert c.nodes['a'].append_entries(3,'b',1,1,[])
    assert not c.nodes['a'].append_entries(1,'a',1,1,[Entry(1,b'bad')]);print('PASS stale leader term rejected')
    assert not c.nodes['b'].append_entries(2,'a',1,999,[Entry(2,b'bad')]);print('PASS log conflict term rejected')
    assert c.nodes['c'].append_entries(3,'b',0,0,c.nodes['b'].log)
    assert c.nodes['c'].log==c.nodes['b'].log;print('PASS follower catches up')
    assert not c.propose('b',b'next',{'b'});print('PASS isolated leader cannot claim quorum')
    print('RESULT 8/8 PASS — deterministic model only')
if __name__=='__main__':test()
