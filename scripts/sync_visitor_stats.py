"""Read public aggregate counts, preserving calendar-month history. Never fetch tracking images."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone, timedelta, date
from email.utils import parsedate_to_datetime
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import URLError
from urllib.parse import urljoin, urlparse
import json
import re
import copy
import time
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

def date_range(first, last):
    start, stop = date.fromisoformat(first), date.fromisoformat(last)
    return [(start + timedelta(days=i)).isoformat() for i in range((stop - start).days + 1)]

def recover_initial_daily(old):
    """Recover a single omitted setup day only when archived totals prove it."""
    daily = copy.deepcopy(old.get('daily', {}))
    if not old.get('updated_at') or not old.get('totals'):
        return daily
    end = datetime.fromisoformat(old['updated_at']).astimezone(timezone.utc).date().isoformat()
    days = date_range(old.get('tracking_started', START), end)
    missing = [d for d in days if not {'visitors', 'pageviews'} <= daily.get(d, {}).keys()]
    if len(missing) == 1:
        target = daily.get(missing[0], {})
        known = [daily[d] for d in days if d != missing[0]]
        visitors = old['totals']['visitors'] - sum(row['visitors'] for row in known)
        views = old['totals']['pageviews'] - sum(row['pageviews'] for row in known)
        # Country history independently records this omitted setup day's visits.
        if 'countries' in target and sum(target['countries'].values()) == visitors and 0 <= visitors <= views:
            target.update(visitors=visitors, pageviews=views)
            daily[missing[0]] = target
    return daily

def parse_totals(overall, rows, countries, old, today):
    text = overall.get_text(' ', strip=True)
    match = re.search(r'viewed\s+([\d,]+)\s+times by\s+([\d,]+)\s+visitor', text)
    if match:
        totals = {'pageviews': number(match[1]), 'visitors': number(match[2])}
        source = 'provider_summary'
    else:
        if not old.get('updated_at') or not old.get('totals'):
            raise ValueError('Cumulative summary absent and no trusted previous snapshot')
        anchor = datetime.fromisoformat(old['updated_at']).astimezone(timezone.utc).date().isoformat()
        previous = old.get('daily', {}).get(anchor, {})
        if anchor > today or not {'visitors', 'pageviews'} <= previous.keys():
            raise ValueError('Previous snapshot has no usable UTC anchor-day counts')
        days = date_range(anchor, today)
        if not days or any(day not in rows for day in days):
            raise ValueError('Incomplete daily coverage since last snapshot; totals cannot be reconstructed')
        increments = [sum(rows[d][i] for d in days) - previous[key]
                      for i, key in enumerate(['visitors', 'pageviews'])]
        if any(n < 0 for n in increments):
            raise ValueError('Daily counts decreased since last snapshot')
        totals = {'visitors': old['totals']['visitors'] + increments[0],
                  'pageviews': old['totals']['pageviews'] + increments[1]}
        source = 'archived_total_plus_daily_history'
    if totals['visitors'] != sum(countries.values()):
        raise ValueError('Source changed during sync; retry later rather than mix snapshots')
    if totals['pageviews'] < old.get('totals', {}).get('pageviews', 0) or totals['pageviews'] < totals['visitors']:
        raise ValueError('Counter reset or incomplete response detected')
    for code, previous in old.get('countries', {}).items():
        if countries.get(code, 0) < previous:
            raise ValueError('Country total decreased; preserving previous snapshot')
    return totals, source

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
    rows = daily_rows(overall, today, 2)
    totals, totals_source = parse_totals(overall, rows, countries, old, today)
    daily = recover_initial_daily(old)
    for day, values in rows.items():
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
              'current_month': current, 'totals': totals, 'totals_source': totals_source, 'countries': countries,
              'months': months, 'daily': daily}
    temp = OUTPUT.with_suffix('.tmp')
    temp.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    temp.replace(OUTPUT)
    print(f"Synced {current}: {totals['pageviews']} pageviews, {len(countries)} countries/regions")

if __name__ == '__main__':
    for attempt in range(3):
        try:
            collect()
            break
        except (ValueError, URLError, TimeoutError) as error:
            if attempt == 2:
                raise
            print(f'Sync attempt {attempt + 1} failed: {error}; retrying without replacing data.')
            time.sleep(3 * (attempt + 1))
