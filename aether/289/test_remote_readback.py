import base64,hashlib,json,sqlite3,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from remote_readback import (capture,audit,anchor_statement,digest,sha,canon,
                             replay_anchor,SCHEMA,ZERO)
from export_audit import make_export

def obs(url,raw):
    host=url.split("/")[2]
    fields={"schema":"AETHER-264/https-acquisition-v1","requested_url":url,
            "host":host,"pinned_ip":"8.8.8.8","dns_address_count":1,
            "tls_hostname_validation":True,"status":200,"elapsed_ms":2,
            "raw_length":len(raw),"raw_sha256":digest(raw),
            "raw_b64":base64.b64encode(raw).decode()}
    return {**fields,"observation_sha256":sha(fields),"operational_authority":"HOLD"}

class Tests(unittest.TestCase):
    def setUp(self):
        temp=tempfile.TemporaryDirectory();self.addCleanup(temp.cleanup)
        self.home=Path(temp.name)
        self.source=self.home/"source.sqlite";self.ack=self.home/"ack.sqlite"
        self.db=self.home/"readback.sqlite"
        nw=[];local_nonces=[]
        for i in range(3):
            kid=f"k{i}"
            claim=canon({"key_id":kid,"witness_nonce":f"witness-nonce-{i}"})
            url=f"https://source{i}.example.org/witness"
            nw.append({"key_id":kid,"url":url,"claim_json":claim.decode(),
                       "observation":obs(url,claim)})
            local_nonces.append({"nonce":f"witness-nonce-{i}","batch_id":1,"key_id":kid})
        source_manifest={"schema":"AETHER-286/atomic-manifest-v1",
                         "trust_sha256":"a"*64,"challenge_nonce":"challenge-source",
                         "previous_head_sha256":ZERO,"witnesses":nw}
        source_row={"id":1,"challenge_nonce":"challenge-source","previous_sha":ZERO,
                    "head_sha":sha(source_manifest),"trust_sha":"a"*64,
                    "manifest_json":canon(source_manifest).decode()}
        db=sqlite3.connect(self.source)
        db.execute("CREATE TABLE batch(id INTEGER,challenge_nonce TEXT,previous_sha TEXT,head_sha TEXT,trust_sha TEXT,manifest_json TEXT)")
        db.execute("CREATE TABLE witness_nonce(nonce TEXT,batch_id INTEGER,key_id TEXT)")
        db.execute("INSERT INTO batch VALUES (?,?,?,?,?,?)",tuple(source_row.values()))
        for n in local_nonces:db.execute("INSERT INTO witness_nonce VALUES (?,?,?)",tuple(n.values()))
        db.commit();db.close()
        self.artifact=make_export([source_row],local_nonces,1)
        self.artifact_bytes=canon(self.artifact)
        acknowledgments=[]
        ack_rows=[]
        for i in range(3):
            kid=f"custodian{i}"
            claim={"custodian_id":kid,"controller_id":f"controller{i}",
                   "nonce":f"ack-nonce-{i}","batch_id":1,
                   "artifact_sha256":self.artifact["artifact_sha256"],
                   "head_sha256":self.artifact["head_sha256"],"signature_b64":"test-mock"}
            url=f"https://custodian{i}.example.org/ack"
            acknowledgments.append({"custodian_id":kid,"url":url,
                                    "observation":obs(url,canon(claim))})
            ack_rows.append((f"ack-nonce-{i}",1,kid))
        ack_manifest={"schema":"AETHER-288/ack-acquisition-v1",
                      "challenge_nonce":"challenge-acknowledgment",
                      "previous_head_sha256":ZERO,"trust_sha256":"b"*64,
                      "artifact_sha256":self.artifact["artifact_sha256"],
                      "acquisitions":acknowledgments}
        self.ack_head=sha(ack_manifest)
        db=sqlite3.connect(self.ack)
        db.execute("CREATE TABLE batch(id INTEGER,nonce TEXT,previous TEXT,head TEXT,manifest TEXT)")
        db.execute("CREATE TABLE receipt(nonce TEXT,batch INTEGER,custodian TEXT)")
        db.execute("INSERT INTO batch VALUES (?,?,?,?,?)",
                   (1,"challenge-acknowledgment",ZERO,self.ack_head,canon(ack_manifest).decode()))
        for n in ack_rows:db.execute("INSERT INTO receipt VALUES (?,?,?)",n)
        db.commit();db.close()
        self.url="https://external.example.org/export.json"
        self.nonce="fresh-readback-nonce-289"
    def collector(self,url,hosts):
        self.assertEqual(url,self.url)
        self.assertIn("external.example.org",hosts)
        return obs(url,self.artifact_bytes)
    def capture(self,collector=None,nonce=None):
        return capture(self.db,self.source,self.ack,self.artifact_bytes,
                       self.url,nonce or self.nonce,collector or self.collector)
    def test_remote_bytes_match(self):
        result=self.capture()
        self.assertTrue(result["remote_bytes_equal"])
        self.assertFalse(result["independent_external_custody_verified"])
    def test_persisted_recovery_audit(self):
        self.capture()
        report=audit(self.db,self.ack)
        self.assertEqual(report["readbacks"],1)
        self.assertNotIn("READBACK_HASH_CHANGED",report["reasons"])
    def test_anchor_current_head(self):
        result=self.capture();anchor=result["ack_highwater"]
        self.assertNotIn("ACK_PREFIX_REPLACED",audit(self.db,self.ack,anchor,sha(anchor))["reasons"])
    def test_anchor_wrong_digest(self):
        result=self.capture();anchor=result["ack_highwater"]
        self.assertIn("ANCHOR_DIGEST_CONFLICT",audit(self.db,self.ack,anchor,"f"*64)["reasons"])
    def test_anchor_prefix_replaced(self):
        result=self.capture();anchor=result["ack_highwater"]
        anchor["ack_head_sha256"]="f"*64
        self.assertIn("ACK_PREFIX_REPLACED",audit(self.db,self.ack,anchor,sha(anchor))["reasons"])
    def test_anchor_nonce_rollback(self):
        result=self.capture();anchor=result["ack_highwater"]
        anchor["ack_nonce_count"]=4
        self.assertIn("ACK_NONCE_HIGHWATER_ROLLBACK",audit(self.db,self.ack,anchor,sha(anchor))["reasons"])
    def test_duplicate_request_nonce(self):
        self.capture()
        with self.assertRaisesRegex(ValueError,"READBACK_NONCE_REPLAY"):self.capture()
    def test_remote_substituted_bytes(self):
        with self.assertRaisesRegex(ValueError,"REMOTE_EXPORTED_BYTES_DIVERGE"):
            self.capture(lambda url,hosts:obs(url,b"{}"))
        self.assertFalse(self.db.exists() and bool(sqlite3.connect(self.db).execute("SELECT COUNT(*) FROM readback").fetchone()[0]))
    def test_bad_raw_hash(self):
        def collector(url,hosts):
            o=self.collector(url,hosts);o["raw_sha256"]="f"*64;return o
        with self.assertRaisesRegex(ValueError,"REMOTE_BODY_DIGEST_OR_LENGTH_INVALID"):
            self.capture(collector)
    def test_bad_transport_hash(self):
        def collector(url,hosts):
            o=self.collector(url,hosts);o["observation_sha256"]="f"*64;return o
        with self.assertRaisesRegex(ValueError,"OBSERVATION_PREIMAGE_CHANGED"):
            self.capture(collector)
    def test_bad_hostname(self):
        def collector(url,hosts):
            o=self.collector(url,hosts);o["host"]="wrong.example.org";return o
        with self.assertRaisesRegex(ValueError,"ACQUISITION_TRANSPORT_MISMATCH"):
            self.capture(collector)
    def test_unsafe_http_rejected(self):
        with self.assertRaises(ValueError):
            capture(self.db,self.source,self.ack,self.artifact_bytes,
                    "http://external.example.org/export.json",self.nonce,self.collector)
    def test_altered_source_export(self):
        payload=json.loads(self.artifact_bytes)
        payload["artifact_sha256"]="f"*64
        with self.assertRaisesRegex(ValueError,"SOURCE_EXPORT_VERIFICATION_FAILED"):
            capture(self.db,self.source,self.ack,canon(payload),self.url,self.nonce,self.collector)
    def test_ack_db_missing(self):
        self.ack.unlink()
        with self.assertRaises(sqlite3.Error):self.capture()
    def test_ack_head_change_detected(self):
        self.capture()
        with sqlite3.connect(self.ack) as db:db.execute("UPDATE batch SET head=?",( "f"*64,))
        self.assertIn("ACK_HISTORY_REWRITTEN",audit(self.db,self.ack)["reasons"])
    def test_ack_nonce_deletion(self):
        self.capture()
        with sqlite3.connect(self.ack) as db:db.execute("DELETE FROM receipt WHERE custodian='custodian0'")
        self.assertIn("ACK_NONCE_ROLLBACK",audit(self.db,self.ack)["reasons"])
    def test_readback_manifest_tamper(self):
        self.capture()
        with sqlite3.connect(self.db) as db:db.execute("UPDATE readback SET artifact_sha=?",("f"*64,))
        self.assertIn("RETAINED_REMOTE_BODY_CHANGED",audit(self.db,self.ack)["reasons"])
    def test_noncanonical_export(self):
        with self.assertRaisesRegex(ValueError,"EXPORT_NOT_CANONICAL"):
            capture(self.db,self.source,self.ack,b" "+self.artifact_bytes,
                    self.url,self.nonce,self.collector)
    def test_no_physical_act(self):
        self.assertFalse(self.capture()["physical_act_allowed"])
if __name__=="__main__":unittest.main()
