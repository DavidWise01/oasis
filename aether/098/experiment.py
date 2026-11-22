#!/usr/bin/env python3
"""AETHER-098: single-controller causal and deterministic decision path.
All measurements, tests and outcomes are synthetic, not a production safety guarantee.
"""
import csv, hashlib, json, random
from dataclasses import dataclass
from pathlib import Path

OUT = Path(__file__).resolve().parent
SEEDS = list(range(98001, 98081))
TICKS = 96
AUDIT_N = 140
SENTINEL_N = 80
ACTIONS_N = 150
RISK_LIMIT = 0.02


def risk(t, scenario):
    if scenario == 'switch':
        return .003 if t < 24 or 48 <= t < 68 or t >= 84 else .075
    if scenario == 'decoy':
        return .003 if t < 24 or 48 <= t < 68 or t >= 84 else (.018 if t < 48 else .075)
    return .003


def bernoulli_count(rng, n, p):
    return sum(rng.random() < p for _ in range(n))


def observations(seed, scenario):
    rng = random.Random(seed + {'switch': 0, 'decoy': 100000, 'stable': 200000}[scenario])
    return [dict(tick=t, audit=bernoulli_count(rng, AUDIT_N, risk(t, scenario)),
                 sentinel=bernoulli_count(rng, SENTINEL_N, risk(t, scenario)),
                 heldout_wrong=bernoulli_count(rng, ACTIONS_N, risk(t, scenario)))
            for t in range(TICKS)]


def simple_upper(errors, n):
    # Exact one-sided fixed-time Clopper-Pearson upper bound.
    # Applied to an observed window only, not a guarantee after hidden drift.
    from scipy.stats import beta
    return 1.0 if n == 0 or errors >= n else float(beta.ppf(.95, errors + 1, n - errors))


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(',', ':'))


def event_hash(prev, event):
    return hashlib.sha256((prev + '|' + canonical(event)).encode('utf-8')).hexdigest()


def execute(stream, seed, scenario):
    audit_history = []
    burst_permission = False
    status = 'OBSERVE'
    chain = '0' * 64
    out = []
    for obs in stream:
        t = obs['tick']; a = int(obs['audit'])
        audit_history = (audit_history + [a])[-5:]
        high = a >= 7 or (len(audit_history) >= 2 and sum(audit_history[-2:]) >= 13)
        contradiction = burst_permission and a <= 3
        if high:
            burst_permission = True
        elif contradiction:
            burst_permission = False
        upper = simple_upper(sum(audit_history), len(audit_history) * AUDIT_N)
        # Single canonical selector: HOLD if risk not certified; else ACT unless sentinel alarms.
        # The sentinel is requested only under a currently eligible context and near a bound.
        probe = bool(burst_permission and .015 <= upper <= .045)
        alarm = bool(probe and int(obs['sentinel']) >= 3)
        authorized = bool(upper <= RISK_LIMIT and not alarm)
        status = 'ACT' if authorized else 'HOLD'
        decision = dict(seed=seed, scenario=scenario, tick=t,
                        audit=a, sentinel_used=int(obs['sentinel']) if probe else None,
                        context='BURST' if burst_permission else 'OTHER',
                        contradiction=bool(contradiction), probe=probe, alarm=alarm,
                        bound=round(upper, 8), action=status)
        h = event_hash(chain, decision)
        result = {**decision, 'heldout_wrong': int(obs['heldout_wrong']) if authorized else 0,
                  'withheld': 0 if authorized else ACTIONS_N,
                  'labels': AUDIT_N + (SENTINEL_N if probe else 0),
                  'prior_hash': chain, 'hash': h}
        out.append(result)
        chain = h
    return out


def verify_chain(rows):
    previous = '0' * 64
    for row in rows:
        if row['prior_hash'] != previous:
            return False
        d = {k: row[k] for k in ('seed', 'scenario', 'tick', 'audit', 'sentinel_used',
             'context', 'contradiction', 'probe', 'alarm', 'bound', 'action')}
        if event_hash(previous, d) != row['hash']:
            return False
        previous = row['hash']
    return True


def save_csv(name, rows):
    with open(OUT / name, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)


def main():
    report = []
    audits = []
    failures = []
    replay_pass = future_pass = hash_pass = sentinel_pass = 0
    n_cases = 0
    scenarios = ('switch', 'decoy', 'stable')
    for scenario in scenarios:
        for seed in SEEDS:
            orig = observations(seed, scenario)
            baseline = execute(orig, seed, scenario)
            replay = execute(orig, seed, scenario)
            n_cases += 1
            rp = baseline == replay
            hp = verify_chain(baseline)
            # Perturb ALL future observation fields after a fixed cut and re-run.
            # Earlier decisions AND prior hashes must remain unchanged.
            cut = 48
            changed = [dict(x) for x in orig]
            for row in changed[cut:]:
                row['audit'] = (row['audit'] + 19) % 141
                row['sentinel'] = (row['sentinel'] + 31) % 81
                row['heldout_wrong'] = (row['heldout_wrong'] + 7) % 151
            after = execute(changed, seed, scenario)
            cp = baseline[:cut] == after[:cut]
            # Sentinel observations are forbidden from influencing decisions when unsampled.
            sentinel_changed = [dict(x) for x in orig]
            for j, row in enumerate(sentinel_changed):
                if not baseline[j]['probe']:
                    row['sentinel'] = 80 - row['sentinel']
            sentinel_replay = execute(sentinel_changed, seed, scenario)
            sp = all(b['action'] == x['action'] and b['hash'] == x['hash'] for b, x in zip(baseline, sentinel_replay))
            replay_pass += rp; future_pass += cp; hash_pass += hp; sentinel_pass += sp
            # Counterfactual failures are preserved; no success assumed.
            if not all((rp, cp, hp, sp)):
                failures.append(dict(seed=seed, scenario=scenario, replay=rp, future_prefix=cp,
                                     chain=hp, unused_sentinel_independence=sp))
            acts = sum(x['action'] == 'ACT' for x in baseline)
            wrong = sum(x['heldout_wrong'] for x in baseline)
            withheld = sum(x['withheld'] for x in baseline)
            labels = sum(x['labels'] for x in baseline)
            revocations = sum(x['contradiction'] for x in baseline)
            cost = round(10*wrong + .05*withheld + .01*labels, 2)
            report.append(dict(seed=seed, scenario=scenario, ticks=TICKS, acts=acts,
                               holds=TICKS-acts, wrong=wrong, withheld=withheld,
                               labels=labels, context_revocations=revocations, cost=cost,
                               replay_pass=rp, causal_prefix_pass=cp,
                               append_chain_pass=hp, unsampled_sentinel_pass=sp))
            if seed == SEEDS[0]:
                audits.extend(baseline)
    save_csv('seed_results.csv', report)
    save_csv('trace_samples.csv', audits)
    if failures: save_csv('failures.csv', failures)
    summary = []
    for scenario in (*scenarios, 'ALL'):
        subset = [r for r in report if scenario == 'ALL' or r['scenario'] == scenario]
        summary.append(dict(scenario=scenario, cases=len(subset), ticks=sum(r['ticks'] for r in subset),
                            acts=sum(r['acts'] for r in subset), holds=sum(r['holds'] for r in subset),
                            wrong=sum(r['wrong'] for r in subset), labels=sum(r['labels'] for r in subset),
                            revocations=sum(r['context_revocations'] for r in subset),
                            cost=round(sum(r['cost'] for r in subset),2)))
    save_csv('results.csv', summary)
    accepted = (n_cases == 240 and not failures and
                all((replay_pass == n_cases, future_pass == n_cases,
                     hash_pass == n_cases, sentinel_pass == n_cases)))
    manifest = dict(bound='AETHER-098', phase='II', cases=n_cases, ticks_per_case=TICKS,
                    replay_pass=replay_pass, causal_prefix_pass=future_pass,
                    append_chain_pass=hash_pass, unused_sentinel_pass=sentinel_pass,
                    failures=len(failures), accepted=accepted,
                    phase_completed=3 if accepted else 2,
                    phase_percent=37.5 if accepted else 25.0,
                    limitations=['Synthetic independently generated observations',
                                 'Fixed-window Clopper-Pearson bounds do not ensure future risk under drift',
                                 'Hash chain is a tamper-evident simulation log, not trusted external storage'])
    (OUT/'manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
    print(json.dumps({'manifest':manifest,'results':summary},indent=2))

if __name__ == '__main__': main()