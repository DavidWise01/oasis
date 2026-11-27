import base64,copy,tempfile,unittest
from pathlib import Path
from raw_probe import CATS,canon,capture,review,sha
class Tests(unittest.TestCase):
    def setUp(self):
        t=tempfile.TemporaryDirectory();self.addCleanup(t.cleanup);self.folder=Path(t.name)
        self.spec={"source_commit":"a"*40,"run_id":42,"challenge_id":"challenge-42",
                   "files":{c:c+".bin" for c in CATS}}
        for c in CATS:(self.folder/(c+".bin")).write_bytes(("RAW:"+c).encode())
        self.doc=capture(self.spec,self.folder)
    def expect(self,change,reason):
        d=copy.deepcopy(self.doc);change(d);r=review(d)
        self.assertIn(reason,r["reasons"],r);self.assertEqual(r["operational_authority"],"HOLD")
    def test_consistent_but_not_certified(self):
        r=review(self.doc);self.assertEqual(len(r["observed"]),6)
        self.assertIn("TRANSCRIPTS_NOT_AUTHENTICATED_AS_LIVE_NETWORK_PROBES",r["reasons"])
    def test_raw_altered(self):self.expect(lambda d:d["records"][0].update(raw_b64=base64.b64encode(b"forged").decode()),"RAW_SHA256_MISMATCH")
    def test_length(self):self.expect(lambda d:d["records"][0].update(raw_length=999),"LENGTH_MISMATCH")
    def test_invalid_base64(self):self.expect(lambda d:d["records"][0].update(raw_b64="!"),"RAW_UNDECODABLE")
    def test_missing_category(self):self.expect(lambda d:d["records"].pop(),"SIX_RECORDS_REQUIRED")
    def test_duplicate_category(self):self.expect(lambda d:d["records"][1].update(category=d["records"][0]["category"]),"CATEGORY_INVALID")
    def test_snapshot_altered(self):self.expect(lambda d:d.update(challenge_id="changed"),"SNAPSHOT_SHA256_MISMATCH")
    def test_snapshot_missing_digest(self):self.expect(lambda d:d.update(snapshot_sha256=None),"SNAPSHOT_DIGEST_INVALID")
    def test_bad_commit(self):self.expect(lambda d:d.update(source_commit="bad"),"COMMIT_INVALID")
    def test_boolean_run(self):self.expect(lambda d:d.update(run_id=True),"RUN_INVALID")
    def test_traversal(self):
        self.spec["files"]["loopback"]="../outside"
        with self.assertRaises(ValueError):capture(self.spec,self.folder)
    def test_symlink(self):
        (self.folder/"loopback.bin").unlink()
        (self.folder/"loopback.bin").symlink_to(self.folder/"private.bin")
        with self.assertRaises(ValueError):capture(self.spec,self.folder)
    def test_oversize(self):
        (self.folder/"loopback.bin").write_bytes(b"x"*65537)
        with self.assertRaises(ValueError):capture(self.spec,self.folder)
    def test_missing_file(self):
        (self.folder/"loopback.bin").unlink()
        with self.assertRaises(ValueError):capture(self.spec,self.folder)
    def test_spec_incomplete(self):
        self.spec["files"].pop("loopback")
        with self.assertRaises(ValueError):capture(self.spec,self.folder)
    def test_spec_bad_commit(self):
        self.spec["source_commit"]="bad"
        with self.assertRaises(ValueError):capture(self.spec,self.folder)
    def test_non_document(self):self.assertIn("DOCUMENT_INVALID",review(None)["reasons"])
    def test_authority_stays_hold(self):
        r=review(self.doc);self.assertFalse(r["physical_act_allowed"])
        self.assertFalse(r["network_isolation_independently_verified"])
if __name__=="__main__":unittest.main()
