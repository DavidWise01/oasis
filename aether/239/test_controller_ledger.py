import copy
import pathlib
import sys
import unittest
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parent))
from controller_ledger import check,digest

def fixture():
    graph={"key1":["root1"],"root1":[],"key2":["root2"],"root2":[],
           "key3":["root3"],"root3":[]}
    event={"sequence":0,"nonce":"n-0","challenge_id":"challenge-1",
           "run_id":123,"previous_sha256":"0"*64}
    event["entry_sha256"]=digest(event)
    return {"controller_graph":graph,
            "witnesses":[{"key_id":"key"+str(i),"root_id":"root"+str(i),
                          "receipt_digest":"a"*64} for i in range(1,4)],
            "ledger":[event],"externally_pinned_head":event["entry_sha256"]}

class Tests(unittest.TestCase):
    def expect(self,change,reason):
        x=fixture()
        change(x)
        result=check(x)
        self.assertIn(reason,result["reasons"],result)
        self.assertEqual(result["operational_authority"],"HOLD")
    def test_clean_structure_still_hold(self):
        self.expect(lambda x:None,"EXTERNAL_CONTROLLER_AND_LEDGER_CUSTODY_UNAUTHENTICATED")
    def test_shared_controller(self):
        self.expect(lambda x:x["controller_graph"]["key2"].append("root1"),
                    "WITNESS_SHARED_CONTROLLER_ANCESTRY")
    def test_cycle(self):
        self.expect(lambda x:x["controller_graph"]["root1"].append("key1"),"ANCESTRY_CYCLE")
    def test_fake_declared_root(self):
        self.expect(lambda x:x["witnesses"][0].update(root_id="root2"),
                    "DECLARED_ROOT_NOT_IN_ANCESTRY")
    def test_missing_graph_node(self):
        self.expect(lambda x:x["controller_graph"].pop("root1"),"ANCESTRY_NODE_MISSING")
    def test_duplicate_key(self):
        self.expect(lambda x:x["witnesses"][1].update(key_id="key1"),"DUPLICATE_WITNESS_KEY")
    def test_missing_witness(self):
        self.expect(lambda x:x["witnesses"].pop(),"EXACT_THREE_WITNESSES_REQUIRED")
    def test_tamper_event(self):
        self.expect(lambda x:x["ledger"][0].update(challenge_id="changed"),"LEDGER_ENTRY_DIGEST_MISMATCH")
    def test_wrong_external_head(self):
        self.expect(lambda x:x.update(externally_pinned_head="b"*64),"EXTERNAL_HEAD_MISMATCH")
    def test_nonce_replay(self):
        def change(x):
            old=x["ledger"][-1]
            new={"sequence":1,"nonce":old["nonce"],"challenge_id":"second",
                 "run_id":124,"previous_sha256":old["entry_sha256"]}
            new["entry_sha256"]=digest(new)
            x["ledger"].append(new)
            x["externally_pinned_head"]=new["entry_sha256"]
        self.expect(change,"LEDGER_NONCE_REPLAY")
    def test_sequence_gap(self):
        self.expect(lambda x:x["ledger"][0].update(sequence=3),"LEDGER_SEQUENCE_GAP")
    def test_previous_hash(self):
        self.expect(lambda x:x["ledger"][0].update(previous_sha256="f"*64),"LEDGER_PREVIOUS_HASH_MISMATCH")
    def test_empty_ledger(self):
        self.expect(lambda x:x.update(ledger=[]),"LEDGER_EMPTY")
    def test_no_document(self):
        self.assertIn("DOCUMENT_INVALID",check(None)["reasons"])
    def test_bad_run_type(self):
        self.expect(lambda x:x["ledger"][0].update(run_id=True),"LEDGER_RUN_INVALID")

if __name__=="__main__":unittest.main()
