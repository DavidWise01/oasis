#define _FILE_OFFSET_BITS 64
#define _TIME_BITS 64
#include <stdint.h>
#include <stdio.h>
#include <time.h>
#include <inttypes.h>

_Static_assert(sizeof(time_t) >= 8, "Y2038 unsafe: time_t must be >=64 bits");

int main(void) {
    time_t now = time(NULL);
    if (now == (time_t)-1) {
        fputs("Clock read failed\n", stderr);
        return 1;
    }
    printf("Unix timestamp: %" PRId64 "\n", (int64_t)now);
    printf("time_t width: %zu bits\n", sizeof(time_t) * 8);
    return 0;
}
