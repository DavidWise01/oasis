"""AETHER-229 synthetic ancestry screening tests; NOT remote witness authentication."""
import copy
import unittest
from ancestry_gate import assess,OWNED_CORPUS,owned_url

def fixture():
    w=[]
    for i in range(3):
        w.append({
          "root_id":"ROOT-"+str(i),"ultimate_controller":"CTRL-"+str(i),
          "operator":"OP-"+str(i),"administrator":"ADMIN-"+str(i),
          "custody_host":"HOST-"+str(i),"corpus_id":OWNED_CORPUS if i==0 else "EXTERNAL-CLAIM-"+str(i),
          "signing_key_sha256":str(i+1)*64,"artifact_sha256":str(i+4)*64,
          "source_url":["https://github.com/DavidWise01/oasis/blob/main/aether/228/protocol.json",
                        "https://external-example-one.invalid/receipt",
                        "https://external-example-two.invalid/receipt"][i],
          "claimed_independent_external":i>0,
          "signature_verified_out_of_band":False,
          "controller_authenticated_out_of_band":False,
          "operational_authority":"HOLD","physical_act_allowed":False
        })
    return {"schema":"AETHER-229/three-root-ancestry-v1",
            "witnesses":w,"previous_phase_freeze":"../224/decision.json",
            "operational_authority":"HOLD","physical_act_allowed":False}

class AncestryTests(unittest.TestCase):
    def reject(self,code,edit):
        doc=fixture()
        edit(doc)
        result=assess(doc)
        self.assertEqual(result["verdict"],"REJECT",result)
        self.assertIn(code,result["reasons"])
        self.assertEqual(result["independent_witness_roots_authenticated"],0)
        self.assertFalse(result["physical_act_allowed"])
        self.assertEqual(result["operational_authority"],"HOLD")

    def test_three_distinct_claims_never_authenticate_themselves(self):
        r=assess(fixture())
        self.assertEqual(r["verdict"],"DOCUMENTARY_DISTINCT_CONTROL_CLAIMS_ONLY",r)
        self.assertEqual(r["declared_witness_roots"],3)
        self.assertFalse(r["external_control_authenticated"])

    def test_owned_github_url(self):
        self.assertTrue(owned_url("https://github.com/DavidWise01/oasis"))
    def test_owned_pages_url(self):
        self.assertTrue(owned_url("https://davidwise01.github.io/oasis/aether/228/"))
    def test_owned_0root_url(self):
        self.assertTrue(owned_url("https://0root.ai/"))
    def test_external_url_not_owned(self):
        self.assertFalse(owned_url("https://example.invalid/aether"))
    def test_missing_third_witness(self):
        self.reject("EXACTLY_THREE_WITNESS_RECORDS_REQUIRED",lambda x:x["witnesses"].pop())
    def test_extra_fourth_witness(self):
        self.reject("EXACTLY_THREE_WITNESS_RECORDS_REQUIRED",lambda x:x["witnesses"].append(copy.deepcopy(x["witnesses"][0])))
    def test_shared_controller(self):
        self.reject("SHARED_CONTROL_OR_KEY:ultimate_controller:0:1",
                    lambda x:x["witnesses"][1].update(ultimate_controller="CTRL-0"))
    def test_shared_operator(self):
        self.reject("SHARED_CONTROL_OR_KEY:operator:1:2",
                    lambda x:x["witnesses"][2].update(operator="OP-1"))
    def test_shared_administrator(self):
        self.reject("SHARED_CONTROL_OR_KEY:administrator:0:2",
                    lambda x:x["witnesses"][2].update(administrator="ADMIN-0"))
    def test_shared_host(self):
        self.reject("SHARED_CONTROL_OR_KEY:custody_host:0:1",
                    lambda x:x["witnesses"][1].update(custody_host="HOST-0"))
    def test_shared_root(self):
        self.reject("SHARED_CONTROL_OR_KEY:root_id:1:2",
                    lambda x:x["witnesses"][2].update(root_id="ROOT-1"))
    def test_shared_key(self):
        self.reject("SHARED_CONTROL_OR_KEY:signing_key_sha256:0:1",
                    lambda x:x["witnesses"][1].update(signing_key_sha256="1"*64))
    def test_shared_corpus(self):
        self.reject("SHARED_SOURCE_CORPUS:0:2",
                    lambda x:x["witnesses"][2].update(corpus_id=OWNED_CORPUS))
    def test_owned_pages_mirror_of_github(self):
        def edit(x):
            x["witnesses"][1].update(source_url="https://davidwise01.github.io/oasis/aether/229/",
                                     corpus_id=OWNED_CORPUS,claimed_independent_external=False)
        self.reject("SAME_OWNED_MIRROR_ANCESTRY:0:1",edit)
    def test_0root_mirror_of_github(self):
        def edit(x):
            x["witnesses"][2].update(source_url="https://0root.ai/",corpus_id=OWNED_CORPUS,
                                     claimed_independent_external=False)
        self.reject("SAME_OWNED_MIRROR_ANCESTRY:0:2",edit)
    def test_owned_mirror_disguised_external(self):
        self.reject("OWNED_MIRROR_MISCLASSIFIED_EXTERNAL:1",
                    lambda x:x["witnesses"][1].update(source_url="https://0root.ai/aether/229"))
    def test_owned_mirror_corpus_relabel(self):
        self.reject("OWNED_MIRROR_ANCESTRY_MISDECLARED:1",
                    lambda x:x["witnesses"][1].update(source_url="https://davidwise01.github.io/oasis/"))
    def test_invalid_signing_key_pin(self):
        self.reject("WITNESS_KEY_FINGERPRINT_INVALID:1",lambda x:x["witnesses"][1].update(signing_key_sha256="bad"))
    def test_invalid_artifact_pin(self):
        self.reject("WITNESS_ARTIFACT_DIGEST_INVALID:2",lambda x:x["witnesses"][2].update(artifact_sha256="bad"))
    def test_http_not_https(self):
        self.reject("WITNESS_SOURCE_URL_INVALID:2",lambda x:x["witnesses"][2].update(source_url="http://external.invalid"))
    def test_missing_operator(self):
        self.reject("WITNESS_REQUIRED_FIELD_MISSING:1",lambda x:x["witnesses"][1].update(operator=""))
    def test_self_claimed_signature_verified(self):
        self.reject("UNSUPPORTED_EXTERNAL_AUTHENTICATION_CLAIM:2",
                    lambda x:x["witnesses"][2].update(signature_verified_out_of_band=True))
    def test_self_claimed_controller_authenticated(self):
        self.reject("UNSUPPORTED_EXTERNAL_AUTHENTICATION_CLAIM:1",
                    lambda x:x["witnesses"][1].update(controller_authenticated_out_of_band=True))
    def test_witness_promotes_act(self):
        self.reject("WITNESS_AUTHORITY_PROMOTION:1",lambda x:x["witnesses"][1].update(physical_act_allowed=True))
    def test_root_promotes_act(self):
        self.reject("ROOT_AUTHORITY_PROMOTION",lambda x:x.update(operational_authority="ACT"))
    def test_missing_previous_freeze(self):
        self.reject("PREVIOUS_FREEZE_BINDING_MISSING",lambda x:x.update(previous_phase_freeze=""))
    def test_wrong_schema(self):
        self.reject("ANCESTRY_SCHEMA_INVALID",lambda x:x.update(schema="FORGED"))
    def test_one_record_is_not_three(self):
        self.reject("EXACTLY_THREE_WITNESS_RECORDS_REQUIRED",lambda x:x.update(witnesses=[x["witnesses"][0]]))
    def test_repeat_assessment_stable(self):
        self.assertEqual(assess(fixture())["record_sha256"],assess(fixture())["record_sha256"])

if __name__=="__main__":
    unittest.main()
