"""Symbolic chemical cipher: address-preserving nested zipper with invertible crossing."""
from dataclasses import dataclass
import random
@dataclass(frozen=True)
class Cell:
    address: int
    value: int
@dataclass(frozen=True)
class Nest:
    core: tuple[Cell, ...]
    extension: tuple[Cell, ...]
    crossed: tuple[Cell, ...]
def interleave(a, b):
    out=[]
    for i in range(max(len(a),len(b))):
        if i<len(a): out.append(a[i])
        if i<len(b): out.append(b[i])
    return tuple(out)
def encode(core, extension):
    core=tuple(core); extension=tuple(extension)
    if len(core)!=10 or len(extension)!=8: raise ValueError('expected 10+8 cells')
    entries=core+extension
    if [c.address for c in entries]!=list(range(1,19)): raise ValueError('addresses must be 1..18')
    if any(type(c.value) is not int or not 0<=c.value<=255 for c in entries): raise ValueError('byte value required')
    return Nest(core,extension,interleave(core,tuple(reversed(extension))))
def decode(nest):
    if not isinstance(nest,Nest): raise ValueError('nest required')
    reconstructed=interleave(nest.core,tuple(reversed(nest.extension)))
    if nest.crossed!=reconstructed: raise ValueError('crossing mismatch')
    if len(nest.core)!=10 or len(nest.extension)!=8: raise ValueError('invalid lengths')
    if [c.address for c in nest.core+nest.extension]!=list(range(1,19)): raise ValueError('address mismatch')
    return nest.core+nest.extension
def test():
    rng=random.Random(2038)
    for _ in range(10000):
        cells=tuple(Cell(i,rng.randrange(256)) for i in range(1,19))
        nested=encode(cells[:10],cells[10:])
        assert decode(nested)==cells
        assert decode(nested)[:10]==cells[:10]
        assert nested.crossed!=cells
    print('PASS: 10000 nested/crossed/inverse round trips, ancestral prefix preserved')
    cells=tuple(Cell(i,i) for i in range(1,19))
    n=encode(cells[:10],cells[10:])
    from dataclasses import replace
    for corrupt in [replace(n,crossed=n.crossed[:-1]),replace(n,crossed=n.crossed[::-1]),replace(n,extension=n.extension[:-1]),replace(n,core=n.core[:-1]),replace(n,extension=(Cell(10,2),)+n.extension[1:])]:
        try: decode(corrupt)
        except ValueError: pass
        else: raise AssertionError('malformed nest accepted')
    print('PASS: 5 malformed structure cases rejected')
    print('RESULT: PASS (symbolic test, not atomic physical claim)')
if __name__=='__main__': test()
