
from dataclasses import dataclass
from typing import Optional, Tuple
from collections import deque

DEPTH = 2**3
OPS = ("source", "encode", "retain", "address", "route", "trigger", "transform", "recover")
CROSSING_STATES = ("PUT_IN", "CREATED", "TRANSFORMED", "ABANDONED")

@dataclass(frozen=True)
class Ring:
    date: int
    name: str
    backbone_endpoint_ready: bool
    software_ready: bool
    population_reach: bool
    new_information_behavior: bool
    behavior: str

    @property
    def accepted(self) -> bool:
        return all((
            self.backbone_endpoint_ready,
            self.software_ready,
            self.population_reach,
            self.new_information_behavior,
        ))

@dataclass(frozen=True)
class Frontier:
    name: str = "NEXT?"
    date: Optional[int] = None
    status: str = "OPEN"

@dataclass(frozen=True)
class Provenance:
    selector_origin: str
    trigger_origin: str
    source_id: str
    result_id: str

@dataclass(frozen=True)
class TriggerPacket:
    event: str
    selector_origin: str
    trigger_origin: str
    rule: str
    resulting_state: str
    next_events: Tuple[str, ...]

RINGS = (
    Ring(1995, "WEB", True, True, True, True,
         "human requests retained network information"),
    Ring(2001, "CORPUS", True, True, True, True,
         "machine indexes and recovers from expanding public corpora"),
    Ring(2006, "CLOUD", True, True, True, True,
         "storage and compute become callable network services"),
    Ring(2011, "MOBILE", True, True, True, True,
         "network access becomes continuously attached to handheld endpoints"),
    Ring(2016, "RANK", True, True, True, True,
         "machine selects which retained item becomes visible next"),
    Ring(2019, "PRELOAD", True, True, True, True,
         "machine preloads likely next information before explicit request"),
    Ring(2024, "GENERATE", True, True, True, True,
         "machine can generate candidate information/actions before execution"),
)

FRONTIER = Frontier()

def ring_mintable(*, backbone_endpoint_ready: bool, software_ready: bool,
                  population_reach: bool, new_information_behavior: bool) -> bool:
    return all((backbone_endpoint_ready, software_ready,
                population_reach, new_information_behavior))

def observable_equivalent(result_a: str, result_b: str) -> bool:
    return result_a == result_b

def provenance_equivalent(a: Provenance, b: Provenance) -> bool:
    return a == b

def bounded_event_closure(seed: str, max_steps: int = 64, fanout: int = 2):
    """
    Conceptual ∞ automation, implemented safely as a finite closure.
    Every retained event may emit more events; runtime is bounded by max_steps.
    """
    queue = deque([seed])
    retained = []
    i = 0
    while queue and i < max_steps:
        event = queue.popleft()
        state = f"retained:{event}"
        retained.append(state)
        # deterministic child emission, no randomness
        if i + 1 < max_steps:
            for j in range(fanout):
                queue.append(f"{event}>{j}")
        i += 1
    return tuple(retained)

def walk():
    return tuple((r.date, r.name, r.behavior) for r in RINGS) + (
        (FRONTIER.date, FRONTIER.name, FRONTIER.status),
    )

def validate():
    errors = []

    if DEPTH != 8:
        errors.append("depth must equal 2^3 = 8")

    if len(OPS) != DEPTH:
        errors.append("operation count must equal depth")

    dates = [r.date for r in RINGS]
    if dates != sorted(dates) or len(dates) != len(set(dates)):
        errors.append("ring dates must be unique and monotonic")

    if [r.name for r in RINGS] != ["WEB","CORPUS","CLOUD","MOBILE","RANK","PRELOAD","GENERATE"]:
        errors.append("canonical ring names changed")

    if not all(r.accepted for r in RINGS):
        errors.append("a frozen ring fails the four-part convergence rule")

    if FRONTIER.date is not None or FRONTIER.status != "OPEN":
        errors.append("NEXT? frontier must remain open and undated")

    # Hardware-only/software-only launches must not mint a ring.
    probes = (
        ring_mintable(backbone_endpoint_ready=True, software_ready=False,
                      population_reach=False, new_information_behavior=False),
        ring_mintable(backbone_endpoint_ready=False, software_ready=True,
                      population_reach=False, new_information_behavior=False),
        ring_mintable(backbone_endpoint_ready=True, software_ready=True,
                      population_reach=False, new_information_behavior=True),
        ring_mintable(backbone_endpoint_ready=True, software_ready=True,
                      population_reach=True, new_information_behavior=False),
    )
    if any(probes):
        errors.append("partial convergence incorrectly minted a ring")

    # a=b at output boundary, while provenance remains distinguishable.
    manual = Provenance("human", "human", "reply", "YES")
    auto   = Provenance("machine", "human", "reply", "YES")
    if not observable_equivalent(manual.result_id, auto.result_id):
        errors.append("a=b output equivalence failed")
    if provenance_equivalent(manual, auto):
        errors.append("provenance was incorrectly collapsed")

    # ∞ closure must be conceptually chainable but operationally bounded.
    if len(bounded_event_closure("reply:yes", max_steps=32, fanout=3)) != 32:
        errors.append("bounded event closure failed")

    return errors
