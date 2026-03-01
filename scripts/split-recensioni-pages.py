#!/usr/bin/env python3
from pathlib import Path
import re
import unicodedata

ROOT = Path('hugo-weebly-md')
SRC_DIR = ROOT / 'content' / 'aburativalentina.weebly.com'
DST_ROOT = ROOT / 'content' / 'recensioni'
REPORT = Path('docs/migrazione-recensioni-report.md')

PAGES = {
    'piemonte': 'Piemonte',
    'giapponesi-in-piemonte': 'Giapponesi in Piemonte',
    'nord-italia': 'Nord Italia',
    'estero': 'Estero',
}

ANCHOR_RE = re.compile(r'<a\s+name="([^"]+)"\s*></a>', re.IGNORECASE)
H1_RE = re.compile(r'<h1>(.*?)</h1>', re.IGNORECASE | re.DOTALL)
TAG_RE = re.compile(r'<[^>]+>')
BACKLINK_RE = re.compile(r'<div\s+style="text-align:right"\s*>\s*<a\s+href="[^"]+#indice"[^>]*>.*?</a>\s*</div>', re.IGNORECASE | re.DOTALL)
INDEX_LINK_RE_TPL = r'href="{page}\.html#([a-zA-Z0-9_-]+)"'


def split_front_matter(text: str):
    if not text.startswith('---\n'):
        return '', text
    end = text.find('\n---\n', 4)
    if end == -1:
        return '', text
    return text[: end + 5], text[end + 5 :]


def html_to_text(s: str) -> str:
    s = TAG_RE.sub('', s)
    s = s.replace('&nbsp;', ' ')
    s = re.sub(r'\s+', ' ', s).strip()
    return s


def slugify(s: str) -> str:
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode('ascii')
    s = s.lower()
    s = re.sub(r'[^a-z0-9]+', '-', s)
    return s.strip('-')


def extract_city(title: str):
    if ',' in title:
        return title.split(',')[-1].strip()
    return ''


def build_post_front_matter(title: str, category: str, page: str, anchor: str, order: int, city: str) -> str:
    tags = [category]
    if city:
        tags.append(city)
    tags_yaml = ', '.join(f'"{t}"' for t in tags)
    return (
        '---\n'
        f'title: "{title.replace("\"", "\\\\\"")}"\n'
        'sezione: "Recensioni di ristoranti"\n'
        f'categoria_principale: "{category}"\n'
        f'categories: ["Recensioni di ristoranti", "{category}"]\n'
        f'tags: [{tags_yaml}]\n'
        'tipo: "recensione"\n'
        f'ordine: {order}\n'
        f'weight: {order}\n'
        f'pagina_origine: "{page}.html"\n'
        f'ancora_origine: "{anchor}"\n'
        f'body_class: "no-header-page wsite-theme-light"\n'
        '---\n\n'
    )


def main() -> int:
    DST_ROOT.mkdir(parents=True, exist_ok=True)
    report_lines = [
        '# Reviews Migration Report',
        '',
        'Semi-automatic split from Weebly pages to individual posts.',
        '',
    ]

    for page_slug, category in PAGES.items():
        src = SRC_DIR / f'{page_slug}.md'
        if not src.exists():
            report_lines.append(f'- {page_slug}: source file not found')
            continue

        _, body = split_front_matter(src.read_text(encoding='utf-8'))
        anchors = list(ANCHOR_RE.finditer(body))
        content_anchors = [m for m in anchors if m.group(1).lower() != 'indice']
        index_links = set(re.findall(INDEX_LINK_RE_TPL.format(page=re.escape(page_slug)), body))
        if not content_anchors:
            report_lines.append(f'- {page_slug}: no content anchors found')
            continue

        section_dir = DST_ROOT / page_slug
        section_dir.mkdir(parents=True, exist_ok=True)

        generated = []
        for i, m in enumerate(content_anchors, start=1):
            anchor = m.group(1)
            start = m.start()
            end = content_anchors[i].start() if i < len(content_anchors) else len(body)
            chunk = body[start:end].strip()
            chunk = BACKLINK_RE.sub('', chunk).strip()

            hm = H1_RE.search(chunk)
            title = html_to_text(hm.group(1)) if hm else anchor.replace('-', ' ').title()
            title = title.replace(' ,', ',').strip()

            chunk = re.sub(r'^\s*<a\s+name="[^"]+"\s*></a>\s*', '', chunk, flags=re.IGNORECASE)

            post_slug = slugify(title) or slugify(anchor)
            city = extract_city(title)
            fm = build_post_front_matter(title, category, page_slug, anchor, i, city)
            out = section_dir / f'{post_slug}.md'
            out.write_text(fm + chunk + '\n', encoding='utf-8')
            generated.append((anchor, out.name, title))

        index = section_dir / '_index.md'
        idx = [
            '---',
            f'title: "{category}"',
            'sezione: "Recensioni di ristoranti"',
            f'categoria_principale: "{category}"',
            f'categories: ["Recensioni di ristoranti", "{category}"]',
            f'tags: ["{category}"]',
            'body_class: "no-header-page wsite-theme-light"',
            f'pagina_origine: "{page_slug}.html"',
            '---',
            '',
            f'Page migrated from `{page_slug}.html` with split posts.',
            '',
            '## Migrated entries',
            '',
        ]
        for _, fn, title in generated:
            idx.append(f'- [{title}]({fn[:-3]})')
        idx.append('')
        index.write_text('\n'.join(idx), encoding='utf-8')

        report_lines.append(f'## {category}')
        report_lines.append('')
        report_lines.append(f'- Source page: `{page_slug}.html`')
        report_lines.append(f'- Generated posts: {len(generated)}')
        missing = sorted(a for a in index_links if a not in {g[0] for g in generated} and a.lower() != 'indice')
        if missing:
            report_lines.append(f'- Anchors present in index but not converted: {len(missing)}')
            for a in missing:
                report_lines.append(f'  - `{a}`')
        else:
            report_lines.append('- Anchors present in index but not converted: 0')
        report_lines.append('')
        for anchor, fn, title in generated:
            report_lines.append(f'  - `{anchor}` -> `{page_slug}/{fn}` ({title})')
        report_lines.append('')

    REPORT.write_text('\n'.join(report_lines), encoding='utf-8')
    print(f'Report written to {REPORT}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
