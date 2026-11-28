import base64,copy,hashlib,json,sqlite3,tempfile,unittest
from pathlib import Path
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from export_audit import (SCHEMA,ACK_SCHEMA,ZERO,sha,canonical,make_export,
                          export,verify_export,audit,readback)

def pub(k):
    return k.public_key().public_bytes(serialization.Encoding.PEM,
        serialization.PublicFormat.SubjectPublicKeyInfo).decode()

def fixture():
    manifest_witnesses=[]
    nonces=[]
    for i in range(3):
        key=f"k{i}"
        claim={"key_id":key,"witness_nonce":f"nonce-{i}"}
        raw=canonical(claim)
        url=f"https://source{i}.example.org/witness"
        obs={"schema":"AETHER-264/https-acquisition-v1","requested_url":url,
             "host":f"source{i}.example.org","pinned_ip":"8.8.8.8",
             "dns_address_count":1,"tls_hostname_validation":True,
             "status":200,"elapsed_ms":1,"raw_length":len(raw),
             "raw_sha256":hashlib.sha256(raw).hexdigest(),
             "raw_b64":base64.b64encode(raw).decode()}
        obs["observation_sha256"]=sha(obs)
        manifest_witnesses.append({"key_id":key,"url":url,"observation":obs,
                                   "claim_json":raw.decode()})
        nonces.append({"nonce":f"nonce-{i}","batch_id":1,"key_id":key})
    manifest={"schema":"AETHER-286/atomic-manifest-v1","trust_sha256":"b"*64,
              "challenge_nonce":"challenge-287-test","previous_head_sha256":ZERO,
              "witnesses":manifest_witnesses}
    head=sha(manifest)
    row={"id":1,"challenge_nonce":"challenge-287-test","previous_sha":ZERO,
         "head_sha":head,"trust_sha":"b"*64,
         "manifest_json":canonical(manifest).decode()}
    return [row],nonces

class Tests(unittest.TestCase):
    def setUp(self):
        t=tempfile.TemporaryDirectory();self.addCleanup(t.cleanup)
        self.db=Path(t.name)/"acquisition.sqlite"
        rows,nonces=fixture()
        db=sqlite3.connect(self.db)
        db.execute("CREATE TABLE batch(id INTEGER PRIMARY KEY,challenge_nonce TEXT,previous_sha TEXT,head_sha TEXT,trust_sha TEXT,manifest_json TEXT)")
        db.execute("CREATE TABLE witness_nonce(nonce TEXT PRIMARY KEY,batch_id INTEGER,key_id TEXT)")
        for row in rows:
            db.execute("INSERT INTO batch VALUES (?,?,?,?,?,?)",
                       tuple(row[k] for k in ("id","challenge_nonce","previous_sha","head_sha","trust_sha","manifest_json")))
        for row in nonces:
            db.execute("INSERT INTO witness_nonce VALUES (?,?,?)",
                       (row["nonce"],row["batch_id"],row["key_id"]))
        db.commit();db.close()
        self.artifact=make_export(*readback(self.db),1)
        self.keys={}
        graph={"journal":["journal-root"],"journal-root":[]}
        custodians={};acks=[]
        for i in range(3):
            k=Ed25519PrivateKey.generate();kid=f"custodian{i}";ctrl=f"controller{i}"
            self.keys[kid]=k
            graph[ctrl]=[f"root{i}"];graph[f"root{i}"]=[]
            custodians[kid]={"controller_id":ctrl,"public_key_pem":pub(k)}
            statement={"schema":ACK_SCHEMA,"custodian_id":kid,"controller_id":ctrl,
                       "nonce":f"acknonce{i}","batch_id":1,
                       "artifact_sha256":self.artifact["artifact_sha256"],
                       "head_sha256":self.artifact["head_sha256"]}
            a={key:val for key,val in statement.items() if key!="schema"}
            a["signature_b64"]=base64.b64encode(k.sign(canonical(statement))).decode()
            acks.append(a)
        trust={"journal_controller":"journal","controllers":graph,"custodians":custodians}
        self.bundle={"trust":trust,"acknowledgments":acks,"consumed_nonces":[]}
        self.pin=sha(trust)
    def audit(self):
        return audit(self.db,self.artifact,self.bundle,self.pin)
    def test_complete_preimage_export(self):
        rows,nonces=readback(self.db)
        self.assertEqual(verify_export(self.artifact,rows,nonces),[])
        self.assertEqual(len(base64.b64decode(self.artifact["manifest_bytes_b64"])),len(rows[0]["manifest_json"]))
    def test_export_file_exact_and_exclusive(self):
        target=self.db.parent/"export.json"
        export(self.db,1,target)
        self.assertEqual(target.read_bytes(),canonical(self.artifact))
        with self.assertRaises(FileExistsError):export(self.db,1,target)
    def test_valid_signatures_still_hold(self):
        result=self.audit()
        self.assertTrue(all(s["valid"] for s in result["observed"]["signature_checks"]))
        self.assertIn("EXTERNAL_RETENTION_NOT_OBSERVED",result["reasons"])
    def test_artifact_byte_change(self):
        self.artifact["manifest_bytes_b64"]="AAAA"
        self.assertIn("EXPORT_PREIMAGE_OR_NONCE_MISMATCH",self.audit()["reasons"])
    def test_artifact_nonce_change(self):
        self.artifact["nonce_rows"][0]["nonce"]="substitute"
        self.assertIn("EXPORT_PREIMAGE_OR_NONCE_MISMATCH",self.audit()["reasons"])
    def test_artifact_checksum_change(self):
        self.artifact["artifact_sha256"]="f"*64
        self.assertIn("EXPORT_ARTIFACT_DIGEST_INVALID",self.audit()["reasons"])
    def test_wrong_trust_pin(self):
        self.pin="f"*64
        self.assertIn("TRUST_ROOT_PIN_CONFLICT",self.audit()["reasons"])
    def test_required_trust_pin(self):
        self.pin=None
        self.assertIn("OUT_OF_BAND_TRUST_ROOT_REQUIRED",self.audit()["reasons"])
    def test_ack_signature_substitution(self):
        self.bundle["acknowledgments"][0]["signature_b64"]="AAAA"
        self.assertIn("ACK_SIGNATURE_INVALID",self.audit()["reasons"])
    def test_ack_export_substitution(self):
        self.bundle["acknowledgments"][0]["head_sha256"]="f"*64
        self.assertIn("ACK_EXPORT_SUBSTITUTION",self.audit()["reasons"])
    def test_ack_nonce_replay(self):
        self.bundle["consumed_nonces"].append("acknonce0")
        self.assertIn("ACK_NONCE_REPLAY",self.audit()["reasons"])
    def test_shared_ancestry(self):
        self.bundle["trust"]["controllers"]["controller1"].append("root0")
        self.pin=sha(self.bundle["trust"])
        self.assertIn("ACK_SHARED_CONTROLLER_ANCESTRY",self.audit()["reasons"])
    def test_journal_self_issued(self):
        self.bundle["trust"]["controllers"]["controller0"].append("journal-root")
        self.pin=sha(self.bundle["trust"])
        self.assertIn("JOURNAL_ACK_SHARED_ANCESTRY",self.audit()["reasons"])
    def test_controller_cycle(self):
        self.bundle["trust"]["controllers"]["root0"].append("controller0")
        self.pin=sha(self.bundle["trust"])
        self.assertIn("ANCESTRY_CYCLE",self.audit()["reasons"])
    def test_missing_local_batch(self):
        with sqlite3.connect(self.db) as db:db.execute("DELETE FROM batch")
        self.assertIn("EXPORT_BATCH_MISSING",self.audit()["reasons"])
    def test_restart_readback(self):
        artifact=self.artifact
        rows,nonces=readback(self.db)
        self.assertEqual(make_export(rows,nonces,1),artifact)
    def test_missing_acknowledgment(self):
        self.bundle["acknowledgments"].pop()
        self.assertIn("THREE_ACKNOWLEDGMENTS_REQUIRED",self.audit()["reasons"])
    def test_never_authorize_act(self):
        self.assertFalse(self.audit()["physical_act_allowed"])

if __name__=="__main__":
    unittest.main()
