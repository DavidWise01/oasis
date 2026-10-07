#include <stdint.h>

/*
  v5: recovery snapshot fencing.

  A replica may only OPEN after its restored durable snapshot matches the
  externally agreed recovery fence exactly:
      snapshot_epoch == required_epoch
      snapshot_digest == required_digest

  parent_state:
    0 = unused
    1 = child A committed
    2 = child B committed

  phase:
    0 = CLOSED / recovering
    1 = OPEN
*/
static uint32_t parent_state = 0;
static uint32_t phase = 0;
static uint32_t snapshot_epoch = 0;
static uint32_t snapshot_digest = 0;

__attribute__((export_name("boot")))
void boot(void) {
  parent_state = 0;
  phase = 0;
  snapshot_epoch = 0;
  snapshot_digest = 0;
}

__attribute__((export_name("install_snapshot")))
uint32_t install_snapshot(uint32_t epoch,
                          uint32_t committed_child,
                          uint32_t digest) {
  if (phase != 0) return 0;
  if (committed_child > 2) return 0;
  snapshot_epoch = epoch;
  parent_state = committed_child;
  snapshot_digest = digest;
  return 1;
}

__attribute__((export_name("finish_recovery_fenced")))
uint32_t finish_recovery_fenced(uint32_t required_epoch,
                                uint32_t required_digest) {
  if (phase != 0) return 0;
  if (snapshot_epoch != required_epoch) return 0;
  if (snapshot_digest != required_digest) return 0;
  phase = 1;
  return 1;
}

__attribute__((export_name("phase_state")))
uint32_t phase_state(void) { return phase; }

__attribute__((export_name("state")))
uint32_t state(void) { return parent_state; }

__attribute__((export_name("snapshot_epoch_state")))
uint32_t snapshot_epoch_state(void) { return snapshot_epoch; }

__attribute__((export_name("snapshot_digest_state")))
uint32_t snapshot_digest_state(void) { return snapshot_digest; }

__attribute__((export_name("try_commit")))
uint32_t try_commit(uint32_t requested_child,
                    uint32_t cert_child,
                    uint32_t internal_votes,
                    uint32_t c1,
                    uint32_t c2) {
  if (phase != 1) return 0;
  if (requested_child != 1 && requested_child != 2) return 0;
  if (cert_child != requested_child) return 0;
  if (internal_votes < 2) return 0;
  if (c1 != 1 || c2 != 1) return 0;

  if (parent_state == requested_child) return 1;
  if (parent_state != 0) return 0;

  parent_state = requested_child;
  return 1;
}
