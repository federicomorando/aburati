#!/usr/bin/env python3
import re
from pathlib import Path

SRC_DIR = Path('hugo-mirror/static/aburativalentina.weebly.com')
DST_DIR = Path('hugo-weebly-md/content/aburativalentina.weebly.com')

TITLE_RE = re.compile(r'<title>(.*?)</title>', re.IGNORECASE | re.DOTALL)
BODY_CLASS_RE = re.compile(r'<body\s+class="([^"]*)"', re.IGNORECASE)
WSITE_CONTENT_START_RE = re.compile(r'<div\s+id="wsite-content"[^>]*>', re.IGNORECASE)


def extract_wsite_content(html: str) -> str:
    m = WSITE_CONTENT_START_RE.search(html)
    if not m:
        raise ValueError('Cannot find #wsite-content start tag')

    pos = m.end()
    depth = 1
    tag_re = re.compile(r'<div\b[^>]*>|</div>', re.IGNORECASE)

    for t in tag_re.finditer(html, pos):
        token = t.group(0).lower()
        if token.startswith('<div'):
            depth += 1
        else:
            depth -= 1
            if depth == 0:
                return html[pos:t.start()].strip()

    raise ValueError('Cannot find matching closing </div> for #wsite-content')


def clean_title(title: str) -> str:
    t = re.sub(r'\s+', ' ', title).strip()
    t = re.sub(r'\s*-\s*Valentina Aburati\s*$', '', t, flags=re.IGNORECASE)
    return t


def write_md(dst: Path, title: str, body_class: str, source_name: str, content_html: str) -> None:
    md = (
        '---\n'
        f'title: "{title.replace("\"", "\\\\\"")}"\n'
        f'body_class: "{body_class.replace("\"", "\\\\\"")}"\n'
        f'source_file: "{source_name}"\n'
        '---\n\n'
        f'{content_html}\n'
    )
    dst.write_text(md, encoding='utf-8')


def main() -> None:
    DST_DIR.mkdir(parents=True, exist_ok=True)
    files = sorted(SRC_DIR.glob('*.html'))

    for src in files:
        html = src.read_text(encoding='utf-8', errors='ignore')

        tm = TITLE_RE.search(html)
        title = clean_title(tm.group(1)) if tm else src.stem

        bm = BODY_CLASS_RE.search(html)
        body_class = bm.group(1).strip() if bm else ''

        content_html = extract_wsite_content(html)

        dst = DST_DIR / f'{src.stem}.md'
        write_md(dst, title, body_class, src.name, content_html)

    print(f'Converted {len(files)} pages into {DST_DIR}')


if __name__ == '__main__':
    main()
