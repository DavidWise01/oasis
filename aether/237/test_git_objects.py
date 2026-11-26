import base64
import hashlib
import json
import pathlib
import sys
import unittest
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parent))
from git_objects import object_id,tree_bytes,verify

COMMIT="a"*40
DATA=b'{"status":"HOLD"}\\n'
DIGEST=hashlib.sha256(DATA).hexdigest()

def fixture():
    blobid=object_id("blob",DATA)
    leaf=[{"path":"pinned-members.json","mode":"100644","type":"blob","sha":blobid}]
    leafid=object_id("tree",tree_bytes(leaf))
    root=[{"path":"evidence","mode":"040000","type":"tree","sha":leafid}]
    rootid=object_id("tree",tree_bytes(root))
    payload={
      ("commits",COMMIT):{"sha":COMMIT,"tree":{"sha":rootid}},
      ("trees",rootid):{"sha":rootid,"tree":root,"truncated":False},
      ("trees",leafid):{"sha":leafid,"tree":leaf,"truncated":False},
      ("blobs",blobid):{"sha":blobid,"size":len(DATA),"encoding":"base64","content":base64.b64encode(DATA).decode()}
    }
    def fetch(kind,oid):
        return json.dumps(payload[(kind,oid)],sort_keys=True).encode()
    return payload,fetch

class GitObjectTests(unittest.TestCase):
    def check(self,mutate,expected):
        data,_=fixture()
        mutate(data)
        def fetch(kind,oid):return json.dumps(data[(kind,oid)],sort_keys=True).encode()
        result=verify(COMMIT,"evidence/pinned-members.json",DIGEST,fetch)
        self.assertEqual(result["verdict"],"REJECT_OR_UNVERIFIED")
        self.assertTrue(any(expected in x for x in result["reasons"]),result["reasons"])
        self.assertEqual(result["operational_authority"],"HOLD")
    def test_valid_object_chain_unqualified(self):
        _,fetch=fixture()
        r=verify(COMMIT,"evidence/pinned-members.json",DIGEST,fetch)
        self.assertEqual(r["verdict"],"OBJECT_IDENTITIES_MATCH_UNQUALIFIED")
        self.assertFalse(r["independent_custody_authenticated"])
    def test_mutated_blob(self):
        def mutate(d):
            key=next(k for k in d if k[0]=="blobs")
            d[key]["content"]=base64.b64encode(b"tampered").decode()
            d[key]["size"]=8
        self.check(mutate,"BLOB_OBJECT_ID_MISMATCH")
    def test_mutated_tree_entry(self):
        def mutate(d):
            key=next(k for k in d if k[0]=="trees" and d[k]["tree"][0]["type"]=="blob")
            d[key]["tree"][0]["mode"]="100755"
        self.check(mutate,"TREE_OBJECT_ID_MISMATCH")
    def test_truncated_tree(self):
        def mutate(d):
            key=next(k for k in d if k[0]=="trees")
            d[key]["truncated"]=True
        self.check(mutate,"TREE_TRUNCATED")
    def test_commit_tree_absent(self):
        self.check(lambda d:d[("commits",COMMIT)].pop("tree"),"COMMIT_TREE_MISSING")
    def test_duplicate_tree_entry(self):
        def mutate(d):
            key=next(k for k in d if k[0]=="trees")
            d[key]["tree"].append(dict(d[key]["tree"][0]))
        self.check(mutate,"TREE_DUPLICATE_ENTRY")
    def test_commit_sha_wrong(self):
        self.check(lambda d:d[("commits",COMMIT)].update(sha="b"*40),"RESPONSE_SHA_MISMATCH")
    def test_manifest_hash_wrong(self):
        _,fetch=fixture()
        r=verify(COMMIT,"evidence/pinned-members.json","0"*64,fetch)
        self.assertIn("PINNED_CONTENT_DIGEST_MISMATCH"," ".join(r["reasons"]))
    def test_path_traversal(self):
        _,fetch=fixture()
        r=verify(COMMIT,"../secret",DIGEST,fetch)
        self.assertIn("PATH_INVALID",r["reasons"])
    def test_invalid_hex(self):
        _,fetch=fixture()
        self.assertIn("PIN_COMMIT_INVALID",verify("no","evidence/pinned-members.json",DIGEST,fetch)["reasons"])
    def test_missing_member(self):
        _,fetch=fixture()
        r=verify(COMMIT,"evidence/missing.json",DIGEST,fetch)
        self.assertTrue(any("PATH_COMPONENT_NOT_UNIQUE_OR_ABSENT" in x for x in r["reasons"]))
    def test_unsupported_gitlink(self):
        with self.assertRaises(ValueError):
            tree_bytes([{"path":"submodule","mode":"160000","type":"commit","sha":"a"*40}])
    def test_sorting(self):
        a=[{"path":"z","mode":"100644","type":"blob","sha":"1"*40},
           {"path":"a","mode":"100644","type":"blob","sha":"2"*40}]
        self.assertEqual(tree_bytes(a),tree_bytes(list(reversed(a))))
    def test_git_blob_fixture_sha(self):
        self.assertEqual(object_id("blob",bytes([116,101,115,116,10])),"9daeafb9864cf43055ae93beb0afd6c7d144bfa4")
if __name__=="__main__":unittest.main()
