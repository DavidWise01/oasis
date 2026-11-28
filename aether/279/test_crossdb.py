import copy,sqlite3,tempfile,unittest
from pathlib import Path
from crossdb import capture,reconcile,sha,SCHEMA
from highwater import statement

def fixture():
    registry=[{"source_id":f"source{i}","controller":f"ctrl{i}","key_pem":f"PEM{i}","version":1} for i in range(3)]
    challenges=[{"nonce":"c1","digest":"a"*64,"registry":sha(registry)}]
    receipts=[{"nonce":f"n{i}","session":f"s{i}","challenge":"c1",
               "source":f"source{i}","payload":"b"*64,"signature":"sig"} for i in range(3)]
    data={"registry":registry,"challenges":challenges,"receipts":receipts,"rotations":[],"highwater":[]}
    entry=statement(1,"0"*64,sha(registry),1,3,0,279)
    data["highwater"]=[{"seq":1,"previous_sha":"0"*64,"head_sha":sha(entry),
                       "registry_sha":sha(registry),"challenges":1,"receipts":3,"rotations":0,"run_id":279}]
    anchor={"schema":SCHEMA,"minimum_seq":1,"head_sha256":sha(entry),
            "minimum_run_id":279,"custodian_claim":"claimed-external"}
    return data,anchor,sha(anchor)
class Tests(unittest.TestCase):
    def expect(self,modify,reason):
        d,a,p=fixture();modify(d,a)
        r=reconcile(d,a,p)
        self.assertIn(reason,r["reasons"],r)
        self.assertEqual(r["operational_authority"],"HOLD")
    def test_matched_local_state_still_hold(self):
        d,a,p=fixture();r=reconcile(d,a,p)
        self.assertIn("CROSS_DATABASE_COMMIT_ATOMICITY_UNPROVEN",r["reasons"])
        self.assertFalse(r["external_custody_verified"])
    def test_highwater_missing(self):
        self.expect(lambda d,a:d["highwater"].clear(),"HIGHWATER_EMPTY")
    def test_receipt_removed(self):
        self.expect(lambda d,a:d["receipts"].pop(),"RECOVERED_RECEIPTS_BELOW_HIGHWATER")
    def test_challenge_removed(self):
        self.expect(lambda d,a:d["challenges"].clear(),"RECOVERED_CHALLENGES_BELOW_HIGHWATER")
    def test_unanchored_addition(self):
        self.expect(lambda d,a:d["receipts"].append(copy.deepcopy(d["receipts"][0])),"HIGHWATER_RECEIPTS_LAGGING")
    def test_registry_replaced(self):
        self.expect(lambda d,a:d["registry"][0].update(key_pem="changed"),"REGISTRY_HIGHWATER_DIVERGENCE")
    def test_another_session_same_nonce(self):
        self.expect(lambda d,a:d["receipts"][1].update(nonce="n0"),"DUPLICATED_SESSION")
    def test_orphan_receipt(self):
        self.expect(lambda d,a:d["receipts"][0].update(challenge="absent"),"ORPHAN_RECEIPT")
    def test_two_sources_only(self):
        self.expect(lambda d,a:d["receipts"][2].update(source="source1"),"INCOMPLETE_SOURCE_TRIPLE")
    def test_counter_correction_without_digest(self):
        self.expect(lambda d,a:d["highwater"][0].update(receipts=2),"HIGHWATER_CHECKPOINT_HASH_MISMATCH")
    def test_wrong_anchor_digest(self):
        d,a,p=fixture();self.assertIn("EXTERNAL_ANCHOR_PIN_CONFLICT",reconcile(d,a,"f"*64)["reasons"])
    def test_anchor_digest_required(self):
        d,a,p=fixture();self.assertIn("EXTERNAL_ANCHOR_DIGEST_REQUIRED",reconcile(d,a,None)["reasons"])
    def test_anchored_head_mismatch(self):
        self.expect(lambda d,a:a.update(head_sha256="f"*64),"ANCHORED_HISTORY_REWRITTEN")
    def test_older_run(self):
        self.expect(lambda d,a:a.update(minimum_run_id=300),"RUN_ID_ROLLBACK")
    def test_capture_real_attached_sqlite(self):
        d,a,p=fixture()
        with tempfile.TemporaryDirectory() as folder:
            rd=Path(folder)/"receipt.sqlite";hd=Path(folder)/"high.sqlite"
            con=sqlite3.connect(rd)
            con.executescript("""
            CREATE TABLE signer(source_id TEXT,controller TEXT,key_pem TEXT,version INTEGER);
            CREATE TABLE challenge(challenge_nonce TEXT,challenge_sha TEXT,registry_sha TEXT);
            CREATE TABLE receipt(session_nonce TEXT,session_id TEXT,challenge_nonce TEXT,source_id TEXT,payload_sha TEXT,signature_b64 TEXT);
            CREATE TABLE rotation(id INTEGER,source_id TEXT,old_key_sha TEXT,new_key_sha TEXT,previous_registry_sha TEXT,next_registry_sha TEXT);
            """)
            for r in d["registry"]:con.execute("INSERT INTO signer VALUES (?,?,?,?)",tuple(r.values()))
            for r in d["challenges"]:con.execute("INSERT INTO challenge VALUES (?,?,?)",tuple(r.values()))
            for r in d["receipts"]:con.execute("INSERT INTO receipt VALUES (?,?,?,?,?,?)",tuple(r.values()))
            con.commit();con.close()
            con=sqlite3.connect(hd)
            con.execute("CREATE TABLE checkpoint(seq INTEGER,previous_sha TEXT,head_sha TEXT,registry_sha TEXT,challenges INTEGER,receipts INTEGER,rotations INTEGER,run_id INTEGER)")
            for r in d["highwater"]:con.execute("INSERT INTO checkpoint VALUES (?,?,?,?,?,?,?,?)",tuple(r.values()))
            con.commit();con.close()
            captured=capture(rd,hd)
            self.assertEqual(captured,d)
    def test_same_path_rejected(self):
        with self.assertRaisesRegex(ValueError,"IDENTICAL_DATABASE_PATHS"):
            capture("/tmp/same.db","/tmp/same.db")
    def test_no_act(self):
        d,a,p=fixture();self.assertFalse(reconcile(d,a,p)["physical_act_allowed"])
if __name__=="__main__":unittest.main()
