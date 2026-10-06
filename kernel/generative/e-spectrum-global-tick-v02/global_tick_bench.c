#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <time.h>
#include <assert.h>

typedef struct {
    uint64_t tick;
    uint8_t active;
} Cell;

static inline void cycle(Cell *cells, size_t n) {
    for (size_t i = 0; i < n; ++i) {
        if (cells[i].active) cells[i].tick += 1;
    }
}

static double now_sec(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (double)ts.tv_sec + (double)ts.tv_nsec / 1e9;
}

static void invariant_tests(void) {
    Cell a[3] = {{0,1},{0,0},{0,1}};
    cycle(a, 3);
    assert(a[0].tick == 1);
    assert(a[1].tick == 0);
    assert(a[2].tick == 1);

    size_t n = 1024;
    Cell *cells = calloc(n, sizeof(Cell));
    assert(cells);
    for (size_t i = 0; i < n; ++i) cells[i].active = 1;
    for (int c = 0; c < 100; ++c) cycle(cells, n);
    for (size_t i = 0; i < n; ++i) assert(cells[i].tick == 100);
    free(cells);
}

static void benchmark(size_t n, size_t cycles) {
    Cell *cells = calloc(n, sizeof(Cell));
    if (!cells) { perror("calloc"); exit(1); }
    for (size_t i = 0; i < n; ++i) cells[i].active = 1;

    double t0 = now_sec();
    for (size_t c = 0; c < cycles; ++c) cycle(cells, n);
    double t1 = now_sec();

    uint64_t checksum = 0;
    for (size_t i = 0; i < n; ++i) checksum += cells[i].tick;

    uint64_t updates = (uint64_t)n * (uint64_t)cycles;
    assert(checksum == updates);

    double dt = t1 - t0;
    printf("cells=%zu cycles=%zu updates=%llu seconds=%.6f updates_per_second=%.3fM checksum=%llu\n",
           n, cycles, (unsigned long long)updates, dt, updates / dt / 1e6,
           (unsigned long long)checksum);
    free(cells);
}

int main(void) {
    invariant_tests();
    puts("0e / GLOBAL TICK C INVARIANTS PASS");
    benchmark(1000, 100000);
    benchmark(10000, 10000);
    benchmark(100000, 1000);
    benchmark(1000000, 100);
    return 0;
}
