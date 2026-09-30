# v184 synchronized cubic throughput

Benchmarks the verified six-branch cubic primitive:

    {{cubic::seed::1i::axes::(x,y:z)::cardinal::+15::clock::5/4/3/2/1/1/0/0}}

One completed cycle produces:

- 48 derived state facts (six branches across eight ticks)
- 6 terminal facts
- 1 synchronous closure fact
- 55 total derived facts
- 268 engine-local logical tokens, where one predicate or one atom argument
  counts as one logical token

The logical-token metric is deliberately not presented as an LLM/BPE token
rate. It is a symbolic throughput metric for this inference engine.
