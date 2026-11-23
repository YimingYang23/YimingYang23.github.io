import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from bs4 import BeautifulSoup
import sync_visitor_stats as stats


def table(count):
    return BeautifulSoup(f'<table><tr><td>China</td><td>{count}</td><td><a href="/detail30/cn/Ete6">Chart</a></td></tr><tr><td>Province</td><td>9</td><td><a href="/detail30/cn-bj/Ete6">Region</a></td></tr></table>', 'html.parser')


class VisitorStatisticsTests(unittest.TestCase):
    def test_source_failure_is_not_a_zero_total(self):
        with self.assertRaises(ValueError):
            stats.parse_countries(BeautifulSoup('<h1>Temporarily unavailable</h1>', 'html.parser'))

    def test_country_total_does_not_double_count_subregions(self):
        self.assertEqual(stats.parse_countries(table('1,234')), {'CN': 1234})

    def test_empty_counter_is_valid(self):
        self.assertEqual(stats.parse_countries(BeautifulSoup('Countries 0 - 0 of 0.', 'html.parser')), {})

    def test_publish_only_total_and_preserve_old_data_on_failure(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'counts.json'
            original = json.dumps({'version': 1, 'totals': {'visitors': 15}, 'countries': {'CN': 15}})
            output.write_text(original, encoding='utf-8')
            with patch.object(stats, 'OUTPUT', output), patch.object(stats, 'fetch', return_value=(table('14'), '2026-11-23')):
                with self.assertRaises(ValueError):
                    stats.collect()
            self.assertEqual(output.read_text(encoding='utf-8'), original)
            with patch.object(stats, 'OUTPUT', output), patch.object(stats, 'fetch', return_value=(table('16'), '2026-11-23')):
                stats.collect()
            data = json.loads(output.read_text(encoding='utf-8'))
            self.assertEqual(data['totals'], {'visitors': 16})
            self.assertEqual(data['version'], 2)
            self.assertFalse({'daily', 'months', 'countries'} & data.keys())


if __name__ == '__main__':
    unittest.main()
