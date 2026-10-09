# SHEET 152 — Release Receipt

```json
{
  "anchor-proof152.js": "e435a8627acf96f635c56906cf5bfdb481ee635d66826f1d2ec9bbb3889a696c",
  "anchor-server152.js": "f342d312d5539d61ffad82c39bb2decfbd4e8e41756e64938eb6e6ff2a4d77e4",
  "bridge152.js": "877635b1333e2ccdec9b879f2fed38c72113030e9f9f5866771a961f1d11757e",
  "gate152.js": "05c5471294a3e16a85df27f3e6f12cf7e32be1bb538cae9f5c81d5b63c38fac0",
  "reconcile152.js": "42b71633fc9da8116d3a855a2b233618807a629093515f7022ff8ed697b8f6bc",
  "replica152.js": "eb8b305afd7af89d961709178c7491ca645ac699dc73dbd545f3fb8690b1d57e",
  "resource152.js": "5f88207497fa74611d6ac37325260004a839164d37b2369488e98a6d58a779e5",
  "completeZipSha256": "bb2f590ca0c0054267573fd536fe3d2cd907dd2b34666706126a8ae90c431818",
  "baseline151FilesUnchanged": 482,
  "tests": "45 new; full chain total 1307; exit 0; Chromium 8 scenarios + export"
}
```

Limitations: one host; legacy S150 writer bound to 128 records; live-check/commit TOCTOU not fully serialized; original SHEET142 concurrency assertion is known to be timing-sensitive.