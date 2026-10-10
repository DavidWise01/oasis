"""Gate 13: symbolic SAPPHON dot-clock crosswalk; not historical decoding."""
from math import lcm
PERIODS=(260,365,584)
def state(day):
    return tuple(day % n for n in PERIODS)
def tick(day, events):
    events.append((day, 'dot', state(day)))
    events.append((day+1, 'sapphon', state(day+1)))
    return day+1
def verify():
    assert sum((1,1,2,4))==8
    assert 236+90+250+8==584
    assert lcm(260,365)==18980
    assert 5*584==8*365==2920
    assert 65*584==104*365==146*260==37960
    assert lcm(*PERIODS)==37960
    assert state(0)==state(37960)==(0,0,0)
    assert state(18980)[:2]==(0,0) and state(18980)[2]!=0
    events=[]; day=0
    for _ in range(20):day=tick(day,events)
    assert day==20 and len(events)==40 and events[0][1]=='dot' and events[1][1]=='sapphon'
    assert all(events[i][0]<=events[i+1][0] for i in range(len(events)-1))
    print('PASS 10/10 checks')
    print('Calendar Round:',lcm(260,365),'days')
    print('Triple alignment:',lcm(*PERIODS),'days')
    print('20 day simulation:',state(day),'events:',len(events))
if __name__=='__main__':verify()
