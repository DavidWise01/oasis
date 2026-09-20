# MORE GARBAGE — one-bit moji recursion v01

This supersedes the forward-tick interpretation in Prim1Bit.00.

Scope remains one bit only.

~~~text
find MOJI
   ↓
reverse walk

8
↓
3
↓
2
↓
1
~~~

At each unresolved stage, recurse through the same bounded anchor:

~~~text
0.[O].0
~~~

Stop as soon as the primitive resolves:

~~~text
Y → repair
N → no repair
~~~

The primitive cost signature remains:

~~~text
[ 1 1 2 4 ] . n . n²
~~~

Cohesion does not require waiting for a whole nibble in this model. The surviving state may still cohere from the literal seed:

~~~text
1.1 of a nibble
~~~

That applies after either Y or N. N still means the original primitive was not repaired; it does not prevent the surviving state from cohering from the 1.1 seed.

"1.1" is preserved literally here; no numerical reinterpretation is introduced.

Lean descendant:

~~~text
lean/Oasis.MoreGarbage.Prim1Bit.01.lean
~~~

Status: fresh candidate, pending user 0e.
