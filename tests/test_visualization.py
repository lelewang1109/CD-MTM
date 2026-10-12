"""Protect scientific plotting against undefined rates and stale numeric caches."""
from pathlib import Path
import sys
import tempfile
import unittest
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'analysis'))
from visualization.catalog import motion_rate, evenly_spaced_frames
from visualization.rendering import fingerprint


class EvidenceTests(unittest.TestCase):
    def test_no_events_is_undefined_not_perfect_performance(self):
        record = {'proxy': [{'method': 'R 20%', 'k': 2, 'eps': .02, 'clear': 0},
                            {'method': 'R 20%', 'k': 4, 'eps': .02, 'clear': 8, 'error': .25}]}
        self.assertIsNone(motion_rate(record, 'R 20%'))
        self.assertEqual(motion_rate(record, 'R 20%', k=4), .25)
        self.assertIsNone(motion_rate(record, 'Hilbert'))
        record['proxy'].append(dict(record['proxy'][1]))
        with self.assertRaises(ValueError):
            motion_rate(record, 'R 20%', k=4)

    def test_cache_changes_with_fields_tracking_or_code(self):
        dataset = dict(name='fixture', native_span=10, nominal=32, domain_area=4, lo=np.zeros(2),
            sc=dict(fields=np.arange(8.).reshape(2, 2, 2), coords=np.zeros((4, 2)), tracks=[[1], [1]]))
        with tempfile.TemporaryDirectory() as directory:
            code = Path(directory) / 'renderer.py'; code.write_text('version = 1')
            first = fingerprint(dataset, [code])
            self.assertEqual(first, fingerprint(dataset, [code]))
            dataset['sc']['fields'][0, 0, 0] += 1
            self.assertNotEqual(first, fingerprint(dataset, [code]))
            dataset['sc']['fields'][0, 0, 0] -= 1
            dataset['sc']['tracks'][1] = [2]
            self.assertNotEqual(first, fingerprint(dataset, [code]))
            dataset['sc']['tracks'][1] = [1]
            dataset['lo'][0] += 1
            self.assertNotEqual(first, fingerprint(dataset, [code]))
            dataset['lo'][0] -= 1
            code.write_text('version = 2')
            self.assertNotEqual(first, fingerprint(dataset, [code]))

    def test_snapshot_rule_uses_time_only(self):
        self.assertEqual(evenly_spaced_frames(30), (0, 14, 29))
        self.assertEqual(evenly_spaced_frames(1), (0,))
        with self.assertRaises(ValueError):
            evenly_spaced_frames(0)


if __name__ == '__main__':
    unittest.main()
