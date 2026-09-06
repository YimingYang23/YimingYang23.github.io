
# Yiming Yang — Academic Homepage

Static academic website hosted on GitHub Pages at https://yimingyang23.github.io/.

## Update content

- Edit biography, news, experience and service in `index.html`.
- Edit paper metadata in `assets/publications.json`, then run `python scripts/render_publications.py` to refresh the English HTML. Install the authoring dependency with `python -m pip install -r scripts/requirements.txt`. Publications remain visible without JavaScript.
- Run `python scripts/build_chinese.py` after English updates; reviewed Chinese translations live in that script. New English prose needs a corresponding Chinese translation.
- English CV: `files/Yiming_Yang_CV.pdf`. Chinese CV: `files/Yiming_Yang_CV_ZH.pdf`. Both languages are linked on both pages.
- Styles: `assets/site.css`. Search, filters, citation copying and demo controls: `assets/site.js`.
- Update the footer and `sitemap.xml` when publishing content changes.

## Preview

Run `python -m http.server 8765 --bind 127.0.0.1` and open http://127.0.0.1:8765/.
No package installation or build service is required to serve the site. DM Sans, Newsreader, Noto Sans SC and Noto Serif SC are served locally, with system-font fallbacks.

## Bright bilingual redesign

`index.html` is English; `zh.html` is Chinese. Both use a fixed light palette. Theme switching, saved theme preferences, and dark styles are removed. Repeated decorative labels and obvious playback instructions are omitted.

The demo gallery includes six surround-view scenes and two lane-view scenes (05 and 06), with keyboard-accessible tabs, scene thumbnails, native playback/full-screen controls and direct video links. Videos only load when played or selected; switching tabs pauses the previous player. The public gallery uses descriptive scene labels and generic filenames; method names, manuscript titles, submission status, and original source filenames are omitted. Original media mappings remain in private backups. Asset sources and font licenses are recorded in `assets/SOURCES.md`.

The pre-redesign site is backed up in `_private/backups/website-before-light-rebuild-20260907.zip`.

## September 2026 content update

- Replaced the former RelTopo preprint entry with its published CoPo / KDD 2026 version (same arXiv record, 2506.13553), using the supplied paper and citation.
- Added the May 2026 CSC scholarship, incoming NTU AutoMan Lab visit (October 2026–October 2027), and reviewer appointments.
- Education dates and degree names follow the provided CV, which differs from the former site's dates.
- Existing publications and preprint status are retained. The CV separately lists manuscripts under review.
- Original website ZIP and original CV files are backed up locally in `_private/backups/`. This directory is ignored by Git and excluded from GitHub Pages. A second CV backup is saved in its original folder.

The original site used styling adapted from Zeqing Yuan's academic homepage. The current design is a custom static implementation.

## September 7 publication audit

The bilingual pages contain 20 distinct publications and preprints. Google Scholar lists 22 records: the two Chinese journal papers are omitted by author request, and the earlier RelTopo record is represented by its published CoPo version. AgentsEval and FutureX were added after comparison; Reasoning to Regulate (arXiv:2607.24199) was supplied separately by the author.

The two demo categories highlight temporal modeling and VLM understanding. Embedded method-name headers are replaced with generic labels in all eight web videos and their thumbnails; the original author media remain in private backups.
