# Y2038 Workshop — Step 1

Interactive, dependency-free walkthrough for the Unix Year 2038 time rollover issue.

Open `index.html` in a browser or publish this folder with GitHub Pages.

## Step 1 — Repeat

1. Keep the Unix epoch at 1970-01-01T00:00:00Z.
2. On a supported 32-bit Linux/glibc configuration, define `_FILE_OFFSET_BITS=64` and `_TIME_BITS=64` before system headers.
3. Assert `sizeof(time_t) >= 8` at compile time.
4. Compile and run `time64.c`:

```sh
cc -std=c11 -Wall -Wextra -Werror time64.c -o time64
./time64
```

The program prints the current timestamp and `time_t` width. A width >= 64 bits is required. This does not guarantee every dependency or persisted timestamp is Y2038-safe.

## Publish as independent repository

Copy the contents of this folder to a newly created GitHub repository. In repository Settings → Pages, set Deploy from a branch, main, /(root). Pages configuration is not managed by the current integration.

## Boundaries

Max signed 32-bit: `2^31 - 1` = `2147483647` = 2038-01-19 03:14:07 UTC.
The following value may wrap to `-2147483648` on implementations using 32-bit wrapping. Signed overflow in C itself is undefined behavior; the browser demonstration explicitly applies two's complement narrowing.

## Scope

Step 1 only. No claims of OS-wide remediation. Follow-up audits must cover wire formats, storage, and dependent libraries.
