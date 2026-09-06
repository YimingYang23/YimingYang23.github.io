"""Refresh the static, searchable publication list. Python 3; no dependencies."""
from pathlib import Path
import html
import json
import re

root = Path(__file__).resolve().parents[1]
publications = json.loads((root / 'assets/publications.json').read_text(encoding='utf-8'))
bib = (root / 'files/CoPo-KDD2026.bib').read_text(encoding='utf-8')
escape = html.escape
cards = []
for paper in publications:
    authors = escape(paper['authors']).replace('Yiming Yang', '<strong>Yiming Yang</strong>')
    links = ''.join(
        f'<a href="{escape(link["url"])}">{escape(link["label"])} <span aria-hidden="true">↗</span></a>'
        for link in paper['links']
    )
    citation = ''
    if paper['title'].startswith('Geometry-Guided Representations'):
        citation = (f'<details class="citation"><summary>BibTeX</summary><pre id="copo-bib">{escape(bib)}</pre>'
                    '<button type="button" id="copy-citation">Copy citation</button> '
                    '<a href="files/CoPo-KDD2026.bib" download>Download .bib</a></details>')
    cards.append(f'''<article class="paper" data-topic="{escape(paper['topic'])}" data-year="{paper['year']}">
      <a class="paper-image" href="{escape(paper['links'][0]['url'])}" tabindex="-1" aria-hidden="true"><img src="{escape(paper['image'])}" alt="" loading="lazy" width="480" height="280"></a>
      <div class="paper-body"><div class="paper-meta"><span class="venue">{escape(paper['venue'])}</span><span>{escape(paper['topic'])}</span></div>
      <h3><a href="{escape(paper['links'][0]['url'])}">{escape(paper['title'])}</a></h3><p class="authors">{authors}</p><div class="paper-links">{links}</div>{citation}</div></article>''')
path = root / 'index.html'
page = path.read_text(encoding='utf-8')
page, count = re.subn(r'(<div class="papers">).*?(</div><p id="empty-results")',
                     lambda match: match[1] + '\n'.join(cards) + match[2], page, count=1, flags=re.S)
if count != 1:
    raise RuntimeError('Publication container not found; index.html was not changed.')
page = re.sub(r'(<p id="result-count"[^>]*>).*?(</p>)',
              lambda m: m[1] + f'{len(publications)} publications & preprints' + m[2], page, count=1)
path.write_text(page, encoding='utf-8')
print(f'Rendered {len(publications)} publications.')
