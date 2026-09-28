# Juliet / Mandel AMTSO Disposable Lab 00

The artifact is the disposable lab.

## Local safe checks
- canonical 68-byte EICAR
- renamed EICAR text file
- single ZIP
- nested/double ZIP
- benign text and ZIP controls

Run:

```bash
python runner/run_safe_checks.py
```

The runner does not execute samples and uses no network.

The official AMTSO live feature-check URLs are listed in `manifest.json`.
