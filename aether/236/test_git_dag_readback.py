import json
import pathlib
import sys
import unittest
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parent))
from git_dag_readback import walk

A="a"*40
B="b"*40
C="c"*40
D="d"*40
E="e"*40

def make(graph):
    def fetch(sha):
        if sha not in graph:raise OSError("404")
        return json.dumps({"sha":sha,"parents":[{"sha":p} for p in graph[sha]]}).encode()
    return fetch

class DagTests(unittest.TestCase):
    def test_strict_parent(self):
        r=walk(A,B,make({B:[A]}))
        self.assertEqual(r["dag_result"],"STRICT_ANCESTOR_OBSERVED_UNQUALIFIED")
        self.assertEqual(r["operational_authority"],"HOLD")
    def test_grandparent(self):
        self.assertEqual(walk(A,C,make({C:[B],B:[A]}))["dag_result"],"STRICT_ANCESTOR_OBSERVED_UNQUALIFIED")
    def test_merge_second_parent(self):
        self.assertEqual(walk(A,D,make({D:[B,C],B:[],C:[A]}))["dag_result"],"STRICT_ANCESTOR_OBSERVED_UNQUALIFIED")
    def test_unrelated(self):
        r=walk(A,B,make({B:[C],C:[]}))
        self.assertIn("STRICT_ANCESTRY_NOT_ESTABLISHED",r["reasons"])
    def test_equal_is_not_strict(self):
        self.assertIn("PIN_NOT_STRICT_ANCESTOR",walk(A,A,make({}))["reasons"])
    def test_missing_commit(self):
        self.assertTrue(any("COMMIT_READ_FAILED" in x for x in walk(A,B,make({}))["reasons"]))
    def test_forged_requested_sha(self):
        r=walk(A,B,lambda sha:json.dumps({"sha":C,"parents":[{"sha":A}]}).encode())
        self.assertIn("COMMIT_READ_FAILED:ValueError",r["reasons"])
    def test_parent_malformed(self):
        r=walk(A,B,lambda sha:json.dumps({"sha":sha,"parents":[{"sha":"oops"}]}).encode())
        self.assertIn("COMMIT_READ_FAILED:ValueError",r["reasons"])
    def test_duplicate_parents(self):
        r=walk(A,B,make({B:[C,C]}))
        self.assertIn("COMMIT_READ_FAILED:ValueError",r["reasons"])
    def test_self_parent(self):
        r=walk(A,B,make({B:[B]}))
        self.assertIn("COMMIT_READ_FAILED:ValueError",r["reasons"])
    def test_invalid_input(self):
        self.assertIn("PIN_SHA_INVALID",walk("wrong",B,make({}))["reasons"])
    def test_bad_json(self):
        r=walk(A,B,lambda sha:b"{")
        self.assertIn("COMMIT_READ_FAILED:JSONDecodeError",r["reasons"])
    def test_oversized(self):
        r=walk(A,B,lambda sha:b"x"*(1024*1024+1))
        self.assertIn("COMMIT_READ_FAILED:ValueError",r["reasons"])
    def test_depth_bound(self):
        graph={}
        chain=[format(i,"040x") for i in range(1,132)]
        for i,s in enumerate(chain[:-1]):graph[s]=[chain[i+1]]
        graph[chain[-1]]=[A]
        r=walk(A,chain[0],make(graph))
        self.assertIn("DEPTH_BOUND_EXCEEDED",r["reasons"])
    def test_no_credential_required_for_mock(self):
        r=walk(A,B,make({B:[A]}))
        self.assertFalse(r["independent_custody_authenticated"])
if __name__=="__main__":unittest.main()
