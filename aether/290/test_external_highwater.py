import base64,hashlib,json,sqlite3,tempfile,unittest
from pathlib import Path
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from external_highwater import capture,audit,sha,canon,ZERO,RECORD_SCHEMA

def pem(key):
    return key.public_key().public_bytes(serialization.Encoding.PEM,serialization.PublicFormat.SubjectPublicKeyInfo).decode()
def observation(url,raw):
    host=url.split("/")[2]
    f={"schema":"AETHER-264/https-acquisition-v1","requested_url":url,"host":host,
       "pinned_ip":"8.8.8.8","dns_address_count":1,"tls_hostname_validation":True,
       "status":200,"elapsed_ms":1,"raw_length":len(raw),
       "raw_sha256":hashlib.sha256(raw).hexdigest(),"raw_b64":base64.b64encode(raw).decode()}
    return {**f,"observation_sha256":sha(f),"operational_authority":"HOLD"}
class Tests(unittest.TestCase):
    def setUp(self):
        t=tempfile.TemporaryDirectory();self.addCleanup(t.cleanup)
        self.db=Path(t.name)/"a290.sqlite";self.ack=Path(t.name)/"ack.sqlite"
        db=sqlite3.connect(self.ack)
        db.execute("CREATE TABLE batch(id INTEGER,nonce TEXT,previous TEXT,head TEXT,manifest TEXT)")
        db.execute("CREATE TABLE receipt(nonce TEXT,batch INTEGER,custodian TEXT)")
        data={"schema":"AETHER-288/ack-acquisition-v1","challenge_nonce":"c",
              "previous_head_sha256":ZERO,"trust_sha256":"a"*64,
              "artifact_sha256":"b"*64,"acquisitions":[]}
        self.head=sha(data)
        db.execute("INSERT INTO batch VALUES (?,?,?,?,?)",(1,"c",ZERO,self.head,canon(data).decode()))
        for i in range(3):db.execute("INSERT INTO receipt VALUES (?,?,?)",(f"nonce{i}",1,f"c{i}"))
        db.commit();db.close()
        self.keys={};keys={};graph={"journal":["jr"],"jr":[]};self.urls={};self.records={}
        self.challenge="external-retention-capture-290"
        self.artifact_sha="b"*64
        for i in range(3):
            kid=f"endpoint{i}";ctrl=f"controller{i}";k=Ed25519PrivateKey.generate()
            self.keys[kid]=k;keys[kid]={"controller_id":ctrl,"public_key_pem":pem(k)}
            graph[ctrl]=[f"root{i}"];graph[f"root{i}"]=[]
            url=f"https://custody{i}.example.org/retained";self.urls[kid]=url
            statement={"schema":RECORD_SCHEMA,"endpoint_id":kid,"controller_id":ctrl,
                       "challenge_nonce":self.challenge,"ack_batch_id":1,"ack_head_sha256":self.head,
                       "ack_nonce_count":3,"source_artifact_sha256":self.artifact_sha,
                       "retained_until_claim":"indefinite-claimed"}
            statement["signature_b64"]=base64.b64encode(k.sign(canon(statement))).decode()
            self.records[url]=canon(statement)
        self.trust={"endpoints":keys,"controller_ancestry":graph,"journal_controller":"journal"}
        self.pin=sha(self.trust)
    def collector(self,url,allow):
        self.assertIn(url.split("/")[2],allow)
        return observation(url,self.records[url])
    def capture(self,collector=None,pin=None,challenge=None):
        return capture(self.db,self.ack,self.trust,pin or self.pin,self.urls,
                       challenge or self.challenge,self.artifact_sha,collector or self.collector)
    def test_three_signed_retention_claims_still_hold(self):
        result=self.capture()
        self.assertEqual(result["retention_signatures_verified"],3)
        self.assertFalse(result["independent_external_custody_verified"])
    def test_recovered_manifest(self):
        self.capture();r=audit(self.db,self.ack)
        self.assertEqual(r["record_nonces"],3)
        self.assertNotIn("MANIFEST_PREIMAGE_INVALID",r["reasons"])
    def test_historical_prefix_match(self):
        result=self.capture();r=audit(self.db,self.ack,1,result["head_sha256"])
        self.assertNotIn("ANCHORED_BATCH_REWRITTEN",r["reasons"])
    def test_wrong_historical_prefix(self):
        self.capture()
        self.assertIn("ANCHORED_BATCH_REWRITTEN",audit(self.db,self.ack,1,"f"*64)["reasons"])
    def test_missing_historical_prefix(self):
        self.capture()
        self.assertIn("ANCHORED_BATCH_REMOVED",audit(self.db,self.ack,2,"f"*64)["reasons"])
    def test_duplicate_challenge(self):
        self.capture()
        with self.assertRaisesRegex(ValueError,"CHALLENGE_REPLAY"):self.capture()
    def test_same_claim_other_challenge_invalid(self):
        self.capture()
        with self.assertRaisesRegex(ValueError,"RECORD_BINDING_INVALID"):
            self.capture(challenge="other-retention-capture-290")
    def test_invalid_signature_atomic(self):
        url=self.urls["endpoint0"];claim=json.loads(self.records[url])
        claim["signature_b64"]="AAAA";self.records[url]=canon(claim)
        with self.assertRaisesRegex(ValueError,"RETENTION_SIGNATURE_INVALID"):self.capture()
        self.assertEqual(audit(self.db,self.ack)["batches"],0)
    def test_raw_digest_tamper(self):
        def bad(url,hosts):
            result=self.collector(url,hosts);result["raw_sha256"]="f"*64;return result
        with self.assertRaises(ValueError):self.capture(bad)
    def test_observation_hash_tamper(self):
        def bad(url,hosts):
            result=self.collector(url,hosts);result["observation_sha256"]="f"*64;return result
        with self.assertRaises(ValueError):self.capture(bad)
    def test_host_reuse(self):
        self.urls["endpoint1"]="https://custody0.example.org/other"
        with self.assertRaisesRegex(ValueError,"REUSED_HOST"):self.capture()
    def test_root_pin_changed(self):
        with self.assertRaisesRegex(ValueError,"TRUST_ROOT_PIN_INVALID"):
            self.capture(pin="f"*64)
    def test_shared_controller_ancestry(self):
        self.trust["controller_ancestry"]["controller1"].append("root0")
        self.pin=sha(self.trust)
        with self.assertRaisesRegex(ValueError,"SHARED_ENDPOINT_ANCESTRY"):self.capture()
    def test_journal_self_issued_ancestry(self):
        self.trust["controller_ancestry"]["controller0"].append("jr")
        self.pin=sha(self.trust)
        with self.assertRaisesRegex(ValueError,"SHARED_JOURNAL_ANCESTRY"):self.capture()
    def test_retention_metadata_does_not_prove_storage(self):
        result=self.capture()
        self.assertIn("REMOTE_IMMUTABILITY_UNVERIFIED",result["reasons"])
    def test_manifest_tamper(self):
        self.capture()
        with sqlite3.connect(self.db) as conn:
            conn.execute("UPDATE batch SET manifest_json='{}'")
        self.assertIn("MANIFEST_PREIMAGE_INVALID",audit(self.db,self.ack)["reasons"])
    def test_nonce_removed(self):
        self.capture()
        with sqlite3.connect(self.db) as conn:
            conn.execute("DELETE FROM record_nonce WHERE endpoint_id='endpoint0'")
        self.assertIn("NONCE_MANIFEST_DIVERGENCE",audit(self.db,self.ack)["reasons"])
    def test_ack_head_rollback(self):
        self.capture()
        with sqlite3.connect(self.ack) as conn:
            conn.execute("DELETE FROM batch")
        with self.assertRaisesRegex(ValueError,"ACK_HISTORY_INCOMPLETE"):
            audit(self.db,self.ack)
    def test_never_act(self):
        self.assertFalse(self.capture()["physical_act_allowed"])
if __name__=="__main__":unittest.main()
