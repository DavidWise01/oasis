# Y2038 Workshop — Step 2: Conversion audit

[Step 1](index.html) → [Interactive Step 2](step2.html)

Step 1 sets 64-bit time on supported builds. Step 2 audits every place a 64-bit timestamp could be narrowed by a cast, C type, ABI, database, or network protocol.

## Compile the numeric guard

```sh
cc -std=c11 -Wall -Wextra -Werror step2-safe.c -o step2-safe
./step2-safe
```

The sample accepts 2147483647 and rejects 2147483648 and 2208988800 as out of 32-bit signed range. The helper guards a numeric conversion; it does not migrate database fields or binary protocol layouts.

## Search

```sh
git grep -nE 'time_t|int32_t|uint32_t|time32|timestamp|strftime|mktime|localtime|gmtime|%d|%ld' -- '*.c' '*.h' '*.cpp' '*.hpp'
```

Search output and the website heuristics require human review. Beware mismatched printf formats, struct packing, external ABI layouts, serialized timestamps, and legacy consumers.

## Publish

The static files in `docs/y2038/` can be served at `/oasis/docs/y2038/step2.html` if GitHub Pages is configured to publish repository root of `main`. GitHub Pages settings and deployment were not changed by these commits.
