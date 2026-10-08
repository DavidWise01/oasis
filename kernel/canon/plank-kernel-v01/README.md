# Plank Kernel v01

Status: **CANONICAL / INTERACTIVE KERNEL INSTRUMENT**

Source: `Plank-Kernel.html`  
Source SHA-256: `607a2bbb1f745f39066a91eb039f2d8c7fe9fd9aac4caa55e07e32e4563a32bd`

## Preserved structure

The uploaded instrument is stored unchanged as the canonical HTML source.

Its implemented model includes:

- six alternating signed poles: `−e,+e,−p,+p,−n,+n`;
- a fail-closed net-pole invariant gate;
- two opposed / counter-rotating bubbles;
- six distinct edge angular rates;
- three internal ring categories: weak, med, strong;
- four force points per ring category;
- mutation receipts for edge crossings, ring reorderings, and near-harmony;
- scale-fallout readouts for shell shear, ring split, mutation flux, and field RMS;
- an interactive self-test;
- explicit source caveat that motion uses dimensionless kernel units and is not a claim about established particle physics.

## Core invariant

```text
signs = -1,+1,-1,+1,-1,+1
net pole = 0
```

The stepper fails closed if the signed pole magnitude drifts from zero:

```text
DECOHERENCE: net pole drift
```

## Placement

This is a canonical kernel instrument under `kernel/canon/`. It is additive support and does not silently replace the separately aligned/frozen kernel trunks.
