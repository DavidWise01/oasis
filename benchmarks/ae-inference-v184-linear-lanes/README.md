# Linear-lane scaling benchmark

Semantics under test:

    1 = one independent linear execution lane
    i = one agent/carrier

Each lane executes the already-verified synchronized cubic primitive with its
own inference engine and no shared fact set.

The benchmark measures 1, 2, 4, and 8 process lanes. The GitHub runner exposes
4 CPUs, so 8 lanes is an intentional oversubscription/saturation point.

Per completed cubic cycle:
- 55 kernel tokens (one derived atom = one kernel token)
- 322 symbolic sub-tokens
- 48 state transitions
