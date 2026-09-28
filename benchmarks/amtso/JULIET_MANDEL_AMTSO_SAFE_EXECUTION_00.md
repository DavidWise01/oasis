# Juliet / Mandel AMTSO Safe Execution 00

Status: **PASS**

The disposable artifact contains the canonical 68-byte EICAR test artifact,
renamed EICAR, one-level ZIP, two-level ZIP, and benign controls.

Local results:

```text
eicar.com       -> xe
eicar.com.txt   -> xe
eicar.com.zip   -> xe
eicar.com-2.zip -> xe
benign.txt      -> 0e
benign.zip      -> 0e
```

No sample was executed. Network use was disabled. Writes were limited to the
artifact's evidence directory.

The live PUA / drive-by / phishing / cloud checks remain URL-driven AMTSO checks
listed in the manifest because this build environment is offline.

Artifact ZIP SHA-256:
`17edcf712da88314417f8e52ca000601941ec9608bab8ced0e18bd333e402f12`
