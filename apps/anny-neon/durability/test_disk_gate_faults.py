#!/usr/bin/env python3
"""ANNY SQLite crash-analogue negative controls, not physical power-loss tests."""
import importlib.util
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('anny_disk_gate', HERE / 'disk_gate.py')
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)


class FailClosedEffectTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='anny-disk-negative-')
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        gate.prepare(self.root, 'CONFIRM_COMMITTED')
        with gate.db(self.root / 'journal.sqlite3') as j:
            j.execute('UPDATE journal SET state=?,receipt_digest=? WHERE id=?',
                      ('CONFIRMED', gate.DIGEST, gate.TRANSFER))

    def mutate_receiver(self, sql, args=()):
        with gate.db(self.root / 'receiver.sqlite3') as r:
            r.execute(sql, args)

    def mutate_journal(self, sql, args=()):
        with gate.db(self.root / 'journal.sqlite3') as j:
            j.execute(sql, args)

    def assert_held(self):
        record = gate.inspect(self.root)
        self.assertEqual(record['violet'], 'HELD', record)
        self.assertEqual(record['state'], 'CONFIRMED')
        self.assertEqual(record['integrity'], ['ok', 'ok'])

    def test_valid_single_effect_verifies(self):
        self.assertEqual(gate.inspect(self.root)['violet'], 'VERIFIED')

    def test_duplicate_unrelated_receiver_effect_fails_closed(self):
        self.mutate_receiver('INSERT INTO receiver VALUES (?,?,?,?,?,?)',
                             ('extra:'+gate.DIGEST, 'other', gate.DIGEST,
                              gate.SOURCE.hex(), 1, 1))
        record=gate.inspect(self.root)
        self.assertEqual(record['effect_count'], 2)
        self.assertEqual(record['receiver_rows'], 2)
        self.assert_held()

    def test_receiver_digest_corruption_fails_closed(self):
        self.mutate_receiver('UPDATE receiver SET digest=? WHERE delivery_key=?',
                             ('0'*64, gate.KEY))
        self.assert_held()

    def test_receiver_source_corruption_fails_closed(self):
        self.mutate_receiver('UPDATE receiver SET source_hex=? WHERE delivery_key=?',
                             ('ff'*5, gate.KEY))
        self.assert_held()

    def test_receiver_acceptance_revoked_fails_closed(self):
        self.mutate_receiver('UPDATE receiver SET accepted=? WHERE delivery_key=?',
                             (0, gate.KEY))
        self.assert_held()

    def test_journal_receipt_corruption_fails_closed(self):
        self.mutate_journal('UPDATE journal SET receipt_digest=? WHERE id=?',
                            ('0'*64, gate.TRANSFER))
        self.assert_held()

    def test_journal_source_corruption_fails_closed(self):
        self.mutate_journal('UPDATE journal SET source_hex=? WHERE id=?',
                            ('ff'*5, gate.TRANSFER))
        self.assert_held()

    def test_both_digest_fields_wrong_even_if_matching_fails_closed(self):
        self.mutate_journal('UPDATE journal SET digest=?,receipt_digest=? WHERE id=?',
                            ('0'*64, '0'*64, gate.TRANSFER))
        self.mutate_receiver('UPDATE receiver SET digest=? WHERE delivery_key=?',
                             ('0'*64, gate.KEY))
        self.assert_held()

    def test_receiver_receipt_missing_fails_closed(self):
        self.mutate_receiver('DELETE FROM receiver WHERE delivery_key=?', (gate.KEY,))
        self.assert_held()

    def test_unconfirmed_state_with_valid_effect_is_held(self):
        self.mutate_journal('UPDATE journal SET state=? WHERE id=?',
                            ('RELEASE_PENDING', gate.TRANSFER))
        value=gate.inspect(self.root)
        self.assertEqual(value['violet'], 'HELD')

    def test_receiver_transfer_id_corruption_fails_closed(self):
        self.mutate_receiver('UPDATE receiver SET transfer_id=? WHERE delivery_key=?',
                             ('unknown',gate.KEY))
        self.assert_held()


if __name__ == '__main__':
    unittest.main(verbosity=2)
