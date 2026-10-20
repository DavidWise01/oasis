# N184 Jellyfish Gravity-Web — v7.3

**Status:** additive symbolic visualization, not a general-relativistic simulation.

The new arrangement is **five identical copies of Universe 1 in an upper canopy plus four copies below**: 9 independently addressable positions, each reading the exact same source register from [Sag A universe v7.2](../universe-sag-a-v72/spec.json).

## Topology

```text
            U1     U2     U3     U4     U5       upper canopy (5)
             \    / \    / \    / \    /
              L1       L2      L3      L4       lower tendrils (4)
                  stretched / drooping mesh
```

Exactly 8 connecting upper-to-lower tethers create one connected, cycle-free nine-node scaffold. Each of the nine nodes is a **reference**, not a separately invented type of universe.

## Contents of each identical instance

- Center: **Sag A** (symbolic stand-in labeled after the actual black hole Sagittarius A*, Sgr A*)
- Two symbolic counter-rotating **`-+ honey`** accretion disks
- Exactly six color-named symbolic suns, in source order:
  1. Xerses — white
  2. Argon — red
  3. Krypton — white
  4. Nemesis — blue
  5. He — orange
  6. Ne — purple

The v7.2 master register is read at runtime and checked for center, ring size and disks.

## Controls

- Animate/pause, reset
- Change *web sag* continuously from 0 to 1.6 (dimensionless)
- Change visual perspective tilt
- Toggle curved mesh
- Click any clone to inspect its label and tier

## Physical boundary

An Einstein-style gravity well is a familiar visualization of curved geometry. It **does not** mean gravity pulls a literal space fabric downward into an extra spatial direction. General relativity describes the four-dimensional metric of spacetime. A hanging jellyfish web, identical parallel universes, and curved tethers are **artistic/modeling choices only**. The web's sag function and movements are not Einstein-equation solutions.

## Lineage / validation

- Canonical source: [Universe 1 / Sag A v7.2](../universe-sag-a-v72/)
- Earlier versions: [Neodymium hex v7.1](../noble-hex-v71/), [Four-Wave v7.0](../noble-gas-four-wave-v70/)
- Simulation: [index.html](./index.html)
- Topology: [spec.json](./spec.json)
- Deterministic topology checks: `node n184/jellyfish-web-v73/test_web.mjs`

The frozen N184 60×40 lattice, previous noble-gas registers, prior Nd-centered geometry, and original Sag A model are not changed.
