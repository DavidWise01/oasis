import base64
import copy
import unittest
from acquisition import acquire, validate_url, public_ip, review, LIMIT

class Response:
    status=200
    def __init__(self,raw=b"raw evidence"):
        self.raw=raw
    def getheader(self,name,default=None):
        return {"Content-Length":str(len(self.raw))}.get(name,default)
    def read(self,n):
        return self.raw[:n]
class Connection:
    def __init__(self,host,ip,timeout=3):
        self.host=host
        self.ip=ip
        self.response=Response()
    def request(self,method,path,headers):
        self.method=method;self.path=path;self.headers=headers
    def getresponse(self):
        return self.response
    def close(self):
        pass
def fetch(resolver=None,factory=Connection):
    return acquire("https://example.org/evidence",["example.org"],
                   resolver=resolver or (lambda h:["93.184.215.14"]),factory=factory)
class Tests(unittest.TestCase):
    def test_mocked_public_acquisition(self):
        doc=fetch()
        self.assertEqual(doc["raw_length"],len(b"raw evidence"))
        self.assertIn("EXTERNAL_CUSTODY_NOT_AUTHENTICATED",review(doc)["reasons"])
    def test_https_only(self):
        with self.assertRaises(ValueError):
            validate_url("http://example.org",["example.org"])
    def test_host_allowlist(self):
        with self.assertRaises(ValueError):
            validate_url("https://other.org",["example.org"])
    def test_embedded_credentials(self):
        with self.assertRaises(ValueError):
            validate_url("https://user:pass@example.org/",["example.org"])
    def test_fragment(self):
        with self.assertRaises(ValueError):
            validate_url("https://example.org/#fragment",["example.org"])
    def test_nonstandard_port(self):
        with self.assertRaises(ValueError):
            validate_url("https://example.org:444/",["example.org"])
    def test_ip_literal(self):
        with self.assertRaises(ValueError):
            validate_url("https://127.0.0.1",["127.0.0.1"])
    def test_private_ip_dns(self):
        with self.assertRaises(ValueError):
            fetch(resolver=lambda h:["10.0.0.5"])
    def test_mixed_public_private(self):
        with self.assertRaises(ValueError):
            fetch(resolver=lambda h:["93.184.215.14","127.0.0.1"])
    def test_link_local_metadata(self):
        self.assertFalse(public_ip("169.254.169.254"))
    def test_loopback(self):
        self.assertFalse(public_ip("127.0.0.1"))
    def test_public_address(self):
        self.assertTrue(public_ip("8.8.8.8"))
    def test_redirect_rejected(self):
        class Redirect(Connection):
            def getresponse(self):
                r=Response();r.status=302;return r
        with self.assertRaises(ValueError):
            fetch(factory=Redirect)
    def test_oversize_body(self):
        class Oversize(Connection):
            def getresponse(self):
                return Response(b"x"*(LIMIT+1))
        with self.assertRaises(ValueError):
            fetch(factory=Oversize)
    def test_body_mutation(self):
        d=fetch();d["raw_b64"]=base64.b64encode(b"forged").decode()
        self.assertIn("RAW_DIGEST_INVALID",review(d)["reasons"])
    def test_digest_mutation(self):
        d=fetch();d["observation_sha256"]="0"*64
        self.assertIn("OBSERVATION_DIGEST_MISMATCH",review(d)["reasons"])
    def test_bogus_peer(self):
        d=fetch();d["pinned_ip"]="10.0.0.1"
        self.assertIn("NETWORK_PEER_INVALID",review(d)["reasons"])
    def test_no_authority(self):
        self.assertFalse(review(fetch())["physical_act_allowed"])
    def test_bad_observation(self):
        self.assertIn("OBSERVATION_INVALID",review(None)["reasons"])
if __name__=="__main__":
    unittest.main()
