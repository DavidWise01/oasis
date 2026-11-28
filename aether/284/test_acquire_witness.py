import base64,json,sqlite3,tempfile,unittest,sys
from pathlib import Path
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"282"))
from retained_journal import ZERO,bootstrap,append,receipt_statement,canon,sha
from acquire_witness import acquire_and_seal,inspect,objhash,digest,raw_body,SCHEMA

def pem(key):
    return key.public_key().public_bytes(serialization.Encoding.PEM,
         serialization.PublicFormat.SubjectPublicKeyInfo).decode()
def signed(key,obj):
    return base64.b64encode(key.sign(canon(obj))).decode()

class Tests(unittest.TestCase):
    def setUp(self):
        t=tempfile.TemporaryDirectory();self.addCleanup(t.cleanup)
        self.db=Path(t.name)/"nonce.sqlite";self.journal=Path(t.name)/"journal.sqlite"
        self.signers=[Ed25519PrivateKey.generate() for _ in range(3)]
        entries=[{"source_id":f"s{i}","controller":f"owner{i}","pem":pem(self.signers[i])} for i in range(3)]
        pin=sha(entries);bootstrap(self.journal,entries,pin)
        challenge={"id":"frozen","nonce":"frozen-284","source_commit":"a"*40,"run_id":284}
        receipts=[]
        for i,key in enumerate(self.signers):
            s=f"s{i}";sid=f"session{i}";nonce=f"nonce{i}";payload="b"*64
            receipts.append({"source_id":s,"session_id":sid,"session_nonce":nonce,
                "payload_sha256":payload,
                "signature_b64":signed(key,receipt_statement(challenge,pin,s,sid,nonce,payload))})
        self.head=append(self.journal,{"challenge":challenge,"receipts":receipts},pin,ZERO)["head_sha256"]
        self.keys={};graph={"journal":["journal-root"],"journal-root":[]};self.records={}
        self.urls={}
        for i in range(3):
            key=Ed25519PrivateKey.generate();kid=f"k{i}";controller=f"w{i}"
            self.keys[kid]={"controller_id":controller,"public_key_pem":pem(key)}
            graph[controller]=[f"wroot{i}"];graph[f"wroot{i}"]=[]
            url=f"https://w{i}.example.org/record";self.urls[kid]=url
            claim={"key_id":kid,"controller_id":controller,"witness_nonce":f"witness-nonce-{i}",
                   "prefix_seq":1,"prefix_sha256":self.head,"run_id":284}
            claim["signature_b64"]=signed(key,{"schema":"AETHER-283/prefix-witness-v1",**claim})
            self.records[url]=canon(claim)
        self.trust={"witness_keys":self.keys,"controller_ancestry":graph,"journal_controller":"journal"}
        self.pin=objhash(self.trust)
        self.challenge="distinct-capture-nonce-284"
    def acquire(self,url,allow):
        assert url.split("/")[2] in allow
        data=self.records[url]
        observation={"schema":"AETHER-264/https-acquisition-v1","requested_url":url,
                     "host":url.split("/")[2],"tls_hostname_validation":True,
                     "status":200,"raw_b64":base64.b64encode(data).decode(),
                     "raw_length":len(data),"raw_sha256":digest(data)}
        observation["observation_sha256"]=objhash(observation)
        return observation
    def run_capture(self,collector=None,challenge=None):
        return acquire_and_seal(self.db,self.journal,self.trust,self.pin,self.urls,
            challenge or self.challenge,collector or self.acquire)
    def test_mock_acquisition_signed_custody_hold(self):
        report=self.run_capture()
        self.assertEqual(len(report["witness_records"]),3)
        self.assertFalse(report["independent_external_custody_verified"])
    def test_persistent_nonce_count(self):
        self.run_capture();self.assertEqual(inspect(self.db)["witness_nonces"],3)
    def test_replay_challenge(self):
        self.run_capture()
        with self.assertRaisesRegex(ValueError,"PERSISTED_CHALLENGE_REPLAY"):self.run_capture()
    def test_replay_witness_with_new_challenge(self):
        self.run_capture()
        with self.assertRaisesRegex(ValueError,"PERSISTED_WITNESS_REPLAY"):
            self.run_capture(challenge="different-capture-nonce-284")
    def test_bad_pin(self):
        with self.assertRaisesRegex(ValueError,"TRUST_ROOT_PIN_MISMATCH"):
            acquire_and_seal(self.db,self.journal,self.trust,"f"*64,self.urls,self.challenge,self.acquire)
    def test_changed_raw(self):
        def bad(url,allow):
            o=self.acquire(url,allow)
            o["raw_b64"]=base64.b64encode(b"garbage").decode()
            return o
        with self.assertRaisesRegex(ValueError,"RAW_SIZE_INVALID"):
            self.run_capture(bad)
    def test_bad_observation_digest(self):
        def bad(url,allow):
            o=self.acquire(url,allow);o["observation_sha256"]="f"*64;return o
        with self.assertRaisesRegex(ValueError,"OBSERVATION_HASH_INVALID"):self.run_capture(bad)
    def test_non_tls_claim(self):
        def bad(url,allow):
            o=self.acquire(url,allow);o["tls_hostname_validation"]=False;return o
        with self.assertRaisesRegex(ValueError,"TLS_HOST_OBSERVATION_INVALID"):self.run_capture(bad)
    def test_hostname_substitution(self):
        def bad(url,allow):
            o=self.acquire(url,allow);o["host"]="evil.example.org";return o
        with self.assertRaisesRegex(ValueError,"TLS_HOST_OBSERVATION_INVALID"):self.run_capture(bad)
    def test_bad_signed_claim(self):
        url=self.urls["k0"];claim=json.loads(self.records[url])
        claim["signature_b64"]="AAAA";self.records[url]=canon(claim)
        with self.assertRaisesRegex(ValueError,"PREFIX_REVIEW_REJECTED"):self.run_capture()
        self.assertEqual(inspect(self.db)["batches"],0)
    def test_missing_prefix(self):
        url=self.urls["k0"];claim=json.loads(self.records[url])
        claim["prefix_seq"]=10;self.records[url]=canon(claim)
        with self.assertRaisesRegex(ValueError,"PREFIX_REVIEW_REJECTED"):self.run_capture()
    def test_duplicate_witness_nonce(self):
        url=self.urls["k1"];claim=json.loads(self.records[url])
        claim["witness_nonce"]="witness-nonce-0";self.records[url]=canon(claim)
        with self.assertRaisesRegex(ValueError,"WITNESS_NONCE_DUPLICATE"):self.run_capture()
    def test_shared_hostname(self):
        self.urls["k1"]="https://w0.example.org/other"
        with self.assertRaisesRegex(ValueError,"SHARED_ENDPOINT_HOST"):self.run_capture()
    def test_http_rejected(self):
        self.urls["k1"]="http://w1.example.org/record"
        with self.assertRaises(ValueError):self.run_capture()
    def test_recovered_ledger_still_hold(self):
        self.run_capture();r=inspect(self.db)
        self.assertFalse(r["physical_act_allowed"])
    def test_failed_receipt_does_not_consume_nonce(self):
        url=self.urls["k0"];raw=self.records[url];self.records[url]=b"{}"
        with self.assertRaises(ValueError):self.run_capture()
        self.records[url]=raw
        self.assertEqual(self.run_capture()["batch_id"],1)
if __name__=="__main__":unittest.main()
