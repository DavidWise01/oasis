import copy
import unittest
from replay_ancestry import assess, digest

def fixture():
    anchor = {"sequence": 0, "head_sha256": "0"*64}
    def make_events():
        previous = anchor["head_sha256"]
        events = []
        for n in range(2):
            e = {"sequence": n+1, "previous_sha256": previous, "run_id": 7,
                 "challenge_id": "fresh", "nonce": "nonce-" + str(n),
                 "transcript_sha256": "b"*64}
            e["event_sha256"] = digest(e)
            events.append(e)
            previous = e["event_sha256"]
        return events
    first = make_events()
    return {"externally_claimed_anchor": anchor,
            "candidate_histories": [
                {"source_id": "A", "events": first,
                 "claimed_head_sha256": first[-1]["event_sha256"]},
                {"source_id": "B", "events": copy.deepcopy(first),
                 "claimed_head_sha256": first[-1]["event_sha256"]}],
            "controller_graph": {"k1": ["root1"], "root1": [],
                                 "k2": ["root2"], "root2": [],
                                 "k3": ["root3"], "root3": []},
            "signers": [{"key_id": "key"+str(i), "controller_id": "k"+str(i)}
                        for i in range(1,4)],
            "consumed_nonces": []}

class Tests(unittest.TestCase):
    def expect(self, change, reason):
        document = fixture()
        change(document)
        answer = assess(document)
        self.assertIn(reason, answer["reasons"], answer)
        self.assertEqual(answer["operational_authority"], "HOLD")
    def test_consistent_unqualified(self):
        self.expect(lambda d: None, "EXTERNAL_ANCHOR_NOT_AUTHENTICATED")
    def test_shared_parent(self):
        self.expect(lambda d: d["controller_graph"]["k2"].append("root1"),
                    "SHARED_CONTROLLER_ANCESTRY")
    def test_ancestry_cycle(self):
        self.expect(lambda d: d["controller_graph"]["root1"].append("k1"),
                    "CONTROLLER_ANCESTRY_CYCLE")
    def test_missing_controller(self):
        self.expect(lambda d: d["controller_graph"].pop("root2"),
                    "MISSING_ANCESTRY_NODE")
    def test_history_fork(self):
        def mutate(d):
            branch = d["candidate_histories"][1]["events"]
            branch[0]["nonce"] = "fork"
            branch[0]["event_sha256"] = digest({k:v for k,v in branch[0].items()
                                                  if k != "event_sha256"})
            branch[1]["previous_sha256"] = branch[0]["event_sha256"]
            branch[1]["event_sha256"] = digest({k:v for k,v in branch[1].items()
                                                  if k != "event_sha256"})
            d["candidate_histories"][1]["claimed_head_sha256"] = branch[-1]["event_sha256"]
        self.expect(mutate, "DIVERGENT_HISTORY")
    def test_nonce_seen_externally(self):
        self.expect(lambda d: d["consumed_nonces"].append("nonce-0"),
                    "ALREADY_CONSUMED_NONCE")
    def test_nonce_reused_within_chain(self):
        self.expect(lambda d: d["candidate_histories"][0]["events"][1].update(nonce="nonce-0"),
                    "NONCE_REPLAY")
    def test_broken_prev(self):
        self.expect(lambda d: d["candidate_histories"][0]["events"][1].update(previous_sha256="e"*64),
                    "PREVIOUS_HEAD_MISMATCH")
    def test_sequence_skip(self):
        self.expect(lambda d: d["candidate_histories"][0]["events"][1].update(sequence=4),
                    "NONMONOTONIC_SEQUENCE")
    def test_event_hash_tamper(self):
        self.expect(lambda d: d["candidate_histories"][0]["events"][0].update(run_id=13),
                    "EVENT_DIGEST_MISMATCH")
    def test_wrong_final_head(self):
        self.expect(lambda d: d["candidate_histories"][0].update(claimed_head_sha256="a"*64),
                    "CANDIDATE_HEAD_MISMATCH")
    def test_bad_transcript_hash(self):
        self.expect(lambda d: d["candidate_histories"][0]["events"][0].update(transcript_sha256="bad"),
                    "TRANSCRIPT_INVALID")
    def test_reused_signer_key(self):
        self.expect(lambda d: d["signers"][1].update(key_id="key1"),
                    "SIGNER_KEY_REUSE")
    def test_signer_missing(self):
        self.expect(lambda d: d["signers"].pop(), "THREE_SIGNERS_REQUIRED")
    def test_invalid_anchor(self):
        self.expect(lambda d: d["externally_claimed_anchor"].update(head_sha256="bad"),
                    "ANCHOR_INVALID")
    def test_missing_candidates(self):
        self.expect(lambda d: d["candidate_histories"].clear(),
                    "CANDIDATE_HISTORIES_INVALID")
    def test_boolean_sequence(self):
        self.expect(lambda d: d["candidate_histories"][0]["events"][0].update(sequence=True),
                    "NONMONOTONIC_SEQUENCE")
    def test_none(self):
        self.assertIn("BUNDLE_INVALID", assess(None)["reasons"])
    def test_noncertifying_immutable_gate(self):
        answer = assess(fixture())
        self.assertFalse(answer["physical_act_allowed"])
        self.assertFalse(answer["independent_controller_custody_authenticated"])

if __name__ == "__main__":
    unittest.main()
