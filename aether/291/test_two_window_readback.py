import base64,hashlib,json,sqlite3,tempfile,unittest
from pathlib import Path
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from two_window_readback import capture,audit,read,canon,sha,digest,ZERO,RECORD_SCHEMA

def pem(key):
    return key.public_key().public_bytes(serialization.Encoding.PEM,
        serialization.PublicFormat.SubjectPublicKeyInfo).decode()
class Tests(unittest.TestCase):
    def setUp(self):
        tmp=tempfile.TemporaryDirectory();self.addCleanup(tmp.cleanup)
        self.db=Path(tmp.name)/"paired.sqlite"
        self.artifact=canon({"schema":"AETHER-287/export-v1","example":"test artifact"})
        self.keys={};self.urls={};self.records={}
        graph={"journal":["journal-root"],"journal-root":[]}
        self.raw={}
        for i in range(3):
            kid=f"k{i}";ctrl=f"controller{i}";key=Ed25519PrivateKey.generate()
            self.keys[kid]={"controller_id":ctrl,"public_key_pem":pem(key)}
            graph[ctrl]=[f"root{i}"];graph[f"root{i}"]=[]
            self.urls[kid]=f"https://vault{i}.example.org/retained"
            statement={"schema":RECORD_SCHEMA,"endpoint_id":kid,"controller_id":ctrl,
                       "challenge_nonce":"retention-challenge-291","ack_batch_id":1,
                       "ack_head_sha256":"a"*64,"ack_nonce_count":3,
                       "source_artifact_sha256":digest(self.artifact),
                       "retained_until_claim":"indefinite-claimed"}
            statement["signature_b64"]=base64.b64encode(key.sign(canon(statement))).decode()
            self.records[kid]=statement
        self.trust={"journal_controller":"journal","controllers":graph,"endpoints":self.keys}
        self.pin=sha(self.trust)
        self.first="window-one-nonce-291"
        self.second="window-two-nonce-291"
    def collector(self,url,allowed):
        self.assertIn(url.split("/")[2],allowed)
        raw=self.artifact
        fields={"schema":"AETHER-264/https-acquisition-v1","requested_url":url,
                "host":url.split("/")[2],"pinned_ip":"8.8.8.8",
                "dns_address_count":1,"tls_hostname_validation":True,
                "status":200,"elapsed_ms":2,"raw_length":len(raw),
                "raw_sha256":hashlib.sha256(raw).hexdigest(),
                "raw_b64":base64.b64encode(raw).decode()}
        return {**fields,"observation_sha256":sha(fields),"operational_authority":"HOLD"}
    def capture(self,nonce=None,collector=None):
        return capture(self.db,self.artifact,self.trust,self.pin,self.urls,
                       self.records,nonce or self.first,collector or self.collector)
    def both(self):
        first=self.capture()
        second=self.capture(self.second)
        return first,second
    def test_first_window_retains_three(self):
        r=self.capture()
        self.assertEqual((r["window"],r["matched_remote_objects"]),(1,3))
        self.assertFalse(r["independent_external_custody_verified"])
    def test_second_window_retains_six(self):
        self.both()
        r=audit(self.db)
        self.assertEqual((r["windows"],r["readbacks"]),(2,6))
        self.assertNotIn("RETAINED_REMOTE_BYTES_INVALID",r["reasons"])
    def test_second_window_chain_parent(self):
        first,second=self.both()
        rows,_=read(self.db)
        self.assertEqual(rows[1]["previous_sha"],first["head_sha256"])
    def test_ordinal_not_elapsed_time(self):
        self.both()
        self.assertIn("WINDOW_ORDINAL_NOT_AUTHENTICATED_TIME",audit(self.db)["reasons"])
    def test_same_nonce_rejected(self):
        self.capture()
        with self.assertRaisesRegex(ValueError,"WINDOW_NONCE_REPLAY"):
            self.capture()
    def test_third_window_rejected(self):
        self.both()
        with self.assertRaisesRegex(ValueError,"TWO_WINDOWS_ALREADY_RECORDED"):
            self.capture("third-window-nonce-291")
    def test_changed_remote_body_rolls_back(self):
        def corrupted(url,allowed):
            doc=self.collector(url,allowed)
            raw=b"changed"
            doc["raw_b64"]=base64.b64encode(raw).decode()
            doc["raw_length"]=len(raw)
            doc["raw_sha256"]=digest(raw)
            fields={k:doc[k] for k in ("schema","requested_url","host","pinned_ip",
                "dns_address_count","tls_hostname_validation","status","elapsed_ms",
                "raw_length","raw_sha256","raw_b64")}
            doc["observation_sha256"]=sha(fields)
            return doc
        with self.assertRaisesRegex(ValueError,"REMOTE_OBJECT_BYTES_CHANGED"):
            self.capture(collector=corrupted)
        self.assertEqual(audit(self.db)["windows"],0)
    def test_changed_observation_hash(self):
        def bad(url,allowed):
            doc=self.collector(url,allowed)
            doc["observation_sha256"]="f"*64
            return doc
        with self.assertRaisesRegex(ValueError,"OBSERVATION_PREIMAGE_CHANGED"):
            self.capture(collector=bad)
    def test_declared_shared_ancestry(self):
        self.trust["controllers"]["controller0"].append("journal-root")
        self.pin=sha(self.trust)
        with self.assertRaisesRegex(ValueError,"SHARED_JOURNAL_ANCESTRY"):
            self.capture()
    def test_shared_endpoint_host(self):
        self.urls["k1"]="https://vault0.example.org/alternate"
        with self.assertRaisesRegex(ValueError,"ENDPOINT_HOST_REUSED"):
            self.capture()
    def test_bad_retention_signature(self):
        self.records["k0"]["signature_b64"]="AAAA"
        with self.assertRaisesRegex(ValueError,"RETENTION_SIGNATURE_INVALID"):
            self.capture()
    def test_retention_artifact_mismatch(self):
        self.records["k0"]["source_artifact_sha256"]="f"*64
        with self.assertRaisesRegex(ValueError,"RETENTION_RECORD_BINDING_INVALID"):
            self.capture()
    def test_source_change_between_windows(self):
        self.capture()
        self.urls["k0"]="https://vault0.example.org/renamed"
        with self.assertRaisesRegex(ValueError,"WINDOW_ANCESTRY_OR_ARTIFACT_DIVERGENCE"):
            self.capture(self.second)
    def test_changed_trust_pin(self):
        with self.assertRaisesRegex(ValueError,"PINNED_TRUST_OR_ENDPOINTS_INVALID"):
            capture(self.db,self.artifact,self.trust,"f"*64,self.urls,self.records,
                    self.first,self.collector)
    def test_historical_prefix_match(self):
        first,second=self.both()
        self.assertNotIn("HISTORICAL_WINDOW_REWRITTEN",
                         audit(self.db,1,first["head_sha256"])["reasons"])
    def test_historical_prefix_mismatch(self):
        self.both()
        self.assertIn("HISTORICAL_WINDOW_REWRITTEN",
                      audit(self.db,1,"f"*64)["reasons"])
    def test_removed_nonce_detected(self):
        self.both()
        with sqlite3.connect(self.db) as con:
            con.execute("DELETE FROM used_observation_nonce WHERE endpoint_id='k0' AND window_seq=1")
        self.assertIn("NONCE_OR_WITNESS_TRIPLE_DIVERGENCE",audit(self.db)["reasons"])
    def test_modified_journal_hash_detected(self):
        self.both()
        with sqlite3.connect(self.db) as con:
            con.execute("UPDATE observation_window SET head_sha=? WHERE seq=2",("f"*64,))
        self.assertIn("WINDOW_MANIFEST_HEAD_INVALID",audit(self.db)["reasons"])
    def test_missing_prefix_detected(self):
        self.capture()
        self.assertIn("HISTORICAL_WINDOW_REMOVED",audit(self.db,2,"f"*64)["reasons"])
    def test_no_physical_act(self):
        self.both()
        self.assertFalse(audit(self.db)["physical_act_allowed"])

if __name__=="__main__":unittest.main()
