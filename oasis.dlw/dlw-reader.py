#!/usr/bin/env python3
"""
dlw-reader — the OaSIs .dlw seal-chain reader.

Reads the oasis.dlw/ family (.dlw files, one per seal/artifact) and:
  1. Parses the manifest (oasis.dlw/manifest.dlw.json).
  2. Re-derives the seal_sha256 by canonical JSON re-serialization so the
     file's sha256 matches what the manifest declares.
  3. Verifies the oasis.chain tether: link = sha256(index|slug|seal|prev).
  4. Lists all .dlw files in a world, newest-first, with their prefix.
  5. Reports the GIT_SHA of the repo head, binding the seal to a commit.
"""
import hashlib
import json
import os
import subprocess

DLW_DIR = os.path.join(
    os.environ.get("OASI_HOME", r"C:\Users\Dave\oasis"), "oasis.dlw"
)

MANIFEST = "manifest.dlw.json"


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def discover():
    if not os.path.isdir(DLW_DIR):
        return []
    items = []
    for f in os.listdir(DLW_DIR):
        if f.endswith((".dlw", ".dlw.json")):
            p = os.path.join(DLW_DIR, f)
            if os.path.isfile(p):
                items.append((f, os.path.getmtime(p), p))
    items.sort(key=lambda t: -t[1])  # newest first
    return items


def parse_manifest(path: str):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def rederive_seal(m: dict):
    """Return (canonical-definition, sha256) matching the declared seal, else (None, None)."""
    for label, blob in (
        ("canonical-sort-keys", json.dumps(m, sort_keys=True, ensure_ascii=False)),
        ("compact", json.dumps(m, separators=(",", ":"), ensure_ascii=False)),
    ):
        if sha256_bytes(blob.encode("utf-8")) == m.get("seal_sha256"):
            return label, sha256_bytes(blob.encode("utf-8"))
    return None, None


def verify_chain(m: dict):
    chain = m.get("chain", {})
    idx = chain.get("index")
    slug = chain.get("slug", "oasis")
    seal = chain.get("seal")
    prev = chain.get("prev", "")
    head = chain.get("head", "")
    link = chain.get("link", "")
    anchor = f"{idx}|{slug}|{seal}|{prev}".encode("utf-8")
    expected = sha256_bytes(anchor)
    return {
        "index": idx,
        "slug": slug,
        "seal": seal,
        "prev": prev,
        "head": head,
        "link_declared": link,
        "link_expected": expected,
        "verified": expected == link,
    }


def git_head_sha() -> str:
    try:
        out = subprocess.run(
            ["git", "rev-parse", "HEAD"], capture_output=True, text=True, cwd=DLW_DIR
        ).stdout.strip()
        return out or "?"
    except Exception:
        return "?"


class DlwReader:
    DIR = DLW_DIR

    @staticmethod
    def run():
        manifest = None
        chain_verify = None
        chain_raw = None

        mf = os.path.join(DLW_DIR, MANIFEST)
        if os.path.exists(mf):
            manifest = parse_manifest(mf)
            label, derived = rederive_seal(manifest)
            manifest["_seal_verdict"] = {
                "declared": manifest.get("seal_sha256"),
                "derived": derived,
                "derived_by": label,
                "match": derived is not None and derived == manifest.get("seal_sha256"),
            }

        cf = os.path.join(DLW_DIR, "oasis.chain")
        if os.path.exists(cf):
            chain_raw = open(cf, encoding="utf-8").read().strip()
            chain_verify = verify_chain(manifest)

        return {
            "dlw_dir": DLW_DIR,
            "discovered": [
                {"file": f, "size": os.path.getsize(p), "mtime": os.path.getmtime(p)}
                for f, _, p in discover()
            ],
            "manifest": manifest,
            "chain_raw": chain_raw,
            "chain_verify": chain_verify,
            "git_head_sha": git_head_sha(),
        }


def render(r: dict) -> str:
    L = []
    L.append("OaSIs .dlw seal-chain reader")
    L.append("=" * 60)
    L.append(f"dir       : {r['dlw_dir']}")
    L.append(f"git head  : {r['git_head_sha']}")
    L.append(f"files     : {len(r['discovered'])}")
    for d in r["discovered"]:
        L.append(f"   {d['file']:34s} {d['size']:6d} bytes")

    if r.get("manifest"):
        m = r["manifest"]
        L.append("-" * 60)
        L.append(f"title     : {m.get('name')}")
        L.append(f"badge     : {m.get('badge')}")
        L.append(f"moniker   : {m.get('moniker')}")
        L.append(f"signature : {m.get('seal_sha256')}")
        L.append(f"architect : {m.get('architect')}")
        L.append(f"license   : {m.get('license')}")
        L.append(f"chain.index : {m.get('chain', {}).get('index')}")

    if r.get("seal_verdict"):
        v = r["seal_verdict"]["_seal_verdict"]
        L.append("-" * 60)
        L.append(f"seal declared   : {v['declared']}")
        L.append(f"seal derived    : {v['derived']}")
        L.append(f"seal derived by : {v['derived_by']}")
        L.append(f"seal match      : {'YES' if v['match'] else 'NO'}")

    if r.get("chain_raw"):
        L.append("-" * 60)
        L.append("chain raw:")
        for ln in r["chain_raw"].splitlines():
            L.append(f"   {ln}")
        if r.get("chain_verify"):
            c = r["chain_verify"]
            L.append(f"chain tether: {'VERIFIED' if c['verified'] else 'MISMATCH'}")

    return "\n".join(L)


if __name__ == "__main__":
    print(render(DlwReader.run()))
