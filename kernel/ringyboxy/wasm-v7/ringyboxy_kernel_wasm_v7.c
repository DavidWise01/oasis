
#include <stdint.h>

/*
  v7: in-flight fence rollover atomicity.

  prepare_* validates an exact child certificate under the replica's current
  lease and captures the canonical epoch+digest seen at prepare time.

  unsafe_finalize commits the prepared child without rechecking the fence.
  strict_finalize requires the canonical fence to still equal the prepared
  fence at the instant the parent is consumed.

  parent_state:
    0 = unused
    1 = child A
    2 = child B
*/
static uint32_t parent_state = 0;

static uint32_t canonical_epoch = 0;
static uint32_t canonical_digest = 0;

static uint32_t lease_epoch = 0;
static uint32_t lease_digest = 0;
static uint32_t open_flag = 0;

static uint32_t prepared_child = 0;
static uint32_t prepared_epoch = 0;
static uint32_t prepared_digest = 0;
static uint32_t prepared_flag = 0;

__attribute__((export_name("reset")))
void reset(void) {
  parent_state = 0;
  canonical_epoch = 0;
  canonical_digest = 0;
  lease_epoch = 0;
  lease_digest = 0;
  open_flag = 0;
  prepared_child = 0;
  prepared_epoch = 0;
  prepared_digest = 0;
  prepared_flag = 0;
}

__attribute__((export_name("install_canonical_fence")))
uint32_t install_canonical_fence(uint32_t epoch, uint32_t digest) {
  if (epoch < canonical_epoch) return 0;
  canonical_epoch = epoch;
  canonical_digest = digest;
  return 1;
}

__attribute__((export_name("open_replica")))
uint32_t open_replica(uint32_t epoch, uint32_t digest) {
  if (epoch != canonical_epoch) return 0;
  if (digest != canonical_digest) return 0;
  lease_epoch = epoch;
  lease_digest = digest;
  open_flag = 1;
  return 1;
}

__attribute__((export_name("refresh_replica")))
uint32_t refresh_replica(uint32_t epoch, uint32_t digest) {
  return open_replica(epoch, digest);
}

static uint32_t cert_ok(uint32_t requested_child,
                        uint32_t cert_child,
                        uint32_t internal_votes,
                        uint32_t c1,
                        uint32_t c2) {
  if (requested_child != 1 && requested_child != 2) return 0;
  if (cert_child != requested_child) return 0;
  if (internal_votes < 2) return 0;
  if (c1 != 1 || c2 != 1) return 0;
  return 1;
}

__attribute__((export_name("prepare")))
uint32_t prepare(uint32_t requested_child,
                 uint32_t cert_child,
                 uint32_t internal_votes,
                 uint32_t c1,
                 uint32_t c2) {
  if (!open_flag) return 0;

  /* Lease must be current at PREPARE. */
  if (lease_epoch != canonical_epoch) return 0;
  if (lease_digest != canonical_digest) return 0;

  if (!cert_ok(requested_child, cert_child, internal_votes, c1, c2)) return 0;

  prepared_child = requested_child;
  prepared_epoch = canonical_epoch;
  prepared_digest = canonical_digest;
  prepared_flag = 1;
  return 1;
}

static uint32_t consume_prepared(void) {
  if (!prepared_flag) return 0;
  if (parent_state == prepared_child) {
    prepared_flag = 0;
    return 1; /* idempotent exact replay */
  }
  if (parent_state != 0) {
    prepared_flag = 0;
    return 0;
  }
  parent_state = prepared_child;
  prepared_flag = 0;
  return 1;
}

__attribute__((export_name("unsafe_finalize")))
uint32_t unsafe_finalize(void) {
  return consume_prepared();
}

__attribute__((export_name("strict_finalize")))
uint32_t strict_finalize(void) {
  if (!prepared_flag) return 0;

  /*
    Atomicity boundary in this single-threaded WASM model:
    the fence is revalidated immediately before parent consumption.
  */
  if (prepared_epoch != canonical_epoch) {
    prepared_flag = 0;
    return 0;
  }
  if (prepared_digest != canonical_digest) {
    prepared_flag = 0;
    return 0;
  }

  return consume_prepared();
}

__attribute__((export_name("state")))
uint32_t state(void) { return parent_state; }

__attribute__((export_name("prepared_state")))
uint32_t prepared_state(void) { return prepared_flag; }

__attribute__((export_name("canonical_epoch_state")))
uint32_t canonical_epoch_state(void) { return canonical_epoch; }
