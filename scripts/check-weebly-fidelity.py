#!/usr/bin/env python3
from pathlib import Path
import re
from difflib import SequenceMatcher

SRC = Path('hugo-mirror/static/aburativalentina.weebly.com')
GEN = Path('hugo-weebly-md/public/aburativalentina.weebly.com')

# Compare by extracting #wsite-content payload from both sides.
START_RE = re.compile(r'<div\s+id="wsite-content"[^>]*>', re.IGNORECASE)
TAG_RE = re.compile(r'<div\b[^>]*>|</div>', re.IGNORECASE)


def extract_wsite_content(html: str) -> str:
    m = START_RE.search(html)
    if not m:
        return ''
    pos = m.end()
    depth = 1
    for t in TAG_RE.finditer(html, pos):
        tok = t.group(0).lower()
        if tok.startswith('<div'):
            depth += 1
        else:
            depth -= 1
            if depth == 0:
                return html[pos:t.start()]
    return ''


def normalize(s: str) -> str:
    # Keep semantic text/content order, ignore spacing noise.
    s = s.replace('\r', '')
    s = re.sub(r'\s+', ' ', s)
    return s.strip()


def main() -> int:
    files = sorted(p.name for p in SRC.glob('*.html'))
    if not files:
        print('No source html files found.')
        return 1

    rows = []
    for fn in files:
        s_path = SRC / fn
        g_path = GEN / fn
        if not g_path.exists():
            rows.append((fn, 0.0, 'missing generated page'))
            continue

        s_html = s_path.read_text(encoding='utf-8', errors='ignore')
        g_html = g_path.read_text(encoding='utf-8', errors='ignore')

        s_body = normalize(extract_wsite_content(s_html))
        g_body = normalize(extract_wsite_content(g_html))

        if not s_body or not g_body:
            rows.append((fn, 0.0, 'failed to extract #wsite-content'))
            continue

        ratio = SequenceMatcher(a=s_body, b=g_body).ratio() * 100.0
        rows.append((fn, ratio, 'ok'))

    rows_sorted = sorted(rows, key=lambda x: x[1], reverse=True)
    avg = sum(r[1] for r in rows_sorted) / len(rows_sorted)

    print('Fidelity check: source mirror vs markdown-generated pages (#wsite-content)')
    print(f'Pages: {len(rows_sorted)} | Average similarity: {avg:.2f}%')
    print('')
    for fn, ratio, note in rows_sorted:
        print(f'{ratio:6.2f}%  {fn}  [{note}]')

    return 0


if __name__ == '__main__':
    raise SystemExit(main())
