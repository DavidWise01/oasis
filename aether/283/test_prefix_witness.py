import base64,copy,json,os,sqlite3,subprocess,sys,tempfile,unittest
from pathlib import Path
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"282"))
from retained_journal import bootstrap,append,receipt_statement,canon,sha,ZERO
from prefix_witness import assess,SCHEMA

def pem(k):
    return k.public_key().public_bytes(serialization.Encoding.PEM,serialization.PublicFormat.SubjectPublicKeyInfo).decode()
def signed(k,stmt):
    return base64.b64encode(k.sign(canon(stmt))).decode()

class Tests(unittest.TestCase):
    def setUp(self):
        temp=tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.path=Path(temp.name)/"j.sqlite"
        self.keys={f"source{i}":Ed25519PrivateKey.generate() for i in range(3)}
        self.entries=[{"source_id":s,"controller":f"controller{s[-1]}","pem":pem(k)} for s,k in self.keys.items()]
        self.pin=sha(self.entries)
        bootstrap(self.path,self.entries,self.pin)
    def bundle(self,n):
        c={"id":f"challenge-{n}","nonce":f"challenge{n}","source_commit":"a"*40,"run_id":282+n}
        receipts=[]
        for i in range(3):
            source=f"source{i}"
            r={"source_id":source,"session_id":f"session{n}-{i}",
               "session_nonce":f"sessionnonce{n}-{i}","payload_sha256":"b"*64}
            stmt=receipt_statement(c,self.pin,source,r["session_id"],r["session_nonce"],r["payload_sha256"])
            r["signature_b64"]=signed(self.keys[source],stmt)
            receipts.append(r)
        return {"challenge":c,"receipts":receipts}
    def populate(self):
        h=append(self.path,self.bundle(1),self.pin,ZERO)
        return h["head_sha256"]
    def witness(self,head):
        keys={};graph={"journal":["journal-root"],"journal-root":[]};claims=[]
        for i in range(3):
            k=Ed25519PrivateKey.generate();key=f"k{i}";controller=f"w{i}"
            graph[controller]=[f"wroot{i}"];graph[f"wroot{i}"]=[]
            keys[key]={"controller_id":controller,"public_key_pem":pem(k)}
            item={"key_id":key,"controller_id":controller,"witness_nonce":f"nonce{i}",
                  "prefix_seq":1,"prefix_sha256":head,"run_id":283}
            item["signature_b64"]=signed(k,{"schema":SCHEMA,**item})
            claims.append(item)
        trust={"witness_keys":keys,"controller_ancestry":graph,"journal_controller":"journal"}
        return {"trust_record":trust,"witnesses":claims,"previous_witness_nonces":[]},sha(trust)
    def expect(self,modify,reason):
        h=self.populate();b,p=self.witness(h);modify(b)
        r=assess(self.path,b,p)
        self.assertIn(reason,r["reasons"],r)
        self.assertEqual(r["operational_authority"],"HOLD")
    def test_signatures_valid_but_custody_hold(self):
        h=self.populate();b,p=self.witness(h)
        r=assess(self.path,b,p)
        self.assertTrue(all(s["valid"] for s in r["observed"]["witness_signatures"]))
        self.assertIn("WITNESS_PUBLIC_KEY_CUSTODY_UNVERIFIED",r["reasons"])
    def test_prefix_rewrite(self):
        self.expect(lambda b:b["witnesses"][0].update(prefix_sha256="f"*64),"ANCHORED_PREFIX_REWRITTEN")
    def test_missing_prefix(self):
        self.expect(lambda b:b["witnesses"][0].update(prefix_seq=2),"ANCHORED_PREFIX_REMOVED")
    def test_wrong_trust_pin(self):
        h=self.populate();b,p=self.witness(h)
        self.assertIn("OUT_OF_BAND_TRUST_DIGEST_MISMATCH",assess(self.path,b,"f"*64)["reasons"])
    def test_required_trust_pin(self):
        h=self.populate();b,p=self.witness(h)
        self.assertIn("OUT_OF_BAND_TRUST_DIGEST_REQUIRED",assess(self.path,b,None)["reasons"])
    def test_wrong_signature(self):
        self.expect(lambda b:b["witnesses"][0].update(signature_b64="AAAA"),"WITNESS_SIGNATURE_INVALID")
    def test_key_substitution(self):
        self.expect(lambda b:b["trust_record"]["witness_keys"]["k0"].update(
            public_key_pem=b["trust_record"]["witness_keys"]["k1"]["public_key_pem"]),"WITNESS_SIGNATURE_INVALID")
    def test_replayed_nonce(self):
        self.expect(lambda b:b["previous_witness_nonces"].append("nonce0"),"WITNESS_NONCE_REPLAY")
    def test_duplicate_nonce(self):
        self.expect(lambda b:b["witnesses"][1].update(witness_nonce="nonce0"),"WITNESS_NONCE_REPLAY")
    def test_shared_witness_controller(self):
        self.expect(lambda b:b["trust_record"]["controller_ancestry"]["w1"].append("wroot0"),"WITNESS_SHARED_CONTROLLER_ANCESTRY")
    def test_self_issued_witness(self):
        self.expect(lambda b:b["trust_record"]["controller_ancestry"]["w0"].append("journal-root"),"SELF_ISSUED_OR_SHARED_JOURNAL_ANCESTRY")
    def test_witness_claims_conflict(self):
        self.expect(lambda b:b["witnesses"][1].update(prefix_sha256="f"*64),"WITNESS_PREFIX_CLAIM_CONFLICT")
    def test_invalid_bundle(self):
        h=self.populate();b,p=self.witness(h)
        self.assertIn("BUNDLE_SCHEMA_INVALID",assess(self.path,None,p)["reasons"])
    def test_original_challenge_signature_tamper(self):
        h=self.populate();b,p=self.witness(h)
        with sqlite3.connect(self.path) as db:
            db.execute("UPDATE receipt SET signature_b64='AAAA' WHERE source_id='source0'")
        self.assertIn("JOURNAL_STORED_RECEIPT_SIGNATURE_INVALID",assess(self.path,b,p)["reasons"])
    def test_uncommitted_process_exit(self):
        script="import sqlite3,os,sys; c=sqlite3.connect(sys.argv[1]);c.execute('BEGIN IMMEDIATE');c.execute('INSERT INTO challenge VALUES (?,?,?)',('uncommitted','{}','a'*64));os._exit(21)"
        result=subprocess.run([sys.executable,"-c",script,str(self.path)],timeout=10)
        self.assertEqual(result.returncode,21)
        self.assertEqual(sqlite3.connect(self.path).execute("SELECT COUNT(*) FROM challenge").fetchone()[0],0)
    def test_recovered_committed_prefix(self):
        head=self.populate();b,p=self.witness(head)
        subprocess.run([sys.executable,"-c","import sqlite3,sys;c=sqlite3.connect(sys.argv[1]);print(c.execute('SELECT COUNT(*) FROM head').fetchone()[0])",str(self.path)],check=True,stdout=subprocess.DEVNULL)
        self.assertEqual(assess(self.path,b,p)["observed"]["local_heads"],1)
    def test_no_physical_act(self):
        h=self.populate();b,p=self.witness(h)
        self.assertFalse(assess(self.path,b,p)["physical_act_allowed"])
if __name__=="__main__":unittest.main()
