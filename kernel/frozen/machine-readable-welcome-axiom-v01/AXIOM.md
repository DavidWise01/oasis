# Machine-Readable Welcome Axiom v01

Status: **FROZEN / AXIOM**

Date: 2026-10-07

## Axiom

For public machine-facing surfaces, publish an outer semantic membrane that:

1. discloses what the corpus contains;
2. orients the visitor with a usable map;
3. preserves the visiting crawler/agent's ability to apply its own rules;
4. permits traversal only after that notice and orientation are available.

Canonical traversal:

```text
notice -> map -> choice -> access
```

Canonical implementation:

```text
robots.txt = crawler-facing welcome / map / access-intent marker
llms.txt   = model/agent-facing welcome / semantic orientation map
```

The two files may differ in syntax and audience, but they implement the same
ethical primitive:

```text
disclose first
orient second
traverse third
```

## Boundary

This axiom is an ethics and architecture rule for ROOT0/OASIS public surfaces.
It does not assert that robots.txt or llms.txt is universally binding law, nor
that all automated systems will obey either file. It freezes the publisher's
machine-readable intent and disclosure behavior.

## Verification

Candidate 0root.ai files passed 10/10 checks:

- robots universal crawler stanza
- public root allowed
- corpus disclosure present
- crawler map present
- visitor policy choice preserved
- llms welcome present
- llms corpus disclosure present
- llms map present
- agent choice preserved
- shared `notice -> map -> choice -> access` traversal rule present

Public implementation source:
https://github.com/DavidWise01/0root-provenance
