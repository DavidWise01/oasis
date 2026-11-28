import copy,sqlite3,tempfile,unittest
from pathlib import Path
from acquisition_replay import replay,read_local,sha,SCHEMA,ANCHOR_SCHEMA,ZERO

def fixture():
    batches=[];nonces=[];manifests=[];previous=ZERO
    for idx in range(1,3):
        records=[]
        for i in range(3):
            kid=f"k{i}";raw=f"{idx}{i}".encode().hex().ljust(64,"a")
            obs=f"{idx}{i}".encode().hex().ljust(64,"b")
            records.append({"key_id":kid,"raw_sha256":raw,
                            "observation_sha256":obs,
                            "requested_url":f"https://w{i}.example.org/batch/{idx}"})
            nonces.append({"nonce":f"witness-{idx}-{i}","batch_id":idx,
                           "key_id":kid,"raw_sha":raw,"observation_sha":obs})
        challenge=f"challenge-{idx}"
        trust="c"*64
        statement={"schema":SCHEMA,"trust_sha256":trust,"challenge_nonce":challenge,
                   "previous_head_sha256":previous,"witnesses":records}
        head=sha(statement)
        batches.append({"id":idx,"trust_sha":trust,"challenge_nonce":challenge,
                        "previous_head":previous,"head_sha":head})
        manifests.append({"batch_id":idx,"trust_sha256":trust,"challenge_nonce":challenge,
                          "previous_head_sha256":previous,"witnesses":records})
        previous=head
    anchor={"schema":ANCHOR_SCHEMA,"minimum_batch_id":2,"head_sha256":previous,
            "minimum_nonce_count":6,"custodian_claim":"claimed-remote-archive"}
    return {"batches":batches,"nonces":nonces},manifests,anchor,sha(anchor)

class Tests(unittest.TestCase):
    def assert_problem(self,mutate,problem):
        local,manifests,anchor,pin=fixture()
        mutate(local,manifests,anchor)
        result=replay(local,manifests,anchor,pin)
        self.assertIn(problem,result["reasons"],result)
        self.assertEqual(result["operational_authority"],"HOLD")
    def test_matching_chain_still_hold(self):
        local,manifests,anchor,pin=fixture()
        report=replay(local,manifests,anchor,pin)
        self.assertTrue(report["observed"]["all_batch_digests_recomputed"])
        self.assertIn("PRESERVED_MANIFEST_CUSTODY_NOT_AUTHENTICATED",report["reasons"])
    def test_removed_batch(self):
        self.assert_problem(lambda l,m,a:l["batches"].pop(),"ANCHORED_BATCH_REMOVED")
    def test_removed_nonce(self):
        self.assert_problem(lambda l,m,a:l["nonces"].pop(),"ANCHORED_NONCE_HIGHWATER_ROLLBACK")
    def test_reordered_batch(self):
        self.assert_problem(lambda l,m,a:l["batches"].reverse(),"BATCH_SEQUENCE_GAP")
    def test_changed_parent(self):
        self.assert_problem(lambda l,m,a:l["batches"][1].update(previous_head="f"*64),"BATCH_PARENT_MISMATCH")
    def test_replaced_head(self):
        self.assert_problem(lambda l,m,a:l["batches"][1].update(head_sha="f"*64),"BATCH_HEAD_RECOMPUTATION_FAILED")
    def test_substituted_raw_receipt(self):
        self.assert_problem(lambda l,m,a:l["nonces"][0].update(raw_sha="f"*64),"MANIFEST_STORED_NONCE_DIVERGENCE")
    def test_changed_observation(self):
        self.assert_problem(lambda l,m,a:l["nonces"][0].update(observation_sha="f"*64),"MANIFEST_STORED_NONCE_DIVERGENCE")
    def test_manifest_endpoint_substitution(self):
        self.assert_problem(lambda l,m,a:m[0]["witnesses"][0].update(requested_url="https://replacement.example.org/"),"BATCH_HEAD_RECOMPUTATION_FAILED")
    def test_manifest_removed(self):
        self.assert_problem(lambda l,m,a:m.pop(),"MANIFEST_COUNT_MISMATCH")
    def test_manifest_reordered(self):
        self.assert_problem(lambda l,m,a:m.reverse(),"MANIFEST_HEADER_SUBSTITUTION")
    def test_duplicate_nonce(self):
        self.assert_problem(lambda l,m,a:l["nonces"][1].update(nonce="witness-1-0"),"NONCE_REPLAY_OR_INVALID")
    def test_duplicate_key_per_batch(self):
        self.assert_problem(lambda l,m,a:l["nonces"][1].update(key_id="k0"),"BATCH_WITNESS_NONCE_TRIPLE_INVALID")
    def test_wrong_anchor_pin(self):
        local,manifests,anchor,pin=fixture()
        self.assertIn("ANCHOR_DIGEST_CONFLICT",replay(local,manifests,anchor,"f"*64)["reasons"])
    def test_missing_anchor_pin(self):
        local,manifests,anchor,pin=fixture()
        self.assertIn("OUT_OF_BAND_ANCHOR_DIGEST_REQUIRED",replay(local,manifests,anchor,None)["reasons"])
    def test_missing_prefix(self):
        self.assert_problem(lambda l,m,a:a.update(minimum_batch_id=3),"ANCHORED_BATCH_REMOVED")
    def test_historical_head_changed(self):
        self.assert_problem(lambda l,m,a:a.update(head_sha256="f"*64),"ANCHORED_HISTORICAL_BATCH_REWRITTEN")
    def test_read_only_sqlite(self):
        local,manifests,anchor,pin=fixture()
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/"db.sqlite"
            con=sqlite3.connect(path)
            con.execute("CREATE TABLE batch(id INTEGER,trust_sha TEXT,challenge_nonce TEXT,previous_head TEXT,head_sha TEXT)")
            con.execute("CREATE TABLE witness_nonce(nonce TEXT,batch_id INTEGER,key_id TEXT,raw_sha TEXT,observation_sha TEXT)")
            for r in local["batches"]:
                con.execute("INSERT INTO batch VALUES (?,?,?,?,?)",tuple(r.values()))
            for r in local["nonces"]:
                con.execute("INSERT INTO witness_nonce VALUES (?,?,?,?,?)",tuple(r.values()))
            con.commit();con.close()
            self.assertEqual(read_local(path),local)
    def test_physical_act_stays_hold(self):
        local,manifests,anchor,pin=fixture()
        self.assertFalse(replay(local,manifests,anchor,pin)["physical_act_allowed"])
if __name__=="__main__":unittest.main()
