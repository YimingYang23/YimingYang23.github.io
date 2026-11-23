"""Publish only the cumulative visitor count. Never fetch tracking images."""
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import URLError
from urllib.parse import urljoin, urlparse
import json
import re
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
            if u.netloc == urlparse(BASE).netloc and re.fullmatch(r'/countries/' + COUNTER + r'/\d+/?', u.path):
                queue.append(u.path)
        if len(seen) > 30:
            raise ValueError('Unexpected country pagination')
    visitors = sum(countries.values())
    if visitors < old.get('totals', {}).get('visitors', 0):
        raise ValueError('Visitor total decreased; preserving previous snapshot')
    result = {'version': 2, 'counter': COUNTER, 'tracking_started': START,
              'updated_at': datetime.now(timezone.utc).isoformat(timespec='seconds'),
              'totals': {'visitors': visitors}}
    temp = OUTPUT.with_suffix('.tmp')
    temp.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    temp.replace(OUTPUT)
    print(f'Synced total visitors: {visitors}')

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
