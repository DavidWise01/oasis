# Base 1i arity/cubic closure test

Canonical structure under test:

    {{0::{i::1i::uniary::binary::ternary::quarterny::cubic::-+}}}

Structural chain:

    1i
    -> uniary(1i)
    -> binary(1i,1i)
    -> ternary(1i,1i,1i)
    -> quarterny(1i,1i,1i,1i)
    -> cubic(-,1i)
    -> cubic(+,1i)
    -> cubic_closed(1i)

The exact test requires both cubic sides for closure. Synthetic replicated
carriers are used only to benchmark scaling and do not redefine the canonical
base 1i literal.
