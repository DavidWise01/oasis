import base64,json,sqlite3,tempfile,unittest
from pathlib import Path
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from signed_object_binding import capture,audit,validate,verify_receipt,canon,sha,digest,ZERO,SCHEMA
class Tests(unittest.TestCase):
    def setUp(self):
        temp=tempfile.TemporaryDirectory();self.addCleanup(temp.cleanup)
        self.db=Path(temp.name)/"302.sqlite"
        self.signer=Ed25519PrivateKey.generate()
        pem=self.signer.public_key().public_bytes(serialization.Encoding.PEM,
                      serialization.PublicFormat.SubjectPublicKeyInfo).decode()
        self.key={"custodian_id":"custodian302","public_key_pem":pem}
        self.object_bytes=b"bound external object content phase302"
        self.receipt_url="https://receipt.example.org/receipt302"
        self.object_url="https://objects.example.net/objects/immutable-v302?versionId=v302"
        self.claim={"schema":SCHEMA,"custodian_id":"custodian302","receipt_nonce":"receipt-302-unique",
                    "previous_receipt_sha256":ZERO,"handoff_sha256":"a"*64,
                    "source_head_sha256":"b"*64,"source_sequence":19,
                    "object_url":self.object_url,"object_version":"v302",
                    "object_sha256":digest(self.object_bytes),"object_length":len(self.object_bytes),
                    "retained_until_claim":"2031-12-31"}
        self.refresh()
        self.config={"schema":"AETHER-302/config-v1","receipt_url":self.receipt_url,
                    "object_url":self.object_url,"receipt_sha256":digest(self.receipt_bytes),
                    "object_sha256":digest(self.object_bytes),"object_length":len(self.object_bytes),
                    "object_version":"v302","handoff_sha256":"a"*64,"source_head_sha256":"b"*64,
                    "source_sequence":19,"key_record":self.key,"key_pin_sha256":sha(self.key)}
        self.pin=sha(self.config)
    def refresh(self):
        unsigned=dict(self.claim)
        self.claim["signature_b64"]=base64.b64encode(self.signer.sign(canon(unsigned))).decode()
        self.receipt_bytes=canon(self.claim)
    def collector(self,url,hosts):
        raw=self.receipt_bytes if url==self.receipt_url else self.object_bytes
        assert url.split("/")[2] in hosts
        obs={"schema":"AETHER-264/https-acquisition-v1","requested_url":url,
             "host":url.split("/")[2],"pinned_ip":"8.8.8.8","dns_address_count":1,
             "tls_hostname_validation":True,"status":200,"elapsed_ms":1,
             "raw_length":len(raw),"raw_sha256":digest(raw),"raw_b64":base64.b64encode(raw).decode()}
        return {**obs,"observation_sha256":sha(obs)}
    def run_capture(self,nonce="window-302-unique-one"):
        return capture(self.db,self.config,self.pin,nonce,self.collector)
    def test_signed_object_accepts_exact_fields(self):
        result=self.run_capture()
        self.assertTrue(result["signed_object_fields_matched"])
        self.assertFalse(result["independent_custodian_ownership_verified"])
    def test_two_windows_and_audit(self):
        self.run_capture();self.run_capture("window-302-unique-two")
        report=audit(self.db,self.config,self.pin)
        self.assertEqual(report["windows"],2)
        self.assertNotIn("RETAINED_WINDOW_INVALID",report["reasons"])
    def test_original_receipt_signature_valid(self):
        self.assertEqual(verify_receipt(self.receipt_bytes,self.config)["object_version"],"v302")
    def test_modified_signature_rejected(self):
        receipt=json.loads(self.receipt_bytes);receipt["signature_b64"]="AAAA"
        self.receipt_bytes=canon(receipt);self.config["receipt_sha256"]=digest(self.receipt_bytes)
        self.pin=sha(self.config)
        with self.assertRaisesRegex(ValueError,"RECEIPT_SIGNATURE_INVALID"):self.run_capture()
    def test_url_substitution_rejected(self):
        self.config["object_url"]="https://objects.example.net/other?versionId=v302"
        self.pin=sha(self.config)
        with self.assertRaisesRegex(ValueError,"SIGNED_OBJECT_BINDING_CHANGED:object_url"):self.run_capture()
    def test_version_substitution_rejected(self):
        self.config["object_version"]="different"
        self.pin=sha(self.config)
        with self.assertRaisesRegex(ValueError,"SIGNED_OBJECT_BINDING_CHANGED:object_version"):self.run_capture()
    def test_length_substitution_rejected(self):
        self.config["object_length"]=len(self.object_bytes)+1
        self.pin=sha(self.config)
        with self.assertRaisesRegex(ValueError,"SIGNED_OBJECT_BINDING_CHANGED:object_length"):self.run_capture()
    def test_digest_substitution_rejected(self):
        self.config["object_sha256"]="f"*64;self.pin=sha(self.config)
        with self.assertRaisesRegex(ValueError,"SIGNED_OBJECT_BINDING_CHANGED:object_sha256"):self.run_capture()
    def test_handoff_substitution_rejected(self):
        self.config["handoff_sha256"]="f"*64;self.pin=sha(self.config)
        with self.assertRaisesRegex(ValueError,"SIGNED_OBJECT_BINDING_CHANGED:handoff_sha256"):self.run_capture()
    def test_modified_remote_bytes_rejected(self):
        self.object_bytes=b"wrong bytes"
        with self.assertRaisesRegex(ValueError,"SIGNED_OBJECT_BYTES_CHANGED"):self.run_capture()
    def test_receipt_raw_digest_mismatch(self):
        self.receipt_bytes=b"changed receipt"
        with self.assertRaisesRegex(ValueError,"SIGNED_RECEIPT_RAW_CHANGED"):self.run_capture()
    def test_duplicate_window_nonce(self):
        self.run_capture()
        with self.assertRaisesRegex(ValueError,"WINDOW_NONCE_REPLAY"):self.run_capture()
    def test_third_window_denied(self):
        self.run_capture();self.run_capture("window-302-unique-two")
        with self.assertRaisesRegex(ValueError,"TWO_WINDOWS_ONLY"):
            self.run_capture("window-302-unique-three")
    def test_changed_configuration_between_windows(self):
        self.run_capture();self.config["object_version"]="changed";self.pin=sha(self.config)
        with self.assertRaisesRegex(ValueError,"WINDOW_CONFIGURATION_CHANGED"):
            self.run_capture("window-302-unique-two")
    def test_identical_hostname_denied(self):
        self.config["object_url"]="https://receipt.example.org/object"
        self.pin=sha(self.config)
        with self.assertRaisesRegex(ValueError,"SHARED_HOST_ANCESTRY_RISK"):self.run_capture()
    def test_bad_key_pin_rejected(self):
        self.config["key_pin_sha256"]="f"*64;self.pin=sha(self.config)
        with self.assertRaisesRegex(ValueError,"CUSTODIAN_KEY_PIN_INVALID"):self.run_capture()
    def test_failure_atomic(self):
        self.object_bytes=b"wrong bytes"
        with self.assertRaises(ValueError):self.run_capture()
        self.assertEqual(audit(self.db,self.config,self.pin)["windows"],0)
    def test_manifest_head_corruption_detected(self):
        self.run_capture()
        with sqlite3.connect(self.db) as db:db.execute("UPDATE window SET head=?",("f"*64,))
        self.assertIn("MANIFEST_SHA_INVALID",audit(self.db,self.config,self.pin)["reasons"])
    def test_external_prefix_rewrite_detected(self):
        self.run_capture()
        self.assertIn("HISTORICAL_WINDOW_REWRITTEN",
                      audit(self.db,self.config,self.pin,1,"f"*64)["reasons"])
    def test_external_prefix_delete_detected(self):
        first=self.run_capture()
        with sqlite3.connect(self.db) as db:db.execute("DELETE FROM window")
        self.assertIn("HISTORICAL_WINDOW_REMOVED",
                      audit(self.db,self.config,self.pin,1,first["head_sha256"])["reasons"])
    def test_no_physical_act(self):
        self.run_capture();self.assertFalse(audit(self.db,self.config,self.pin)["physical_act_allowed"])
if __name__=="__main__":unittest.main()
