# {{i & dd}} — Coupled Diamond Processor v0.2

Separate, reversible processor extension of the existing frozen {{i}} and new {{d}} v0.1 four-port/three-coupler language. Frozen KET and isomorphic v111 are unchanged.

**Structure:** {{i}} is the original coordinate-distinct address stream; d+ encodes that stream in forward order; d- encodes it in reverse order. Both use the symbolic frame |.|.|.| (four ports and three explicit path links). Two projected rails, one identity register, one witness.

**Invariant:**

    decode(d+) = reverse(decode(d-)) = i

The two rails have independently addressable view projections (v0-v7). A SHA-256 identity seal hashes (source view, original address list, parent, generation) and is invariant under projecting either rail. A SHA-256 witness hashes the identity seal and both projected serialized carriers; it changes when rails are reprojected. Neither hash is a signature or proof of independent witnesses. The decoder checks inverse recovery, seals, frame validity, address ranges, padding, lengths, and lineage structure.

A double mirror-reverse operation restores stream geometry but creates two additional append-only generations and therefore never restores the former identity seal. A 42-symbol stream occupies 11 cells per rail = 22 total cells, each nominally 4/3.

**Mathematical quantum sidecar:** Qubit order [i_branch, d+, d-], pure 3-qubit state

    |psi> = (|001> + |110>) / sqrt(2)

Only two of eight basis states have nonzero probability, each 1/2. For each qubit, its reduced density matrix is I/2, purity = 0.5. This is an entangled state *in classical statevector simulation*. The logical qubit i_branch represents a branch bit, not the immutable 42-token {{i}} identity. This software neither runs a physical quantum processor nor establishes physical entanglement, quantum speedup, or fault-tolerant quantum error correction.

**API:** See i-dd-processor.mjs exports bindTwin, recoverTwin, rotateTwin, nextGeneration, mirrorReverse, serializeTwin, deserializeTwin. See three-qubit.mjs for STATE, distribution, reducedSingle, purity, measure. Run local package benchmark.mjs for tested cases (2,688 source/destination path positions, 5,397 classical checks plus mathematical statevector checks). Full high-definition SVG blueprint and benchmark are in the downloadable project package.
