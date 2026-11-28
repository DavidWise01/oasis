import json,sqlite3,tempfile,unittest
from pathlib import Path
from handoff_qualification import (sigv4_parity,handoff_preimage,durable_write,
                                   export_handoff,audit_packet,canonical,sha,sha_bytes)
ZERO="0"*64
class Tests(unittest.TestCase):
    def setUp(self):
        t=tempfile.TemporaryDirectory();self.addCleanup(t.cleanup)
        self.db=Path(t.name)/"a297.sqlite";self.out=Path(t.name)/"handoff.json"
        record=[]
        import base64
        for kind in ("VERSIONING","LOCK_CONFIGURATION","HEAD","RETENTION"):
            body=b"" if kind=="HEAD" else b"<x>example</x>"
            record.append({"operation":kind,"method":"HEAD" if kind=="HEAD" else "GET",
                           "response_status":200,
                           "response_headers":{"x-amz-request-id":"request1"},
                           "response_raw_sha256":sha_bytes(body),
                           "response_raw_b64":base64.b64encode(body).decode(),
                           "path_sha256":"a"*64,"request_sha256":"b"*64})
        manifest={"schema":"AETHER-297/owner-bound-evidence-v1","challenge":"long-capture-nonce-299",
                  "previous_head_sha256":ZERO,"evidence":{
                      "schema":"AETHER-297/owner-bound-evidence-v1","records":record}}
        self.head=sha(manifest)
        db=sqlite3.connect(self.db)
        db.execute("CREATE TABLE evidence (id INTEGER PRIMARY KEY,challenge TEXT,previous_head TEXT,head TEXT,manifest TEXT)")
        db.execute("INSERT INTO evidence VALUES (?,?,?,?,?)",(1,manifest["challenge"],ZERO,self.head,canonical(manifest).decode()))
        db.commit();db.close()
        self.ancestry="e"*64
    def export(self,fail_at=None):
        return export_handoff(self.db,self.out,1,self.head,"external-custodian-claimed",
                              self.ancestry,fail_at)
    def test_actual_signer_botocore_get(self):
        r=sigv4_parity("s3.us-east-1.amazonaws.com","/vault/file",
          {"versionId":"v1","retention":""},"us-east-1","123456789012",
          "AKIDEXAMPLE","SECRETEXAMPLE","","20261128T115600Z","GET")
        self.assertTrue(r["signature_parity"])
        self.assertFalse(r["independent_external_custody_verified"])
    def test_actual_signer_botocore_head(self):
        r=sigv4_parity("s3.us-east-1.amazonaws.com","/vault/file",
          {"versionId":"v1"},"us-east-1","123456789012",
          "AKIDEXAMPLE","SECRETEXAMPLE","","20261128T115600Z","HEAD")
        self.assertTrue(r["signature_parity"])
    def test_actual_signer_botocore_temporary_token(self):
        r=sigv4_parity("s3.us-east-1.amazonaws.com","/vault/file",
          {"versionId":"v1"},"us-east-1","123456789012",
          "AKIDEXAMPLE","SECRETEXAMPLE","SESSION123","20261128T115600Z","HEAD")
        self.assertTrue(r["signature_parity"])
    def test_write_method_rejected(self):
        with self.assertRaisesRegex(ValueError,"READ_ONLY_METHOD_REQUIRED"):
            sigv4_parity("s3.us-east-1.amazonaws.com","/vault/file",{},"us-east-1",
                          "123456789012","AKID","SECRET","","20261128T115600Z","PUT")
    def test_handoff_created(self):
        r=self.export()
        self.assertEqual(r["operational_authority"],"HOLD")
        self.assertTrue(self.out.exists())
    def test_handoff_readback(self):
        self.export()
        self.assertEqual(audit_packet(self.out,self.db)["packet_sha256"],sha_bytes(self.out.read_bytes()))
    def test_create_only_no_overwrite(self):
        self.export()
        original=self.out.read_bytes()
        with self.assertRaises(FileExistsError):self.export()
        self.assertEqual(self.out.read_bytes(),original)
    def test_missing_history(self):
        with sqlite3.connect(self.db) as db:db.execute("DELETE FROM evidence")
        with self.assertRaisesRegex(ValueError,"EMPTY_EVIDENCE_JOURNAL"):self.export()
    def test_wrong_prefix(self):
        with self.assertRaisesRegex(ValueError,"PINNED_HISTORY_REWRITTEN"):
            export_handoff(self.db,self.out,1,"f"*64,"custodian",self.ancestry)
    def test_ancestry_pin_required(self):
        with self.assertRaisesRegex(ValueError,"OUT_OF_BAND_ANCESTRY_PIN_REQUIRED"):
            export_handoff(self.db,self.out,1,self.head,"custodian","missing")
    def test_recipient_required(self):
        with self.assertRaisesRegex(ValueError,"RECIPIENT_ID_REQUIRED"):
            export_handoff(self.db,self.out,1,self.head,"",self.ancestry)
    def test_pre_fsync_fault_preserves_file(self):
        with self.assertRaisesRegex(RuntimeError,"INJECTED_PRE_FSYNC"):self.export("before_fsync")
        self.assertTrue(self.out.exists())
        self.assertEqual(audit_packet(self.out)["operational_authority"],"HOLD")
    def test_post_fsync_fault_preserves_file(self):
        with self.assertRaisesRegex(RuntimeError,"INJECTED_POST_FSYNC"):self.export("after_fsync")
        self.assertTrue(self.out.exists())
    def test_pre_readback_fault_preserves_file(self):
        with self.assertRaisesRegex(RuntimeError,"INJECTED_PRE_READBACK"):self.export("before_readback")
        self.assertTrue(self.out.exists())
    def test_retry_after_fault_cannot_overwrite(self):
        with self.assertRaises(RuntimeError):self.export("before_fsync")
        with self.assertRaises(FileExistsError):self.export()
    def test_packet_tamper_detected(self):
        self.export()
        body=json.loads(self.out.read_bytes())
        body["source_head_sha256"]="f"*64
        self.out.write_bytes(canonical(body))
        with self.assertRaisesRegex(ValueError,"HANDOFF_SOURCE_ROLLBACK"):
            audit_packet(self.out,self.db)
    def test_packet_external_digest_pin(self):
        self.export()
        with self.assertRaisesRegex(ValueError,"HANDOFF_DIGEST_PIN_CONFLICT"):
            audit_packet(self.out,None,"f"*64)
    def test_packet_no_act(self):
        self.export()
        result=audit_packet(self.out)
        self.assertFalse(result["physical_act_allowed"])
    def test_local_db_head_modified(self):
        self.export()
        with sqlite3.connect(self.db) as db:db.execute("UPDATE evidence SET head=?",("f"*64,))
        with self.assertRaisesRegex(ValueError,"HISTORY_MANIFEST_HASH_INVALID"):audit_packet(self.out,self.db)
    def test_packet_authority_promotion_blocked(self):
        self.export();obj=json.loads(self.out.read_bytes());obj["independent_custody_verified"]=True
        self.out.write_bytes(canonical(obj))
        with self.assertRaisesRegex(ValueError,"FORBIDDEN_AUTHORITY_PROMOTION"):audit_packet(self.out)
    def test_prefix_removed_after_export(self):
        self.export()
        with sqlite3.connect(self.db) as db:db.execute("DELETE FROM evidence")
        with self.assertRaisesRegex(ValueError,"EMPTY_EVIDENCE_JOURNAL"):audit_packet(self.out,self.db)
if __name__=="__main__":unittest.main()
