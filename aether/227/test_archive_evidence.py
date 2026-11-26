"""AETHER-227 synthetic archive tests; no real GitHub Actions archive is supplied."""
import io
import json
import stat
import tempfile
from pathlib import Path
import unittest
import zipfile
from archive_evidence import inspect_zip,export,REQUIRED,digest,canonical

SHA="a"*40

def payloads():
    files={name:("SYNTHETIC "+name+"\n").encode() for name in REQUIRED}
    files["commit.txt"]=(SHA+"\n").encode()
    files["aether218-gate.json"]=json.dumps({
       "source_commit":SHA,"native_qualification_passed":True,
       "operational_authority":"HOLD","physical_qualification_percent":0}).encode()
    files["aether219-manifest.json"]=json.dumps({
       "source_commit":SHA,"native_qualification_verified_by_this_manifest":True,
       "operational_authority":"HOLD","physical_qualification_percent":0}).encode()
    return files

def archive(files,duplicates=None,symlink=None):
    buf=io.BytesIO()
    with zipfile.ZipFile(buf,"w",compression=zipfile.ZIP_STORED) as z:
        for key,value in files.items():
            z.writestr(key,value)
        if duplicates is not None:
            import warnings
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                z.writestr(duplicates,b"modified duplicate")
        if symlink is not None:
            info=zipfile.ZipInfo(symlink)
            info.external_attr=(stat.S_IFLNK|0o777)<<16
            z.writestr(info,b"link")
    return buf.getvalue()

class ArchiveEvidenceTests(unittest.TestCase):
    def reject(self,reason,data,sha=SHA):
        result=inspect_zip(data,sha)
        self.assertEqual(result["verdict"],"REJECT",result)
        self.assertIn(reason,result["reasons"],result)
        self.assertEqual(result["operational_authority"],"HOLD")
        self.assertFalse(result["physical_act_allowed"])
        self.assertEqual(result["physical_qualification_percent"],0)

    def test_complete_synthetic_archived_bytes_documentary_only(self):
        d=inspect_zip(archive(payloads()),SHA)
        self.assertEqual(d["verdict"],"DOCUMENTARY_ARCHIVE_BYTES_CONSISTENT_ONLY",d)
        self.assertFalse(d["native_ci_execution_independently_authenticated"])
        self.assertFalse(d["github_artifact_remote_retention_authenticated"])

    def test_export_repeats_identical_archive_bytes(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            for name,data in payloads().items():
                (root/name).write_bytes(data)
            a=export(root,SHA)
            b=export(root,SHA)
            self.assertEqual(a,b)
            self.assertEqual(inspect_zip(a,SHA)["verdict"],"DOCUMENTARY_ARCHIVE_BYTES_CONSISTENT_ONLY")

    def test_missing_zip(self):
        self.reject("ARCHIVE_BYTES_MISSING",None)

    def test_garbage_zip(self):
        self.reject("ARCHIVE_CORRUPT_OR_UNREADABLE",b"garbage")

    def test_missing_required_log(self):
        f=payloads();f.pop("cargo_test.log")
        self.reject("REQUIRED_EVIDENCE_MISSING",archive(f))

    def test_mutated_commit(self):
        f=payloads();f["commit.txt"]=("b"*40+"\n").encode()
        self.reject("SOURCE_COMMIT_MISMATCH",archive(f))

    def test_bad_native_gate(self):
        f=payloads();f["aether218-gate.json"]=json.dumps({
            "source_commit":SHA,"native_qualification_passed":False,
            "operational_authority":"HOLD","physical_qualification_percent":0}).encode()
        self.reject("NATIVE_EXECUTION_NOT_QUALIFIED",archive(f))

    def test_bad_manifest_gate(self):
        f=payloads();f["aether219-manifest.json"]=json.dumps({
            "source_commit":SHA,"native_qualification_verified_by_this_manifest":False,
            "operational_authority":"HOLD","physical_qualification_percent":0}).encode()
        self.reject("MANIFEST_NATIVE_QUALIFICATION_NOT_PASSED",archive(f))

    def test_manifest_revision_swap(self):
        f=payloads();m=json.loads(f["aether219-manifest.json"])
        m["source_commit"]="b"*40;f["aether219-manifest.json"]=json.dumps(m).encode()
        self.reject("MANIFEST_SOURCE_MISMATCH",archive(f))

    def test_native_revision_swap(self):
        f=payloads();m=json.loads(f["aether218-gate.json"])
        m["source_commit"]="b"*40;f["aether218-gate.json"]=json.dumps(m).encode()
        self.reject("NATIVE_GATE_SOURCE_MISMATCH",archive(f))

    def test_authority_promotion_in_gate(self):
        f=payloads();m=json.loads(f["aether218-gate.json"])
        m["operational_authority"]="ACT";f["aether218-gate.json"]=json.dumps(m).encode()
        self.reject("GATE_AUTHORITY_PROMOTION",archive(f))

    def test_authority_promotion_in_manifest(self):
        f=payloads();m=json.loads(f["aether219-manifest.json"])
        m["physical_qualification_percent"]=100
        f["aether219-manifest.json"]=json.dumps(m).encode()
        self.reject("MANIFEST_AUTHORITY_PROMOTION",archive(f))

    def test_duplicate_entry(self):
        self.reject("DUPLICATE_ARCHIVE_ENTRY",archive(payloads(),duplicates="cargo_test.log"))

    def test_parent_traversal_entry(self):
        f=payloads();f["../escaped"]=b"danger"
        self.reject("UNSAFE_ARCHIVE_PATH",archive(f))

    def test_absolute_path_entry(self):
        f=payloads();f["/tmp/escaped"]=b"danger"
        self.reject("UNSAFE_ARCHIVE_PATH",archive(f))

    def test_backslash_path(self):
        f=payloads();f["windows\\path"]=b"danger"
        self.reject("UNSAFE_ARCHIVE_PATH",archive(f))

    def test_symlink_entry(self):
        self.reject("SYMLINK_ARCHIVE_ENTRY",archive(payloads(),symlink="link"))

    def test_zero_entries(self):
        self.reject("REQUIRED_EVIDENCE_MISSING",archive({}))

    def test_expected_sha_not_pinned(self):
        self.reject("EXPECTED_SOURCE_COMMIT_UNPINNED",archive(payloads()),sha="invalid")

    def test_bad_native_json(self):
        f=payloads();f["aether218-gate.json"]=b"invalid json"
        self.reject("GATE_JSON_INVALID",archive(f))

    def test_bad_manifest_json(self):
        f=payloads();f["aether219-manifest.json"]=b"invalid json"
        self.reject("MANIFEST_JSON_INVALID",archive(f))

    def test_entry_digests_are_exact(self):
        r=inspect_zip(archive(payloads()),SHA)
        self.assertEqual(r["entries"]["commit.txt"]["sha256"],digest(payloads()["commit.txt"]))

    def test_zip_hash_changes_when_log_changes(self):
        original=archive(payloads())
        f=payloads();f["cargo_check.log"]+=b"TAMPER"
        changed=archive(f)
        self.assertNotEqual(inspect_zip(original,SHA)["archive_sha256"],
                            inspect_zip(changed,SHA)["archive_sha256"])

    def test_canonical_inventory_is_key_order_invariant(self):
        self.assertEqual(canonical({"b":1,"a":2}),canonical({"a":2,"b":1}))

if __name__=="__main__":
    unittest.main()
