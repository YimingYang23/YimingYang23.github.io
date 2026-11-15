import unittest
from bs4 import BeautifulSoup
from sync_visitor_stats import aggregate_months, daily_rows, parse_countries

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

if __name__ == '__main__':
    unittest.main()
