import base64,hashlib,json,sqlite3,tempfile,unittest
from pathlib import Path
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from ack_acquisition import capture,audit,sha,canonical,ZERO
from export_audit import make_export,ACK_SCHEMA

def pub(k):
    return k.public_key().public_bytes(serialization.Encoding.PEM,
        serialization.PublicFormat.SubjectPublicKeyInfo).decode()
def signed(k,value):
    return base64.b64encode(k.sign(canonical(value))).decode()

class Tests(unittest.TestCase):
    def setUp(self):
        t=tempfile.TemporaryDirectory();self.addCleanup(t.cleanup)
        self.path=Path(t.name)/"acks.sqlite";self.journal=Path(t.name)/"journal.sqlite"
        witnesses=[];nonces=[]
        for i in range(3):
            key=f"k{i}";url=f"https://source{i}.example.org/witness"
            claim=canonical({"key_id":key,"witness_nonce":f"wnonce{i}"})
            fields={"schema":"AETHER-264/https-acquisition-v1","requested_url":url,
                    "host":f"source{i}.example.org","pinned_ip":"8.8.8.8","dns_address_count":1,
                    "tls_hostname_validation":True,"status":200,"elapsed_ms":1,
                    "raw_length":len(claim),"raw_sha256":hashlib.sha256(claim).hexdigest(),
                    "raw_b64":base64.b64encode(claim).decode()}
            witnesses.append({"key_id":key,"url":url,"observation":{**fields,"observation_sha256":sha(fields)},
                              "claim_json":claim.decode()})
            nonces.append({"nonce":f"wnonce{i}","batch_id":1,"key_id":key})
        manifest={"schema":"AETHER-286/atomic-manifest-v1","trust_sha256":"b"*64,
                  "challenge_nonce":"challenge-old","previous_head_sha256":ZERO,"witnesses":witnesses}
        row={"id":1,"challenge_nonce":"challenge-old","previous_sha":ZERO,
             "head_sha":sha(manifest),"trust_sha":"b"*64,"manifest_json":canonical(manifest).decode()}
        db=sqlite3.connect(self.journal)
        db.execute("CREATE TABLE batch (id INTEGER,challenge_nonce TEXT,previous_sha TEXT,head_sha TEXT,trust_sha TEXT,manifest_json TEXT)")
        db.execute("CREATE TABLE witness_nonce (nonce TEXT,batch_id INTEGER,key_id TEXT)")
        db.execute("INSERT INTO batch VALUES (?,?,?,?,?,?)",tuple(row.values()))
        for r in nonces:db.execute("INSERT INTO witness_nonce VALUES (?,?,?)",tuple(r.values()))
        db.commit();db.close()
        self.artifact=make_export([row],nonces,1)
        self.keys={};self.records={};self.urls={}
        graph={"journal":["journal-root"],"journal-root":[]};custodians={}
        for i in range(3):
            kid=f"custodian{i}";controller=f"controller{i}";k=Ed25519PrivateKey.generate()
            self.keys[kid]=k;graph[controller]=[f"root{i}"];graph[f"root{i}"]=[]
            custodians[kid]={"controller_id":controller,"public_key_pem":pub(k)}
            claim={"custodian_id":kid,"controller_id":controller,"nonce":f"ack-nonce-{i}",
                   "batch_id":1,"artifact_sha256":self.artifact["artifact_sha256"],
                   "head_sha256":self.artifact["head_sha256"]}
            claim["signature_b64"]=signed(k,{"schema":ACK_SCHEMA,**claim})
            url=f"https://custodian{i}.example.org/receipt";self.urls[kid]=url
            self.records[url]=canonical(claim)
        self.trust={"journal_controller":"journal","controllers":graph,"custodians":custodians}
        self.pin=sha(self.trust)
        self.challenge="capture-challenge-288-A"
    def collector(self,url,allowed):
        self.assertIn(url.split("/")[2],allowed)
        raw=self.records[url];host=url.split("/")[2]
        fields={"schema":"AETHER-264/https-acquisition-v1","requested_url":url,
                "host":host,"pinned_ip":"8.8.8.8","dns_address_count":1,
                "tls_hostname_validation":True,"status":200,"elapsed_ms":5,
                "raw_length":len(raw),"raw_sha256":hashlib.sha256(raw).hexdigest(),
                "raw_b64":base64.b64encode(raw).decode()}
        return {**fields,"observation_sha256":sha(fields),"operational_authority":"HOLD"}
    def run_capture(self,collector=None,challenge=None):
        return capture(self.path,self.journal,self.artifact,self.trust,self.pin,
                       self.urls,challenge or self.challenge,collector or self.collector)
    def test_valid_crypto_stays_hold(self):
        result=self.run_capture()
        self.assertFalse(result["independent_custody_verified"])
        self.assertEqual(result["receipt_count"],3)
    def test_local_replay_reconstructs(self):
        self.run_capture()
        self.assertEqual(audit(self.path)["reasons"],
                         ["EXTERNAL_CUSTODY_NOT_AUTHENTICATED","LOCAL_DATABASE_ROLLBACK_POSSIBLE"])
    def test_duplicate_capture_challenge(self):
        self.run_capture()
        with self.assertRaisesRegex(ValueError,"CHALLENGE_REPLAY"):self.run_capture()
    def test_persisted_nonce_replay(self):
        self.run_capture()
        with self.assertRaisesRegex(ValueError,"PERSISTED_NONCE_REPLAY"):
            self.run_capture(challenge="capture-challenge-288-B")
    def test_invalid_signature_atomic(self):
        url=self.urls["custodian0"];original=self.records[url]
        value=json.loads(original);value["signature_b64"]="AAAA"
        self.records[url]=canonical(value)
        with self.assertRaisesRegex(ValueError,"ACK_VALIDATION_FAILED"):self.run_capture()
        self.assertEqual(audit(self.path)["batches"],0)
        self.records[url]=original
        self.assertEqual(self.run_capture()["batch_id"],1)
    def test_substituted_body(self):
        def bad(url,allowed):
            result=self.collector(url,allowed);result["raw_b64"]="AAAA";return result
        with self.assertRaisesRegex(ValueError,"RAW_BODY_INVALID"):self.run_capture(bad)
    def test_substituted_observation_hash(self):
        def bad(url,allowed):
            result=self.collector(url,allowed);result["observation_sha256"]="f"*64;return result
        with self.assertRaisesRegex(ValueError,"OBSERVATION_SHA_INVALID"):self.run_capture(bad)
    def test_duplicate_endpoint_host(self):
        self.urls["custodian1"]="https://custodian0.example.org/different"
        with self.assertRaisesRegex(ValueError,"DUPLICATE_HOST"):self.run_capture()
    def test_stale_trust_pin(self):
        self.pin="f"*64
        with self.assertRaisesRegex(ValueError,"TRUST_PIN_INVALID"):self.run_capture()
    def test_export_mismatch(self):
        self.artifact["artifact_sha256"]="f"*64
        with self.assertRaisesRegex(ValueError,"EXPORT_PREIMAGE_INVALID"):self.run_capture()
    def test_manifest_tamper_detected(self):
        self.run_capture()
        with sqlite3.connect(self.path) as db:
            db.execute("UPDATE batch SET manifest='{}'")
        self.assertIn("MANIFEST_HEAD_MISMATCH",audit(self.path)["reasons"])
    def test_nonce_deleted_detected(self):
        self.run_capture()
        with sqlite3.connect(self.path) as db:
            db.execute("DELETE FROM receipt WHERE custodian='custodian0'")
        self.assertIn("RECEIPT_MANIFEST_DIVERGENCE",audit(self.path)["reasons"])
    def test_pinned_head(self):
        result=self.run_capture()
        self.assertNotIn("PREFIX_REPLACED",audit(self.path,1,result["head_sha256"])["reasons"])
        self.assertIn("PREFIX_REPLACED",audit(self.path,1,"f"*64)["reasons"])
    def test_crash_restart_readback(self):
        self.run_capture()
        self.assertEqual(audit(self.path)["nonces"],3)
    def test_no_act(self):
        self.assertFalse(self.run_capture()["physical_act_allowed"])

if __name__=="__main__":unittest.main()
