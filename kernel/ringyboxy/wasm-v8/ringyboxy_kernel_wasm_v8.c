
#include <stdint.h>

/*
  v8: crash after parent consumption but before ACK.

  The module models two layers:

    committed_child / committed_txid
      = durable canonical commit record once restored/persisted

    ack_txid
      = volatile/client acknowledgement state

  Safety rule:
    ACK is never the source of truth.
    Recovery restores the durable commit record first.
    Exact txid replay is idempotent.
    Sibling txid/child cannot consume the already-used parent.
*/

static uint32_t committed_child = 0;
static uint32_t committed_txid = 0;
static uint32_t ack_txid = 0;

__attribute__((export_name("boot_empty")))
void boot_empty(void) {
  committed_child = 0;
  committed_txid = 0;
  ack_txid = 0;
}

__attribute__((export_name("restore_commit")))
uint32_t restore_commit(uint32_t child, uint32_t txid) {
  if (child > 2) return 0;
  if (child == 0 && txid != 0) return 0;
  if (child != 0 && txid == 0) return 0;
  committed_child = child;
  committed_txid = txid;
  ack_txid = 0;
  return 1;
}

__attribute__((export_name("commit_no_ack")))
uint32_t commit_no_ack(uint32_t child, uint32_t txid) {
  if (child != 1 && child != 2) return 0;
  if (txid == 0) return 0;

  if (committed_child == child && committed_txid == txid)
    return 1; /* exact idempotent replay */

  if (committed_child != 0)
    return 0; /* parent already consumed */

  committed_child = child;
  committed_txid = txid;
  return 1;
}

__attribute__((export_name("ack_commit")))
uint32_t ack_commit(uint32_t txid) {
  if (committed_txid == 0) return 0;
  if (txid != committed_txid) return 0;
  ack_txid = txid;
  return 1;
}

__attribute__((export_name("clear_volatile_ack")))
void clear_volatile_ack(void) {
  ack_txid = 0;
}

__attribute__((export_name("committed_child_state")))
uint32_t committed_child_state(void) { return committed_child; }

__attribute__((export_name("committed_txid_state")))
uint32_t committed_txid_state(void) { return committed_txid; }

__attribute__((export_name("ack_txid_state")))
uint32_t ack_txid_state(void) { return ack_txid; }
