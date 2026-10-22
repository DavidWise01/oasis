"""Optimized 184/257 symbolic frame. Compatible with prior schema."""
import hashlib,random,struct,time
SIZE=257
PACK=struct.Struct('>I')
def instantiate(data,generation=0):
    if len(data)!=184 or not 0<=generation<2**32:raise ValueError('bad inputs')
    frame=bytearray(SIZE);frame[0]=0xa1;frame[1:185]=data
    PACK.pack_into(frame,185,generation)
    frame[189:221]=hashlib.sha256(data).digest()
    return frame
def turnover_in_place(frame,generation):
    if type(frame)!=bytearray or len(frame)!=SIZE or not 0<=generation<2**32:raise ValueError('bad frame')
    PACK.pack_into(frame,185,generation)
def verify(frame):
    return (len(frame)==SIZE and frame[0]==0xa1 and
            frame[221:]==bytes(36) and
            hashlib.sha256(frame[1:185]).digest()==frame[189:221])
def recover(frame):
    if not verify(frame):raise ValueError('invalid frame')
    return bytes(frame[1:185]),PACK.unpack_from(frame,185)[0]
def test():
    r=random.Random(184257)
    for _ in range(10000):
        data=r.randbytes(184);g=r.randrange(2**32);frame=instantiate(data,g)
        assert recover(frame)==(data,g)
        frozen=bytes(frame[:185]+frame[189:])
        for step in (1,2,3):
            new=(g+step)%(2**32);turnover_in_place(frame,new)
            assert recover(frame)==(data,new)
            assert bytes(frame[:185]+frame[189:])==frozen
    frame=instantiate(bytes(range(184)));frame[12]^=1;assert not verify(frame)
    frame=instantiate(bytes(range(184)));frame[256]=1;assert not verify(frame)
    print('PASS 10,000 frames; 30,000 turnovers; corruption rejection')
def bench(n=100000):
    data=bytes(range(184))
    start=time.perf_counter()
    for i in range(n):
        frame=bytearray(257);frame[0]=0xa1;frame[1:185]=data
        frame[185:189]=i.to_bytes(4,'big')
        frame[189:221]=hashlib.sha256(data).digest()
    old=time.perf_counter()-start
    frame=instantiate(data);start=time.perf_counter()
    for i in range(n):turnover_in_place(frame,i)
    new=time.perf_counter()-start
    assert recover(frame)[1]==n-1
    print(f'full rebuild {old:.6f}s, in-place {new:.6f}s, speedup {old/new:.2f}x')
if __name__=='__main__':test();bench()
