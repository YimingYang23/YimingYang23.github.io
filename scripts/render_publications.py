"""Refresh the static publication list; then run build_chinese.py."""
from pathlib import Path
import html
import json
import re
from bs4 import BeautifulSoup

root = Path(__file__).resolve().parents[1]
publications = json.loads((root / 'assets/publications.json').read_text(encoding='utf-8'))
bib = (root / 'files/CoPo-KDD2026.bib').read_text(encoding='utf-8')
escape = html.escape
cards = []
for paper in publications:
    authors = escape(paper['authors']).replace('Yiming Yang', '<strong>Yiming Yang</strong>')
    for name in paper.get('equal_contribution', []):
        marked_name = '<strong>Yiming Yang</strong>' if name == 'Yiming Yang' else escape(name)
        authors = authors.replace(marked_name, marked_name + '<sup>*</sup>')
    author_note = '<p class="authors author-note">* Equal contribution</p>' if paper.get('equal_contribution') else ''
    title = escape(paper['title'])
    illustration = f'<img src="{escape(paper["image"])}" alt="" loading="lazy" width="480" height="280">'
    if paper['links']:
        url = escape(paper['links'][0]['url'])
        title = f'<a href="{url}">{title}</a>'
        illustration = f'<a class="paper-image" href="{url}" tabindex="-1" aria-hidden="true">{illustration}</a>'
    else:
        illustration = f'<div class="paper-image">{illustration}</div>'
    links = ''.join(
        f'<a href="{escape(link["url"])}"><svg class="icon" aria-hidden="true"><use href="assets/icons.svg#{"github" if link["label"] == "Code" else "book"}"></use></svg>{escape(link["label"])} <span aria-hidden="true">↗</span></a>'
        for link in paper['links']
    )
    citation = ''
    if paper['title'].startswith('Geometry-Guided Representations'):
        citation = (f'<details class="citation"><summary>BibTeX</summary><pre id="copo-bib">{escape(bib)}</pre>'
                    '<button type="button" id="copy-citation">Copy citation</button> '
                    '<a href="files/CoPo-KDD2026.bib" download>Download .bib</a></details>')
    cards.append(f'''<article class="paper" data-topic="{escape(paper['topic'])}" data-year="{paper['year']}">
      {illustration}
      <div class="paper-body"><div class="paper-meta"><span class="venue">{escape(paper['venue'])}</span><span>{escape(paper['topic'])}</span></div>
      <h3>{title}</h3><p class="authors">{authors}</p>{author_note}{('<div class="paper-links">' + links + '</div>') if links else ''}{citation}</div></article>''')
path = root / 'index.html'
page = BeautifulSoup(path.read_text(encoding='utf-8'), 'html.parser')
container = page.select_one('.papers')
if container is None:
    raise RuntimeError('Publication container not found; index.html was not changed.')
container.clear()
container.append(BeautifulSoup('\n'.join(cards), 'html.parser'))
page.select_one('#result-count').string = f'{len(publications)} papers'
path.write_text(str(page), encoding='utf-8')
print(f'Rendered {len(publications)} publications.')
