import io
import json
import pathlib
import sys
import unittest
import zipfile

sys.path.insert(0,str(pathlib.Path(__file__).resolve().parent))
from verify_hosted_zip import verify,digest

def make_zip(entries):
    buf=io.BytesIO()
    with zipfile.ZipFile(buf,"w",zipfile.ZIP_DEFLATED) as z:
        for name,body in entries:z.writestr(name,body)
    return buf.getvalue()

class HostedZipTests(unittest.TestCase):
    def test_matching_bytes_never_certify(self):
        r=verify(make_zip([("evidence.json",b"record")]),{"evidence.json":digest(b"record")})
        self.assertEqual(r["verdict"],"MEMBERS_MATCH_PINNED_MANIFEST_UNQUALIFIED")
        self.assertEqual(r["operational_authority"],"HOLD")
        self.assertFalse(r["physical_act_allowed"])
    def test_wrong_digest(self):
        r=verify(make_zip([("evidence.json",b"wrong")]),{"evidence.json":digest(b"right")})
        self.assertIn("MEMBER_DIGEST_MISMATCH",r["reasons"])
    def test_missing_member(self):
        r=verify(make_zip([("a",b"x")]),{"a":digest(b"x"),"b":digest(b"y")})
        self.assertIn("MEMBER_SET_MISMATCH",r["reasons"])
    def test_extra_member(self):
        r=verify(make_zip([("a",b"x"),("b",b"y")]),{"a":digest(b"x")})
        self.assertIn("MEMBER_SET_MISMATCH",r["reasons"])
    def test_duplicate_member(self):
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore",UserWarning)
            blob=make_zip([("a",b"x"),("a",b"x")])
        self.assertIn("DUPLICATE_MEMBER",verify(blob,{"a":digest(b"x")})["reasons"])
    def test_path_traversal(self):
        r=verify(make_zip([("../secret",b"x")]),{"safe":digest(b"x")})
        self.assertIn("UNSAFE_OR_DIRECTORY_MEMBER",r["reasons"])
    def test_manifest_traversal(self):
        r=verify(make_zip([("a",b"x")]),{"../a":digest(b"x")})
        self.assertIn("PINNED_MANIFEST_INVALID",r["reasons"])
    def test_empty_manifest(self):
        self.assertIn("PINNED_MANIFEST_INVALID",verify(b"junk",{})["reasons"])
    def test_malformed_zip(self):
        self.assertEqual(verify(b"notzip",{"a":digest(b"x")})["verdict"],"REJECT_OR_UNVERIFIED")
    def test_directory_member(self):
        r=verify(make_zip([("folder/",b"")]),{"folder/x":digest(b"x")})
        self.assertIn("UNSAFE_OR_DIRECTORY_MEMBER",r["reasons"])
    def test_invalid_manifest_digest(self):
        self.assertIn("PINNED_MANIFEST_INVALID",verify(b"x",{"a":"pass"})["reasons"])
    def test_oversized_archive(self):
        self.assertIn("ARCHIVE_EMPTY_OR_OVERSIZE",verify(b"x"*(16*1024*1024+1),{"a":digest(b"x")})["reasons"])

if __name__=="__main__":
    unittest.main()
