import unittest
from checkpoints import assess,digest
def entry(n,prev,nonce=None):
    e={"sequence":n,"previous_sha256":prev,"nonce":nonce or "n"+str(n),"challenge_id":"c1","run_id":71}
    e["entry_sha256"]=digest(e);return e
def chain(n):
    xs=[];last="0"*64
    for i in range(n):
        e=entry(i,last);xs.append(e);last=e["entry_sha256"]
    return xs
def fixture():
    ws=[]
    for i,n in enumerate((2,3,3)):
        xs=chain(n)
        ws.append({"root":"r"+str(i),"checkpoint_id":"id"+str(i),"length":n,
         "head_sha256":xs[-1]["entry_sha256"],"entries":xs,"source_commit":"a"*40,
         "challenge_id":"c1","run_id":71})
    return {"source_commit":"a"*40,"challenge_id":"c1","run_id":71,"witnesses":ws}
class Tests(unittest.TestCase):
    def expect(self,change,reason):
        b=fixture();change(b);r=assess(b)
        self.assertIn(reason,r["reasons"],r)
        self.assertEqual(r["operational_authority"],"HOLD")
    def test_consistent_unqualified(self):
        self.expect(lambda b:None,"EXTERNAL_WITNESS_CUSTODY_AND_SIGNATURES_UNAUTHENTICATED")
        self.assertTrue(assess(fixture())["observed"]["consistent_prefixes"])
    def test_divergent_valid_hashes(self):
        def change(b):
            a=entry(0,"0"*64,"evil");bb=entry(1,a["entry_sha256"]);cc=entry(2,bb["entry_sha256"])
            b["witnesses"][2]["entries"]=[a,bb,cc];b["witnesses"][2]["head_sha256"]=cc["entry_sha256"]
        self.expect(change,"DIVERGENT_LEDGER_HISTORY")
    def test_wrong_head(self):self.expect(lambda b:b["witnesses"][0].update(head_sha256="f"*64),"CHECKPOINT_HEAD_MISMATCH")
    def test_duplicate_root(self):self.expect(lambda b:b["witnesses"][1].update(root="r0"),"DUPLICATE_ROOT")
    def test_duplicate_checkpoint(self):self.expect(lambda b:b["witnesses"][2].update(checkpoint_id="id1"),"CHECKPOINT_REPLAY")
    def test_source(self):self.expect(lambda b:b["witnesses"][2].update(source_commit="b"*40),"CROSS_WITNESS_BINDING_MISMATCH")
    def test_challenge(self):self.expect(lambda b:b["witnesses"][2].update(challenge_id="evil"),"CROSS_WITNESS_BINDING_MISMATCH")
    def test_run(self):self.expect(lambda b:b["witnesses"][2].update(run_id=72),"CROSS_WITNESS_BINDING_MISMATCH")
    def test_digest(self):self.expect(lambda b:b["witnesses"][1]["entries"][0].update(entry_sha256="f"*64),"ENTRY_DIGEST_MISMATCH")
    def test_previous(self):self.expect(lambda b:b["witnesses"][1]["entries"][1].update(previous_sha256="f"*64),"PREVIOUS_HASH_MISMATCH")
    def test_nonce(self):self.expect(lambda b:b["witnesses"][1]["entries"][1].update(nonce="n0"),"NONCE_REPLAY")
    def test_sequence(self):self.expect(lambda b:b["witnesses"][1]["entries"][1].update(sequence=9),"SEQUENCE_GAP")
    def test_length(self):self.expect(lambda b:b["witnesses"][1].update(length=4),"CHECKPOINT_LENGTH_MISMATCH")
    def test_event_binding(self):self.expect(lambda b:b["witnesses"][1]["entries"][0].update(run_id=72),"LEDGER_EVENT_BINDING_MISMATCH")
    def test_missing(self):self.expect(lambda b:b["witnesses"].pop(),"WITNESS_SET_INVALID")
    def test_none(self):self.assertIn("BUNDLE_INVALID",assess(None)["reasons"])
    def test_empty(self):self.expect(lambda b:b["witnesses"][1].update(entries=[]),"CHAIN_LENGTH_INVALID")
if __name__=="__main__":unittest.main()
