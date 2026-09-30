# v184 inference benchmark harness

This directory benchmarks the sealed ae-inference-v184 engine without changing
the sealed kernel.

Metrics:

- fixed-point latency
- derivations per second
- v183 microcycles per second
- approximate logical terms per second

logical_terms_per_second_approx is an engine-local rough scalar, not an LLM
tokenizer throughput measurement.

Scenarios:

1. 5,000 repeated v183 +1 -> 0&1 microcycles.
2. 10,000 unary facts through two inference stages (20,000 derivations).
3. 500-key two-premise join.
4. transitive closure of a 20-node chain.

GitHub Actions runner results are useful for regression tracking but should not
be treated as hardware-independent absolute performance.
