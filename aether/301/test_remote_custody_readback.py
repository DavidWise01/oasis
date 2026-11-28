import base64,hashlib,json,sqlite3,tempfile,unittest
from pathlib import Path
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from remote_custody_readback import capture,audit,sha,canon,digest,ZERO,SCHEMA

class Tests(unittest.TestCase):
    def setUp(self):
        temp=tempfile.TemporaryDirectory();self.addCleanup(temp.cleanup)
        self.db=Path(temp.name)/"a301.sqlite"
        key=Ed25519PrivateKey.generate()
        pem=key.public_key().public_bytes(serialization.Encoding.PEM,serialization.PublicFormat.SubjectPublicKeyInfo).decode()
        self.key_record={"custodian_id":"custodian301","public_key_pem":pem}
        self.object_raw=b"retained immutable-object candidate 301"
        self.receipt_url="https://receipt.example.org/evidence/301"
        self.object_url="https://object.example.org/evidence/301"
        self.receipt={"schema":"AETHER-300/external-acceptance-v1",
            "custodian_id":"custodian301","handoff_sha256":"a"*64,
            "source_head_sha256":"b"*64,"source_sequence":17,
            "previous_receipt_sha256":ZERO,"receipt_nonce":"receipt301-unique",
            "remote_object_id_claim":"retained-v1","retained_until_claim":"2030-01-01"}
        self.receipt["signature_b64"]=base64.b64encode(key.sign(canon(self.receipt))).decode()
        self.receipt_raw=canon(self.receipt)
        self.config={"schema":"AETHER-301/acquisition-config-v1",
            "receipt_url":self.receipt_url,"object_url":self.object_url,
            "receipt_sha256":digest(self.receipt_raw),
            "object_sha256":digest(self.object_raw),
            "handoff_sha256":"a"*64,"source_head_sha256":"b"*64,
            "source_sequence":17,"key_record":self.key_record,
            "key_sha256":sha(self.key_record)}
        self.pin=sha(self.config)
    def collector(self,url,allowed):
        self.assertIn(url.split("/")[2],allowed)
        raw=self.receipt_raw if url==self.receipt_url else self.object_raw
        fields={"schema":"AETHER-264/https-acquisition-v1",
                "requested_url":url,"host":url.split("/")[2],
                "pinned_ip":"8.8.8.8","dns_address_count":1,
                "tls_hostname_validation":True,"status":200,"elapsed_ms":1,
                "raw_length":len(raw),"raw_sha256":digest(raw),
                "raw_b64":base64.b64encode(raw).decode()}
        return {**fields,"observation_sha256":sha(fields),"operational_authority":"HOLD"}
    def first(self):
        return capture(self.db,self.config,self.pin,"window-first-301",self.collector)
    def second(self):
        return capture(self.db,self.config,self.pin,"window-second-301",self.collector)
    def test_signed_receipt_and_object_match(self):
        result=self.first()
        self.assertTrue(result["receipt_signature_valid"])
        self.assertFalse(result["independent_custody_verified"])
    def test_two_windows_and_recovery(self):
        self.first();self.second()
        result=audit(self.db,self.config,self.pin)
        self.assertEqual(result["windows"],2)
        self.assertNotIn("RETAINED_OBSERVATION_INVALID",result["reasons"])
    def test_historical_prefix_success(self):
        first=self.first();self.second()
        result=audit(self.db,self.config,self.pin,1,first["journal_head_sha256"])
        self.assertNotIn("EXTERNALLY_ANCHORED_WINDOW_CHANGED",result["reasons"])
    def test_historical_prefix_changed(self):
        self.first()
        self.assertIn("EXTERNALLY_ANCHORED_WINDOW_CHANGED",
                      audit(self.db,self.config,self.pin,1,"f"*64)["reasons"])
    def test_historical_prefix_removed(self):
        self.first()
        self.assertIn("EXTERNALLY_ANCHORED_WINDOW_REMOVED",
                      audit(self.db,self.config,self.pin,2,"f"*64)["reasons"])
    def test_window_replay_rejected(self):
        self.first()
        with self.assertRaisesRegex(ValueError,"WINDOW_REPLAY"):self.first()
    def test_third_window_rejected(self):
        self.first();self.second()
        with self.assertRaisesRegex(ValueError,"TWO_WINDOWS_ALREADY_CAPTURED"):
            capture(self.db,self.config,self.pin,"window-third-301",self.collector)
    def test_config_pin_mismatch(self):
        with self.assertRaisesRegex(ValueError,"CONFIG_PIN_INVALID"):
            capture(self.db,self.config,"f"*64,"window-first-301",self.collector)
    def test_shared_source_host_rejected(self):
        self.config["object_url"]="https://receipt.example.org/object"
        self.pin=sha(self.config)
        with self.assertRaisesRegex(ValueError,"RECEIPT_AND_OBJECT_SAME_HOST"):
            capture(self.db,self.config,self.pin,"window-first-301",self.collector)
    def test_signature_substitution(self):
        record=json.loads(self.receipt_raw);record["signature_b64"]="AAAA"
        self.receipt_raw=canon(record)
        self.config["receipt_sha256"]=digest(self.receipt_raw)
        self.pin=sha(self.config)
        with self.assertRaisesRegex(ValueError,"RECEIPT_SIGNATURE_INVALID"):
            capture(self.db,self.config,self.pin,"window-first-301",self.collector)
    def test_receipt_bytes_changed(self):
        self.receipt_raw=b"modified"
        with self.assertRaisesRegex(ValueError,"REMOTE_RECEIPT_BYTES_CHANGED"):self.first()
    def test_object_bytes_changed(self):
        self.object_raw=b"modified"
        with self.assertRaisesRegex(ValueError,"REMOTE_OBJECT_BYTES_CHANGED"):self.first()
    def test_no_partial_acceptance_on_failed_object(self):
        self.object_raw=b"corrupt"
        with self.assertRaises(ValueError):self.first()
        self.assertEqual(audit(self.db,self.config,self.pin)["windows"],0)
    def test_mutated_journal_head(self):
        self.first()
        with sqlite3.connect(self.db) as db:
            db.execute("UPDATE window SET head=?",("f"*64,))
        self.assertIn("WINDOW_MANIFEST_HEAD_INVALID",audit(self.db,self.config,self.pin)["reasons"])
    def test_removed_window_detected(self):
        first=self.first()
        with sqlite3.connect(self.db) as db:db.execute("DELETE FROM window")
        self.assertIn("EXTERNALLY_ANCHORED_WINDOW_REMOVED",
                      audit(self.db,self.config,self.pin,1,first["journal_head_sha256"])["reasons"])
    def test_source_key_pin_mismatch(self):
        self.config["key_sha256"]="f"*64
        self.pin=sha(self.config)
        with self.assertRaisesRegex(ValueError,"CUSTODIAN_KEY_PIN_INVALID"):
            capture(self.db,self.config,self.pin,"window-first-301",self.collector)
    def test_window_config_replacement_rejected(self):
        self.first()
        self.config["object_sha256"]="f"*64
        self.pin=sha(self.config)
        with self.assertRaisesRegex(ValueError,"SOURCE_CONFIGURATION_CHANGED"):
            capture(self.db,self.config,self.pin,"window-second-301",self.collector)
    def test_not_clock_or_custody_authority(self):
        self.first();self.second()
        report=audit(self.db,self.config,self.pin)
        self.assertFalse(report["independent_clock_verified"])
        self.assertFalse(report["physical_act_allowed"])
if __name__=="__main__":unittest.main()
