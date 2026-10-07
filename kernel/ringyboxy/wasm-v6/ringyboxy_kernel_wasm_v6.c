#include <stdint.h>

/*
  v6: live fencing-token rollover.

  canonical fence:
    current_epoch/current_digest

  replica lease:
    lease_epoch/lease_digest

  Unsafe commit path checks only that the replica was once opened.
  Strict commit path requires the lease to equal the current canonical fence
  at the instant of commit.
*/
static uint32_t parent_state = 0;
static uint32_t current_epoch = 0;
static uint32_t current_digest = 0;
static uint32_t lease_epoch = 0;
static uint32_t lease_digest = 0;
static uint32_t open_flag = 0;

__attribute__((export_name("reset")))
void reset(void) {
  parent_state = 0;
  current_epoch = 0;
  current_digest = 0;
  lease_epoch = 0;
  lease_digest = 0;
  open_flag = 0;
}

__attribute__((export_name("install_canonical_fence")))
uint32_t install_canonical_fence(uint32_t epoch, uint32_t digest) {
  if (epoch < current_epoch) return 0;
  current_epoch = epoch;
  current_digest = digest;
  return 1;
}

__attribute__((export_name("open_replica")))
uint32_t open_replica(uint32_t epoch, uint32_t digest) {
  if (epoch != current_epoch) return 0;
  if (digest != current_digest) return 0;
  lease_epoch = epoch;
  lease_digest = digest;
  open_flag = 1;
  return 1;
}

__attribute__((export_name("refresh_replica")))
uint32_t refresh_replica(uint32_t epoch, uint32_t digest) {
  if (epoch != current_epoch) return 0;
  if (digest != current_digest) return 0;
  lease_epoch = epoch;
  lease_digest = digest;
  open_flag = 1;
  return 1;
}

__attribute__((export_name("state")))
uint32_t state(void) { return parent_state; }

__attribute__((export_name("lease_epoch_state")))
uint32_t lease_epoch_state(void) { return lease_epoch; }

__attribute__((export_name("canonical_epoch_state")))
uint32_t canonical_epoch_state(void) { return current_epoch; }

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

static uint32_t consume_parent(uint32_t requested_child) {
  if (parent_state == requested_child) return 1;
  if (parent_state != 0) return 0;
  parent_state = requested_child;
  return 1;
}

__attribute__((export_name("try_commit_unsafe")))
uint32_t try_commit_unsafe(uint32_t requested_child,
                           uint32_t cert_child,
                           uint32_t internal_votes,
                           uint32_t c1,
                           uint32_t c2) {
  if (!open_flag) return 0;
  if (!cert_ok(requested_child, cert_child, internal_votes, c1, c2)) return 0;
  return consume_parent(requested_child);
}

__attribute__((export_name("try_commit_strict")))
uint32_t try_commit_strict(uint32_t requested_child,
                           uint32_t cert_child,
                           uint32_t internal_votes,
                           uint32_t c1,
                           uint32_t c2) {
  if (!open_flag) return 0;
  if (lease_epoch != current_epoch) return 0;
  if (lease_digest != current_digest) return 0;
  if (!cert_ok(requested_child, cert_child, internal_votes, c1, c2)) return 0;
  return consume_parent(requested_child);
}
