"""Tested locally: 184 data addresses inside 257 positions, with simulated generations."""
import hashlib,random
def encode(data,generation):
    if len(data)!=184 or not 0<=generation<2**32:raise ValueError('invalid size or generation')
    out=bytearray(257);out[0]=0xa1;out[1:185]=data
    out[185:189]=generation.to_bytes(4,'big')
    out[189:221]=hashlib.sha256(data).digest()
    return bytes(out)
def decode(frame):
    if len(frame)!=257 or frame[0]!=0xa1 or any(frame[221:]):raise ValueError('invalid frame')
    data=frame[1:185]
    if hashlib.sha256(data).digest()!=frame[189:221]:raise ValueError('digest mismatch')
    return data,int.from_bytes(frame[185:189],'big')
def test():
    rng=random.Random(184257)
    for _ in range(10000):
        data=bytes(rng.randrange(256) for _ in range(184));g=rng.randrange(2**32)
        frame=encode(data,g)
        assert decode(frame)==(data,g)
        for d in (1,2,3):
            rotated=encode(data,(g+d)%(2**32))
            assert decode(rotated)==(data,(g+d)%(2**32))
            assert rotated[1:185]==frame[1:185]
    print('PASS 10000 records and 30000 turnovers')
    data=bytes(range(184));f=bytearray(encode(data,3));f[4]^=1
    try:decode(f)
    except ValueError:pass
    else:raise AssertionError('accepted payload corruption')
    f=bytearray(encode(data,3));f[256]=1
    try:decode(f)
    except ValueError:pass
    else:raise AssertionError('accepted reserved metadata')
    print('PASS corrupted payload and illegal reserved metadata rejected')
if __name__=='__main__':test()
