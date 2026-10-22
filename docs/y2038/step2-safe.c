#include <stdint.h>
#include <stdbool.h>
#include <limits.h>
#include <stdio.h>
#include <inttypes.h>

bool to_legacy_i32(int64_t seconds, int32_t *out) {
    if (!out || seconds < INT32_MIN || seconds > INT32_MAX) {
        return false;
    }
    *out = (int32_t)seconds;
    return true;
}

int main(void) {
    const int64_t samples[] = {2147483647LL, 2147483648LL, 2208988800LL};
    for (size_t i = 0; i < sizeof(samples)/sizeof(samples[0]); ++i) {
        int32_t legacy = 0;
        bool ok = to_legacy_i32(samples[i], &legacy);
        if (ok) {
            printf("%" PRId64 " -> %" PRId32 "\n", samples[i], legacy);
        } else {
            printf("%" PRId64 " -> REJECTED (out of int32 range)\n", samples[i]);
        }
    }
    return 0;
}
