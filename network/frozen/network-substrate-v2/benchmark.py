
import time, json
from network_substrate_frozen import bounded_event_closure, walk, validate

def bench():
    validation = validate()
    sizes = [1_000, 10_000, 100_000, 500_000]
    rows = []
    for n in sizes:
        t0 = time.perf_counter()
        out = bounded_event_closure("reply:yes", max_steps=n, fanout=2)
        dt = time.perf_counter() - t0
        rows.append({
            "steps": n,
            "seconds": dt,
            "events_per_second": n/dt if dt else None,
            "retained_states": len(out),
        })
    return {
        "validation_errors": validation,
        "walk": walk(),
        "benchmark": rows,
    }

if __name__ == "__main__":
    print(json.dumps(bench(), indent=2))
