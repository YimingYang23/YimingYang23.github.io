
# Yiming Yang — Academic Homepage

Static academic website hosted on GitHub Pages at https://yimingyang23.github.io/.

## Update content

- Edit biography, news, experience and service in `index.html`.
- Edit paper metadata in `assets/publications.json`, then run `python scripts/render_publications.py` to refresh the HTML. This uses only Python's standard library. Publications remain visible without JavaScript.
- Replace `files/Yiming_Yang_CV.pdf` to update all CV download buttons.
- Styles: `assets/site.css`. Search, filters, citation copying and theme switching: `assets/site.js`.
- Update the footer and `sitemap.xml` when publishing content changes.

## Preview

Run `python -m http.server 8765 --bind 127.0.0.1` and open http://127.0.0.1:8765/.
No package installation or build service is required. Web fonts are optional; local font fallbacks are supplied.

## September 2026 content update

- Replaced the former RelTopo preprint entry with its published CoPo / KDD 2026 version (same arXiv record, 2506.13553), using the supplied paper and citation.
- Added the May 2026 CSC scholarship, incoming NTU AutoMan Lab visit (October 2026–October 2027), and reviewer appointments.
- Education dates and degree names follow the provided CV, which differs from the former site's dates.
- Existing publications and preprint status are retained. The CV separately lists manuscripts under review.
- Original website ZIP and original CV files are backed up locally in `_private/backups/`. This directory is ignored by Git and excluded from GitHub Pages. A second CV backup is saved in its original folder.

The original site used styling adapted from Zeqing Yuan's academic homepage. The current design is a custom static implementation.
