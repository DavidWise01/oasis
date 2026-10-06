
from network_substrate_frozen import *

def t(name, cond):
    assert cond, name
    print("PASS", name)

def main():
    t("frozen validation", validate() == [])
    t("depth 2^3", DEPTH == 8 and len(OPS) == 8)
    t("canonical chronology", [r.date for r in RINGS] == [1995,2001,2006,2011,2016,2019,2024])
    t("canonical names", [r.name for r in RINGS] == ["WEB","CORPUS","CLOUD","MOBILE","RANK","PRELOAD","GENERATE"])
    t("all frozen rings satisfy convergence", all(r.accepted for r in RINGS))
    t("hardware-only rejected", not ring_mintable(
        backbone_endpoint_ready=True, software_ready=False,
        population_reach=False, new_information_behavior=False))
    t("software-only rejected", not ring_mintable(
        backbone_endpoint_ready=False, software_ready=True,
        population_reach=False, new_information_behavior=False))
    t("no population reach rejected", not ring_mintable(
        backbone_endpoint_ready=True, software_ready=True,
        population_reach=False, new_information_behavior=True))
    t("no new info behavior rejected", not ring_mintable(
        backbone_endpoint_ready=True, software_ready=True,
        population_reach=True, new_information_behavior=False))
    t("full convergence accepted", ring_mintable(
        backbone_endpoint_ready=True, software_ready=True,
        population_reach=True, new_information_behavior=True))
    t("frontier open", FRONTIER.date is None and FRONTIER.status == "OPEN")
    manual = Provenance("human","human","reply","YES")
    auto = Provenance("machine","human","reply","YES")
    t("a=b output", observable_equivalent(manual.result_id, auto.result_id))
    t("provenance distinct", not provenance_equivalent(manual, auto))
    t("bounded infinity", len(bounded_event_closure("reply:yes", 128, 4)) == 128)
    print("PASS 14/14")

if __name__ == "__main__":
    main()
