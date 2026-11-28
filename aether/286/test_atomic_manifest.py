import base64,json,sqlite3,sys,tempfile,unittest
from pathlib import Path
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"282"))
from retained_journal import ZERO,bootstrap,append,receipt_statement,canon,sha
from atomic_manifest import capture,inspect,readback,audit_rows,SCHEMA

def pem(k):return k.public_key().public_bytes(serialization.Encoding.PEM,serialization.PublicFormat.SubjectPublicKeyInfo).decode()
def sig(k,obj):return base64.b64encode(k.sign(canon(obj))).decode()
class Tests(unittest.TestCase):
    def setUp(self):
        t=tempfile.TemporaryDirectory();self.addCleanup(t.cleanup)
        self.db=Path(t.name)/"a286.sqlite";self.journal=Path(t.name)/"j.sqlite"
        owners=[Ed25519PrivateKey.generate() for _ in range(3)]
        registry=[{"source_id":f"s{i}","controller":f"owner{i}","pem":pem(k)} for i,k in enumerate(owners)]
        pin=sha(registry);bootstrap(self.journal,registry,pin)
        ch={"id":"c1","nonce":"challenge-286","source_commit":"a"*40,"run_id":286}
        receipts=[]
        for i,k in enumerate(owners):
            source=f"s{i}";sid=f"session{i}";nonce=f"nn{i}";payload="b"*64
            receipts.append({"source_id":source,"session_id":sid,"session_nonce":nonce,
                             "payload_sha256":payload,"signature_b64":sig(k,receipt_statement(ch,pin,source,sid,nonce,payload))})
        self.prefix=append(self.journal,{"challenge":ch,"receipts":receipts},pin,ZERO)["head_sha256"]
        graph={"journal":["jroot"],"jroot":[]}
        self.keys={};self.urls={};self.raw={}
        for i in range(3):
            k=Ed25519PrivateKey.generate();kid=f"k{i}";controller=f"w{i}"
            graph[controller]=[f"wroot{i}"];graph[f"wroot{i}"]=[]
            self.keys[kid]={"controller_id":controller,"public_key_pem":pem(k)}
            url=f"https://w{i}.example.org/prefix";self.urls[kid]=url
            claim={"key_id":kid,"controller_id":controller,"witness_nonce":f"nonce-{i}",
                   "prefix_seq":1,"prefix_sha256":self.prefix,"run_id":286}
            claim["signature_b64"]=sig(k,{"schema":"AETHER-283/prefix-witness-v1",**claim})
            self.raw[url]=canon(claim)
        self.trust={"witness_keys":self.keys,"controller_ancestry":graph,"journal_controller":"journal"}
        self.pin=sha(self.trust);self.challenge="fresh-batch-challenge-286"
    def collector(self,url,allow):
        self.assertIn(url.split("/")[2],allow)
        raw=self.raw[url]
        fields={"schema":"AETHER-264/https-acquisition-v1","requested_url":url,"host":url.split("/")[2],
                "pinned_ip":"8.8.8.8","dns_address_count":1,"tls_hostname_validation":True,
                "status":200,"elapsed_ms":5,"raw_length":len(raw),"raw_sha256":__import__("hashlib").sha256(raw).hexdigest(),
                "raw_b64":base64.b64encode(raw).decode()}
        observation={**fields,"observation_sha256":sha(fields),"operational_authority":"HOLD"}
        return observation
    def commit(self,collector=None,nonce=None):
        return capture(self.db,self.journal,self.trust,self.pin,self.urls,
                       nonce or self.challenge,collector or self.collector)
    def test_atomic_manifest_retention(self):
        result=self.commit()
        self.assertEqual(result["manifest_preimages_retained"],3)
        self.assertEqual(inspect(self.db)["witness_nonces"],3)
    def test_complete_replay(self):
        self.commit()
        self.assertEqual(audit_rows(*readback(self.db)),[])
    def test_prefix_pin(self):
        first=self.commit()
        self.assertNotIn("EXTERNAL_PREFIX_CONFLICT",inspect(self.db,1,first["head_sha256"])["reasons"])
    def test_bad_external_prefix(self):
        self.commit()
        self.assertIn("EXTERNAL_PREFIX_CONFLICT",inspect(self.db,1,"f"*64)["reasons"])
    def test_manifest_url_change_detected(self):
        self.commit()
        with sqlite3.connect(self.db) as db:
            manifest=json.loads(db.execute("SELECT manifest_json FROM batch").fetchone()[0])
            manifest["witnesses"][0]["url"]="https://replaced.example.org/prefix"
            db.execute("UPDATE batch SET manifest_json=?",(canon(manifest).decode(),))
        self.assertIn("BATCH_HEAD_TAMPER",inspect(self.db)["reasons"])
    def test_nonce_removal_detected(self):
        self.commit()
        with sqlite3.connect(self.db) as db:
            db.execute("DELETE FROM witness_nonce WHERE key_id='k0'")
        self.assertIn("THREE_WITNESS_CONSERVATION_INVALID",inspect(self.db)["reasons"])
    def test_claim_raw_change_detected(self):
        self.commit()
        with sqlite3.connect(self.db) as db:
            manifest=json.loads(db.execute("SELECT manifest_json FROM batch").fetchone()[0])
            manifest["witnesses"][0]["claim_json"]="{}"
            db.execute("UPDATE batch SET manifest_json=?",(canon(manifest).decode(),))
        self.assertIn("RETAINED_PREIMAGE_INVALID",inspect(self.db)["reasons"])
    def test_replay_challenge_rejected(self):
        self.commit()
        with self.assertRaisesRegex(ValueError,"PERSISTED_CHALLENGE_REPLAY"):self.commit()
    def test_replay_witness_rejected(self):
        self.commit()
        with self.assertRaisesRegex(ValueError,"PERSISTED_WITNESS_REPLAY"):
            self.commit(nonce="second-batch-challenge-286")
    def test_bad_signed_prefix_rolls_back(self):
        url=self.urls["k0"];original=self.raw[url]
        record=json.loads(original);record["signature_b64"]="AAAA";self.raw[url]=canon(record)
        with self.assertRaisesRegex(ValueError,"SIGNED_PREFIX_REJECTED"):self.commit()
        self.assertEqual(inspect(self.db)["batches"],0)
        self.raw[url]=original
        self.assertEqual(self.commit()["batch_id"],1)
    def test_observation_hash_mismatch(self):
        def bad(url,allow):
            o=self.collector(url,allow);o["observation_sha256"]="f"*64;return o
        with self.assertRaisesRegex(ValueError,"OBSERVATION_PREIMAGE_TAMPER"):self.commit(bad)
    def test_shared_endpoint_blocked(self):
        self.urls["k1"]="https://w0.example.org/other"
        with self.assertRaisesRegex(ValueError,"DUPLICATE_ENDPOINT_HOST"):self.commit()
    def test_invalid_raw_body_blocked(self):
        def bad(url,allow):
            o=self.collector(url,allow);o["raw_sha256"]="f"*64;return o
        with self.assertRaisesRegex(ValueError,"RAW_BODY_TAMPER"):self.commit(bad)
    def test_physical_act_hold(self):
        self.commit()
        self.assertFalse(inspect(self.db)["physical_act_allowed"])
if __name__=="__main__":unittest.main()
