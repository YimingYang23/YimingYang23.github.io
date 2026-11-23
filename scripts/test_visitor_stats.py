import unittest
from bs4 import BeautifulSoup
from sync_visitor_stats import aggregate_months, daily_rows, parse_countries, parse_totals, recover_initial_daily

class VisitorStatisticsTests(unittest.TestCase):
    def test_calendar_month_and_year_boundaries(self):
        records = {
            '2026-11-30': {'pageviews': 8, 'visitors': 3, 'countries': {'CN': 2, 'SG': 1}},
            '2026-12-01': {'pageviews': 4, 'visitors': 1, 'countries': {'SG': 1}},
            '2026-12-31': {'pageviews': 10, 'visitors': 4, 'countries': {'CN': 4}},
            '2027-01-01': {'pageviews': 2, 'visitors': 1, 'countries': {'US': 1}},
        }
        months = aggregate_months(records)
        self.assertEqual(months['2026-12'], {'pageviews': 14, 'visitors': 5, 'countries': {'CN': 4, 'SG': 1}})
        self.assertEqual(months['2027-01']['countries'], {'US': 1})

    def test_daily_source_today_uses_provider_utc_date(self):
        soup = BeautifulSoup('<table><tr><td>Today</td><td>1</td><td>1,002</td></tr>'
                             '<tr><td>December 31, 2026</td><td>2</td><td>5</td></tr></table>', 'html.parser')
        self.assertEqual(daily_rows(soup, '2027-01-01', 2), {'2027-01-01': [1, 1002], '2026-12-31': [2, 5]})

    def test_failed_provider_page_is_not_zero_visitors(self):
        with self.assertRaises(ValueError):
            parse_countries(BeautifulSoup('<h1>Temporarily unavailable</h1>', 'html.parser'))

    def test_country_rows_ignore_paid_region_teasers(self):
        soup = BeautifulSoup('<table><tr><td>China</td><td>1,234</td><td><a href="/detail30/cn/Ete6">Chart</a></td></tr>'
                             '<tr><td>Upgrade to collect 31 regions</td></tr></table>', 'html.parser')
        self.assertEqual(parse_countries(soup), {'CN': 1234})

    def test_missing_summary_preserves_total_instead_of_summing_partial_history(self):
        old = {'updated_at': '2026-11-19T22:15:34+00:00',
               'totals': {'pageviews': 23, 'visitors': 15}, 'countries': {'CN': 7, 'US': 5, 'SG': 3},
               'daily': {'2026-11-19': {'pageviews': 5, 'visitors': 3}}}
        rows = {'2026-11-19': [3, 5], '2026-11-20': [0, 0], '2026-11-21': [0, 0],
                '2026-11-22': [0, 0], '2026-11-23': [0, 0]}
        totals, source = parse_totals(BeautifulSoup('<h1>History</h1>', 'html.parser'), rows, old['countries'], old, '2026-11-23')
        self.assertEqual(totals, {'pageviews': 23, 'visitors': 15})
        self.assertEqual(source, 'archived_total_plus_daily_history')

    def test_same_day_increment_includes_repeat_pageviews(self):
        old = {'updated_at': '2026-11-23T01:00:00+00:00', 'totals': {'visitors': 15, 'pageviews': 23},
               'countries': {'CN': 15}, 'daily': {'2026-11-23': {'visitors': 1, 'pageviews': 2}}}
        totals, _ = parse_totals(BeautifulSoup('', 'html.parser'), {'2026-11-23': [2, 8]}, {'CN': 16}, old, '2026-11-23')
        self.assertEqual(totals, {'visitors': 16, 'pageviews': 29})

    def test_missing_day_and_inconsistent_totals_fail_closed(self):
        old = {'updated_at': '2026-11-19T01:00:00+00:00', 'totals': {'visitors': 2, 'pageviews': 3},
               'daily': {'2026-11-19': {'visitors': 2, 'pageviews': 3}}}
        with self.assertRaisesRegex(ValueError, 'Incomplete daily coverage'):
            parse_totals(BeautifulSoup('', 'html.parser'), {'2026-11-19': [2, 3], '2026-11-21': [0, 0]}, {'CN': 2}, old, '2026-11-21')
        with self.assertRaisesRegex(ValueError, 'Source changed'):
            parse_totals(BeautifulSoup('', 'html.parser'), {'2026-11-19': [2, 3]}, {'CN': 3}, old, '2026-11-19')

    def test_existing_summary_format_is_still_supported(self):
        html = BeautifulSoup('This counter has been viewed <b>1,234</b> times by <b>56</b> visitors!', 'html.parser')
        totals, source = parse_totals(html, {}, {'CN': 56}, {}, '2026-11-23')
        self.assertEqual(totals, {'pageviews': 1234, 'visitors': 56})
        self.assertEqual(source, 'provider_summary')

    def test_setup_day_recovery_retains_all_month_history(self):
        old = {'tracking_started': '2026-11-15', 'updated_at': '2026-11-17T22:00:00+00:00',
               'totals': {'visitors': 12, 'pageviews': 18},
               'daily': {'2026-11-15': {'countries': {'CN': 4, 'SG': 2}},
                         '2026-11-16': {'visitors': 0, 'pageviews': 0},
                         '2026-11-17': {'visitors': 6, 'pageviews': 6}}}
        daily = recover_initial_daily(old)
        self.assertEqual(daily['2026-11-15']['pageviews'], 12)
        self.assertEqual(aggregate_months(daily)['2026-11']['pageviews'], 18)
        self.assertNotIn('pageviews', old['daily']['2026-11-15'])
        old['daily']['2026-11-15']['countries']['CN'] = 3
        self.assertNotIn('pageviews', recover_initial_daily(old)['2026-11-15'])

if __name__ == '__main__':
    unittest.main()
