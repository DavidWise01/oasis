import base64,copy,unittest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from process_ledger import assess,canon,digest,parse_stat

def fixture():
    boot="11111111-2222-3333-4444-555555555555"
    identities={"supervisor":{"pid":10,"start_ticks":100,"netns_inode":101,"boot_id":boot},
                "worker":{"pid":11,"start_ticks":200,"netns_inode":202,"boot_id":boot}}
    anchor="0"*64
    e={"sequence":0,"challenge_id":"fresh-1","nonce":"nonce-1","run_id":41,
       "identity_sha256":digest(identities),"previous_sha256":anchor}
    e["event_sha256"]=digest(e)
    statement={"schema":"AETHER-252/process-ledger-v1","head_sha256":e["event_sha256"],
               "identity_sha256":digest(identities)}
    pins={};receipts=[]
    for i in range(3):
        key=Ed25519PrivateKey.generate();kid="key"+str(i);root="root"+str(i)
        receipts.append({"key_id":kid,"controller_root":root,
                         "signature_b64":base64.b64encode(key.sign(canon(statement))).decode()})
        pins[kid]={"controller_root":root,"public_key_pem":key.public_key().public_bytes(
            serialization.Encoding.PEM,serialization.PublicFormat.SubjectPublicKeyInfo).decode()}
    return {"identities":identities,"externally_pinned_previous_head":anchor,
            "consumption_events":[e],"receipts":receipts,"witness_pins":pins}
class Tests(unittest.TestCase):
    def expect(self,mutation,reason):
        b=fixture();mutation(b);result=assess(b)
        self.assertIn(reason,result["reasons"],result)
        self.assertEqual(result["operational_authority"],"HOLD")
    def test_good_crypto_still_hold(self):
        x=assess(fixture())
        self.assertEqual(sum(v["valid"] for v in x["observed"]["signatures"]),3)
        self.assertIn("WITNESS_CONTROLLER_ANCESTRY_UNVERIFIED",x["reasons"])
    def test_same_namespace(self):self.expect(lambda b:b["identities"]["worker"].update(netns_inode=101),"NAMESPACE_NOT_SEPARATED")
    def test_wrong_boot(self):self.expect(lambda b:b["identities"]["worker"].update(boot_id="aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"),"BOOT_ID_MISMATCH")
    def test_same_process(self):
        def change(b):b["identities"]["worker"].update(pid=10,start_ticks=100)
        self.expect(change,"SAME_PROCESS_IDENTITY")
    def test_identity_substituted(self):self.expect(lambda b:b["identities"]["worker"].update(start_ticks=201),"EVENT_IDENTITY_SUBSTITUTED")
    def test_nonce_replay(self):
        def change(b):
            e=copy.deepcopy(b["consumption_events"][0]);e["sequence"]=1
            e["previous_sha256"]=b["consumption_events"][0]["event_sha256"]
            e["event_sha256"]=digest({k:v for k,v in e.items() if k!="event_sha256"})
            b["consumption_events"].append(e)
        self.expect(change,"NONCE_REPLAY")
    def test_hash_tamper(self):self.expect(lambda b:b["consumption_events"][0].update(challenge_id="tampered"),"EVENT_HASH_INVALID")
    def test_chain_broken(self):self.expect(lambda b:b["consumption_events"][0].update(previous_sha256="f"*64),"EVENT_CHAIN_BROKEN")
    def test_event_sequence(self):self.expect(lambda b:b["consumption_events"][0].update(sequence=9),"EVENT_SEQUENCE_INVALID")
    def test_untrusted_anchor(self):self.expect(lambda b:b.update(externally_pinned_previous_head="bad"),"EXTERNAL_ANCHOR_INVALID")
    def test_corrupt_signature(self):self.expect(lambda b:b["receipts"][0].update(signature_b64=base64.b64encode(b"x"*64).decode()),"SIGNATURE_INVALID")
    def test_unknown_key(self):self.expect(lambda b:b["witness_pins"].pop("key0"),"PUBLIC_KEY_NOT_PINNED")
    def test_duplicate_root(self):self.expect(lambda b:b["receipts"][1].update(controller_root="root0"),"ROOT_DUPLICATE_OR_INVALID")
    def test_missing_receipt(self):self.expect(lambda b:b["receipts"].pop(),"THREE_RECEIPTS_REQUIRED")
    def test_boolean_pid(self):self.expect(lambda b:b["identities"]["worker"].update(pid=True),"IDENTITY_VALUES_INVALID")
    def test_empty_events(self):self.expect(lambda b:b.update(consumption_events=[]),"EVENT_COUNT_INVALID")
    def test_bad_bundle(self):self.assertIn("BUNDLE_INVALID",assess(None)["reasons"])
    def test_proc_stat_parenthesis(self):
        raw="123 (weird ) comm) S "+" ".join(["0"]*18+["999"]+["0"]*4)
        self.assertEqual(parse_stat(raw)["start_ticks"],999)
    def test_proc_stat_short(self):
        with self.assertRaises(ValueError):parse_stat("123 (x) S 1")
if __name__=="__main__":unittest.main()
