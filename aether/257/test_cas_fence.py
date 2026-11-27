import unittest
from cas_fence import assess,sha

def transition(ident,host,challenge,nonce,expected_seq,expected_head,decision,new_seq,new_head):
    t={"attempt_id":ident,"host_id":host,"challenge_id":challenge,"nonce":nonce,
       "expected_sequence":expected_seq,"expected_head_sha256":expected_head,
       "decision":decision,"new_sequence":new_seq,"new_head_sha256":new_head}
    t["decision_record_sha256"]=sha(t)
    return t

def fixture():
    anchor={"sequence":10,"head_sha256":"a"*64}
    a=transition("attemptA","hostA","c1","nonce1",10,"a"*64,"ACCEPTED",11,"b"*64)
    b=transition("attemptB","hostB","c2","nonce2",10,"a"*64,"STALE_REJECTED",11,"b"*64)
    transitions=[a,b]
    journal=sha({"anchor":anchor,"transitions":transitions})
    witnesses=[{"controller_claim":"controller"+str(i),"journal_sha256":journal,
                "observed_head_sha256":"b"*64} for i in range(3)]
    return {"externally_claimed_anchor":anchor,"transitions":transitions,"witnesses":witnesses}

class Tests(unittest.TestCase):
    def expect(self,modify,reason):
        item=fixture()
        modify(item)
        answer=assess(item)
        self.assertIn(reason,answer["reasons"],answer)
        self.assertEqual(answer["operational_authority"],"HOLD")
    def test_valid_claims_not_authority(self):
        self.expect(lambda b:None,"NO_EXTERNAL_COMPARE_AND_SWAP_ATOMICITY_PROOF")
    def test_split_brain_accepted_stale(self):
        def change(b):
            t=b["transitions"][1];t["decision"]="ACCEPTED";t["new_sequence"]=11;t["new_head_sha256"]="c"*64
            t["decision_record_sha256"]=sha({k:v for k,v in t.items() if k!="decision_record_sha256"})
        self.expect(change,"ACCEPTED_STALE_HEAD_OR_SPLIT_BRAIN")
    def test_double_challenge(self):
        def change(b):
            t=b["transitions"][1];t.update(decision="ACCEPTED",expected_sequence=11,
                expected_head_sha256="b"*64,new_sequence=12,new_head_sha256="c"*64,
                challenge_id="c1")
            t["decision_record_sha256"]=sha({k:v for k,v in t.items() if k!="decision_record_sha256"})
        self.expect(change,"DOUBLE_CONSUMED_CHALLENGE")
    def test_double_nonce(self):
        def change(b):
            t=b["transitions"][1];t.update(decision="ACCEPTED",expected_sequence=11,
                expected_head_sha256="b"*64,new_sequence=12,new_head_sha256="c"*64,
                nonce="nonce1")
            t["decision_record_sha256"]=sha({k:v for k,v in t.items() if k!="decision_record_sha256"})
        self.expect(change,"DOUBLE_CONSUMED_NONCE")
    def test_unjustified_rejection(self):
        self.expect(lambda b:b["transitions"][1].update(expected_sequence=11,
            expected_head_sha256="b"*64),"UNJUSTIFIED_STALE_REJECTION")
    def test_rejection_changes_head(self):
        self.expect(lambda b:b["transitions"][1].update(new_head_sha256="d"*64),
            "REJECTED_ATTEMPT_MUTATED_HEAD")
    def test_accept_without_increment(self):
        self.expect(lambda b:b["transitions"][0].update(new_sequence=10),
            "ACCEPTED_SEQUENCE_NOT_MONOTONIC")
    def test_accept_without_head_change(self):
        self.expect(lambda b:b["transitions"][0].update(new_head_sha256="a"*64),
            "ACCEPTED_HEAD_NOT_ADVANCED")
    def test_decision_tamper(self):
        self.expect(lambda b:b["transitions"][0].update(host_id="intruder"),
            "DECISION_RECORD_TAMPERED")
    def test_duplicate_attempt(self):
        self.expect(lambda b:b["transitions"][1].update(attempt_id="attemptA"),
            "DUPLICATE_ATTEMPT_ID")
    def test_boolean_sequence(self):
        self.expect(lambda b:b["transitions"][0].update(expected_sequence=True),
            "SEQUENCE_TYPE_INVALID")
    def test_bad_head(self):
        self.expect(lambda b:b["transitions"][0].update(new_head_sha256="bad"),
            "TRANSITION_HEAD_INVALID")
    def test_witness_shared_controller(self):
        self.expect(lambda b:b["witnesses"][1].update(controller_claim="controller0"),
            "WITNESS_CONTROLLER_DUPLICATE_OR_INVALID")
    def test_witness_forked_journal(self):
        self.expect(lambda b:b["witnesses"][0].update(journal_sha256="f"*64),
            "WITNESS_JOURNAL_MISMATCH")
    def test_witness_wrong_head(self):
        self.expect(lambda b:b["witnesses"][0].update(observed_head_sha256="d"*64),
            "WITNESS_FINAL_HEAD_MISMATCH")
    def test_missing_witness(self):
        self.expect(lambda b:b["witnesses"].pop(),"THREE_WITNESSES_REQUIRED")
    def test_missing_transitions(self):
        self.expect(lambda b:b.update(transitions=[]),"TRANSITIONS_INVALID")
    def test_bad_anchor(self):
        self.expect(lambda b:b["externally_claimed_anchor"].update(head_sha256="bad"),
            "ANCHOR_INVALID")
    def test_invalid_bundle(self):
        self.assertIn("BUNDLE_INVALID",assess(None)["reasons"])
    def test_no_physical_act(self):
        self.assertFalse(assess(fixture())["physical_act_allowed"])
if __name__=="__main__":
    unittest.main()
