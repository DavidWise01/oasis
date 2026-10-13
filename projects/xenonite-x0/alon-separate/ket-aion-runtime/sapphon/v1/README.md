# A.I.O.N. / ALON SAPPHON — versioned visualization adapter v1.0.0

**Scope:** Additive first-generation SAPPHON visualization inside the A.I.O.N./K.E.T.-aligned application runtime. Frozen OASIS/K.E.T. kernel source remains unchanged.

## Source of truth
- Physical geometry: original ALON crystal builder, seed 42, 7.95 Å, vacancy index 0.
- Formula: Al23O27N5; 55 occupied atoms, 122 modeled Al–anion contacts, and 42 chosen-cell periodic crossings.
- `model.json` and both HTML viewers contain identical reference coordinates and bonds; the adapter compares every site and bond with freshly generated crystal data.
- SAPPHON vessel, nested rings, and Jane/Patricia/Toph/Icarium color anchors are symbolic, not chemical atoms or evidence of electronic properties.

## Usage
```bash
python ket_aion.py --module sapphon --out ./aion-sapphon-run
python ket_aion.py --module all --out ./aion-all-run
```

Open `aion-sapphon-run/sapphon-v1/index.html` (offline/WebGL2 with software fallback). `threejs.html` uses Three.js 0.160.1 via CDN and requires an internet connection and a WebGL-capable browser.

This adapter exports SHA-256 hashes and a local hash-chained ledger; it is not signed durable provenance or a certified production kernel. ALON geometry is unrelaxed and pulse spectroscopy remains synthetic.
