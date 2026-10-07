
#include <stdint.h>

/*
  v9: atomic durable commit record recovery.

  Durable commit record fields:
    marker : 0 = absent, 1 = committed
    child  : 1 or 2
    txid   : nonzero
    crc    : deterministic record checksum

  Recovery rule:
    accept durable state only when the whole record is self-consistent.
    Any torn/partial/corrupt record keeps the commit gate CLOSED.

  This models the recovery invariant; it is not a filesystem implementation.
*/

static uint32_t committed_child = 0;
static uint32_t committed_txid = 0;
static uint32_t recovery_open = 0;

static uint32_t record_crc(uint32_t marker, uint32_t child, uint32_t txid) {
  uint32_t x = 0x9E3779B9u;
  x ^= marker * 0x85EBCA6Bu;
  x ^= child  * 0xC2B2AE35u;
  x ^= txid;
  x ^= (x >> 16);
  x *= 0x7FEB352Du;
  x ^= (x >> 15);
  return x;
}

__attribute__((export_name("boot_closed")))
void boot_closed(void) {
  committed_child = 0;
  committed_txid = 0;
  recovery_open = 0;
}

/*
  Restore a supposedly durable record.
  Returns 1 only if the record is complete and valid.
*/
__attribute__((export_name("restore_record")))
uint32_t restore_record(uint32_t marker,
                        uint32_t child,
                        uint32_t txid,
                        uint32_t crc) {
  recovery_open = 0;
  committed_child = 0;
  committed_txid = 0;

  if (marker != 1) return 0;
  if (child != 1 && child != 2) return 0;
  if (txid == 0) return 0;
  if (crc != record_crc(marker, child, txid)) return 0;

  committed_child = child;
  committed_txid = txid;
  recovery_open = 1;
  return 1;
}

/* Empty ledger is explicitly valid and may open a fresh parent. */
__attribute__((export_name("restore_empty")))
uint32_t restore_empty(void) {
  committed_child = 0;
  committed_txid = 0;
  recovery_open = 1;
  return 1;
}

__attribute__((export_name("make_crc")))
uint32_t make_crc(uint32_t marker, uint32_t child, uint32_t txid) {
  return record_crc(marker, child, txid);
}

__attribute__((export_name("try_commit")))
uint32_t try_commit(uint32_t child, uint32_t txid) {
  if (!recovery_open) return 0;
  if (child != 1 && child != 2) return 0;
  if (txid == 0) return 0;

  if (committed_child == child && committed_txid == txid)
    return 1; /* exact replay */

  if (committed_child != 0)
    return 0; /* consumed */

  committed_child = child;
  committed_txid = txid;
  return 1;
}

__attribute__((export_name("child_state")))
uint32_t child_state(void) { return committed_child; }

__attribute__((export_name("txid_state")))
uint32_t txid_state(void) { return committed_txid; }

__attribute__((export_name("open_state")))
uint32_t open_state(void) { return recovery_open; }
