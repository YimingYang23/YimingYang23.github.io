"""Read public aggregate counts, preserving calendar-month history. Never fetch tracking images."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.parse import urljoin, urlparse
import json
import re
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / 'assets/visitor-stats.json'
BASE = 'https://s05.flagcounter.com'
COUNTER = 'Ete6'
# Counter creation was Nov 16 in Singapore / Nov 15 UTC (provider's calendar).
START = '2026-11-15'

def fetch(path):
    req = Request(urljoin(BASE, path), headers={'User-Agent': 'YimingYangHomepageStats/1.0'})
    with urlopen(req, timeout=30) as response:
        day = parsedate_to_datetime(response.headers['Date']).astimezone(timezone.utc).date()
        return BeautifulSoup(response.read(), 'html.parser'), day.isoformat()

def number(text):
    if not re.fullmatch(r'[\d,]+', text.strip()):
        raise ValueError('Unexpected count: ' + text[:50])
    return int(text.replace(',', '').strip())

def daily_rows(soup, today, columns):
    rows = {}
    for tr in soup.select('tr'):
        cells = tr.find_all(['td', 'th'], recursive=False)
        if len(cells) != columns + 1:
            continue
        label = cells[0].get_text(' ', strip=True)
        if label == 'Today':
            day = today
        else:
            try:
                day = datetime.strptime(label, '%B %d, %Y').date().isoformat()
            except ValueError:
                continue
        values = [number(c.get_text(' ', strip=True)) for c in cells[1:]]
        if START <= day <= today:
            rows[day] = values
    return rows

def parse_countries(soup):
    result = {}
    for link in soup.select('a[href]'):
        match = re.fullmatch(r'/detail30/([a-z]{2})/' + COUNTER + r'/?', link['href'])
        if not match:
            continue
        cells = link.find_parent('tr').find_all('td', recursive=False)
        index = next(i for i,c in enumerate(cells) if link in c.descendants)
        result[match[1].upper()] = number(cells[index - 1].get_text(' ', strip=True))
    if not result and not re.search(r'(?:0 - 0 of 0|No flags)', soup.get_text(' ', strip=True)):
        raise ValueError('Country table unavailable; refusing to overwrite statistics')
    return result

def aggregate_months(daily):
    months = {}
    for day, row in sorted(daily.items()):
        month = months.setdefault(day[:7], {'countries': {}, 'pageviews': 0, 'visitors': 0})
        month['pageviews'] += row.get('pageviews', 0)
        month['visitors'] += row.get('visitors', 0)
        for code, count in row.get('countries', {}).items():
            month['countries'][code] = month['countries'].get(code, 0) + count
    return months

def collect():
    old = json.loads(OUTPUT.read_text(encoding='utf-8')) if OUTPUT.exists() else {}
    countries = {}
    queue = ['/countries/' + COUNTER + '/']
    seen = set()
    while queue:
        path = queue.pop(0)
        if path in seen:
            continue
        seen.add(path)
        soup, _ = fetch(path)
        countries.update(parse_countries(soup))
        for a in soup.select('a[href]'):
            u = urlparse(urljoin(BASE, a['href']))
            # Only pagination links supplied by the public country table.
            if u.netloc == urlparse(BASE).netloc and re.fullmatch(r'/countries/' + COUNTER + r'/\d+/?', u.path):
                queue.append(u.path)
        if len(seen) > 30:
            raise ValueError('Unexpected country pagination')
    overall, today = fetch('/more30/' + COUNTER + '/')
    m = re.search(r'viewed\s+([\d,]+)\s+times by\s+([\d,]+)\s+visitor', overall.get_text(' ', strip=True))
    if not m:
        raise ValueError('Pageview totals unavailable')
    totals = {'pageviews': number(m[1]), 'visitors': number(m[2])}
    if totals['visitors'] != sum(countries.values()):
        raise ValueError('Source changed during sync; retry later rather than mix snapshots')
    if totals['pageviews'] < old.get('totals', {}).get('pageviews', 0):
        raise ValueError('Counter reset or incomplete response detected')
    daily = old.get('daily', {})
    for day, values in daily_rows(overall, today, 2).items():
        daily.setdefault(day, {}).update(visitors=values[0], pageviews=values[1])
    def country_history(code):
        soup, day = fetch('/detail30/' + code.lower() + '/' + COUNTER)
        return code, daily_rows(soup, day, 1)
    missing = []
    with ThreadPoolExecutor(max_workers=4) as pool:
        for code, rows in pool.map(country_history, sorted(countries)):
            if not rows:
                missing.append(code)
            for day, values in rows.items():
                daily.setdefault(day, {}).setdefault('countries', {})[code] = values[0]
    months = aggregate_months(daily)
    current = today[:7]
    if current == START[:7]:
        # The counter was created this month. All-time totals are exactly this
        # month's totals, even during the provider's 48h history warm-up.
        months[current] = {**totals, 'countries': countries.copy(), 'complete': True}
    else:
        if missing or current not in months:
            raise ValueError('Calendar history still unavailable for: ' + ', '.join(missing))
        for month in months.values():
            month['complete'] = sum(month['countries'].values()) == month['visitors']
        if not months[current]['complete']:
            raise ValueError('Current month country totals do not match daily visitor totals')
    result = {'version': 1, 'counter': COUNTER, 'timezone': 'UTC', 'tracking_started': START,
              'updated_at': datetime.now(timezone.utc).isoformat(timespec='seconds'),
              'current_month': current, 'totals': totals, 'countries': countries,
              'months': months, 'daily': daily}
    OUTPUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f"Synced {current}: {totals['pageviews']} pageviews, {len(countries)} countries/regions")

if __name__ == '__main__':
    collect()
