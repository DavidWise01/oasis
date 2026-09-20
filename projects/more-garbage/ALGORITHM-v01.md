# MORE GARBAGE algorithm v01 — primitive scope

v00 tested whole strings. That scope was wrong.

v01 runs **one primitive at a time**.

```text
i = current primitive

right?
├── Y → +1 → move on
└── N → (0,0,0,-1) down
          ↓
       local search
          ↓
       recover exactly one primitive?
       ├── Y → five gates → emit → move forward
       └── N → rm / A::xx → delete current → move forward
```

Example:

```text
Mona

M → Y → +1
o → Y → +1
n → Y → +1
a → Y → +1
```

The scanner does not pay recursive search cost for aligned primitives.

For a failed alignment, it opens progressively larger local windows and asks whether that corrupted cluster can be inverted into exactly one normalized output primitive. This is how a multi-character mojibake cluster can still represent one bad primitive.

## Cost model

```text
base scan                n
failed local search      n
scan × search            n · n = n²   worst-case structural bound
```

The encoding set and recursion depth are bounded constants in v01, so they multiply the search cost without changing the n² structural model.

## Five local gates

A recovered local primitive still has to pass:

```text
verify → sort → verify → compress → expand
```

Any NO invokes `rm / A::xx` for the current primitive and continues forward.

## White-whale correction

The Mona Lisa sentence is not processed as one repair object. Clean primitives walk linearly until the corrupted apostrophe cluster is reached.

For:

```text
The Mona Lisa doesnÃƒÂ¢Ã¢â€šÂ¬Ã¢â€žÂ¢t have eyebrows.
```

v01 walks the clean prefix one primitive at a time, descends only at the corrupted local cluster, recovers that cluster as `’`, and resumes +1 traversal.

This makes recursion a **cost of failed alignment**, not the default execution mode.
