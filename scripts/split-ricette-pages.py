#!/usr/bin/env python3
from pathlib import Path
import re
import unicodedata

ROOT = Path("hugo-weebly-md")
SRC_DIR = ROOT / "content" / "aburativalentina.weebly.com"
DST_ROOT = ROOT / "content" / "ricette"
REPORT = Path("docs/migrazione-ricette-report.md")

PAGES = {
    "antipasti": "Antipasti",
    "primi": "Primi",
    "secondi": "Secondi",
    "contorni": "Contorni",
    "dolci": "Dolci",
    "ricette-di-base": "Ricette di base",
}

NAME_ANCHOR_RE = re.compile(r'<a\s+name="([^"]+)"\s*>\s*</a>', re.IGNORECASE)
NAME_ANCHOR_OPEN_RE = re.compile(r'<a\s+name="([^"]+)"\s*>', re.IGNORECASE)
LINK_RE_TPL = r'href="{page}\.html#([a-zA-Z0-9_-]+)"'
TAG_RE = re.compile(r"<[^>]+>")
HEADING_RE = re.compile(r"<h[1-3][^>]*>(.*?)</h[1-3]>", re.IGNORECASE | re.DOTALL)
BACKLINK_RE = re.compile(
    r'<div\s+style="text-align:right"\s*>\s*<a\s+href="[^"]+#indice"[^>]*>.*?</a>\s*</div>',
    re.IGNORECASE | re.DOTALL,
)


def split_front_matter(text: str):
    if not text.startswith("---\n"):
        return "", text
    end = text.find("\n---\n", 4)
    if end == -1:
        return "", text
    return text[: end + 5], text[end + 5 :]


def html_to_text(s: str) -> str:
    s = TAG_RE.sub("", s)
    s = (
        s.replace("&nbsp;", " ")
        .replace("&amp;", "&")
        .replace("&egrave;", "è")
        .replace("&agrave;", "à")
        .replace("&ograve;", "ò")
        .replace("&ugrave;", "ù")
        .replace("&Eacute;", "É")
    )
    s = re.sub(r"\s+", " ", s).strip()
    return s


def clean_index_title(s: str) -> str:
    s = re.sub(r"\s+", " ", s).strip()
    if s.count(")") > s.count("(") and s.endswith(")"):
        s = s[:-1].rstrip()
    return s


def normalize_title_for_match(s: str) -> str:
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii")
    s = s.lower()
    s = re.sub(r"[^a-z0-9]+", "", s)
    return s


def slugify(s: str) -> str:
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii")
    s = s.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")


def normalize_anchor(a: str) -> str:
    return a.lstrip("#").strip()


def extract_index_items(body: str, page_slug: str):
    indice = re.search(r'<a\s+name="indice"\s*>\s*</a>', body, re.IGNORECASE)
    if not indice:
        return []
    start = indice.end()

    # Try to keep extraction inside the index container only.
    block_end = body.find("</div>", start)
    block = body[start:block_end] if block_end != -1 else body[start:]
    first_content_anchor = re.search(r'<a\s+name="([^"]+)"\s*>\s*</a>', block, re.IGNORECASE)
    if first_content_anchor and normalize_anchor(first_content_anchor.group(1)).lower() != "indice":
        block = block[: first_content_anchor.start()]

    items = []
    for m in re.finditer(r'<a\s+href="([^"]+)"[^>]*>(.*?)</a>', block, re.IGNORECASE | re.DOTALL):
        href, href_label = m.group(1), m.group(2)
        if href.lower().startswith("http://") or href.lower().startswith("https://"):
            continue
        label = clean_index_title(html_to_text(href_label))
        if not label:
            continue
        anchor = None
        hm = re.search(rf'(?:/aburativalentina\.weebly\.com/)?{re.escape(page_slug)}\.html#([a-zA-Z0-9_-]+)', href, re.IGNORECASE)
        if hm:
            anchor = normalize_anchor(hm.group(1))
            if anchor.lower() == "indice":
                continue
        key = (anchor or "", label)
        if key not in {(a or "", t) for a, t in items}:
            items.append((anchor, label))
    return items


def build_post_front_matter(
    title: str,
    categoria: str,
    page_slug: str,
    anchor: str,
    order: int,
    draft: bool = False,
) -> str:
    return (
        "---\n"
        f'title: "{title.replace("\"", "\\\\\"")}"\n'
        'sezione: "Le mie ricette"\n'
        f'categoria_principale: "{categoria}"\n'
        f'categories: ["Le mie ricette", "{categoria}"]\n'
        f'tags: ["{categoria}"]\n'
        'tipo: "ricetta"\n'
        f"ordine: {order}\n"
        f"weight: {order}\n"
        f'pagina_origine: "{page_slug}.html"\n'
        f'ancora_origine: "{anchor}"\n'
        'body_class: "no-header-page wsite-theme-light"\n'
        + ("draft: true\n" if draft else "")
        + "---\n\n"
    )


def main() -> int:
    DST_ROOT.mkdir(parents=True, exist_ok=True)
    report = [
        "# Recipes Migration Report",
        "",
        "Semi-automatic split from Weebly recipe pages to individual posts.",
        "",
    ]

    for page_slug, categoria in PAGES.items():
        src = SRC_DIR / f"{page_slug}.md"
        if not src.exists():
            report.append(f"- {page_slug}: source file not found")
            continue

        _, body = split_front_matter(src.read_text(encoding="utf-8"))
        index_items = extract_index_items(body, page_slug)
        if not index_items:
            report.append(f"- {page_slug}: no index items found")
            continue

        section_dir = DST_ROOT / page_slug
        section_dir.mkdir(parents=True, exist_ok=True)
        for old in section_dir.glob("*.md"):
            old.unlink()

        anchor_to_pos = {}
        for m in NAME_ANCHOR_OPEN_RE.finditer(body):
            raw = normalize_anchor(m.group(1))
            if raw.lower() == "indice":
                continue
            if raw not in anchor_to_pos:
                anchor_to_pos[raw] = m.start()

        headings = []
        for hm in HEADING_RE.finditer(body):
            title = clean_index_title(html_to_text(hm.group(1)))
            if title:
                headings.append((hm.start(), title))

        ordered_detected = [a for a, _ in index_items if a and a in anchor_to_pos]
        generated = []
        missing = []
        used_heading_positions = set()
        used_anchor_names = set()

        for i, (anchor, index_title) in enumerate(index_items, start=1):
            if not anchor or anchor not in anchor_to_pos:
                want = normalize_title_for_match(index_title)
                match_idx = None
                for j, (hpos, htitle) in enumerate(headings):
                    if hpos in used_heading_positions:
                        continue
                    got = normalize_title_for_match(htitle)
                    if want and (want in got or got in want):
                        match_idx = j
                        break

                if match_idx is not None:
                    hpos, _ = headings[match_idx]
                    next_pos = headings[match_idx + 1][0] if match_idx + 1 < len(headings) else len(body)
                    chunk = body[hpos:next_pos].strip()
                    chunk = BACKLINK_RE.sub("", chunk).strip()

                    title = index_title
                    post_slug = slugify(title) or slugify(anchor or f"entry-{i}")
                    out = section_dir / f"{post_slug}.md"
                    if out.exists():
                        out = section_dir / f"{post_slug}-{slugify(anchor or f'entry-{i}')}.md"
                    fm = build_post_front_matter(title, categoria, page_slug, anchor or f"entry-{i}", i, draft=False)
                    out.write_text(fm + chunk + "\n", encoding="utf-8")
                    generated.append((anchor or f"entry-{i}", out.name, title, False))
                    used_heading_positions.add(hpos)
                    if anchor:
                        used_anchor_names.add(anchor)
                    continue

                # Second fallback: infer anchor name from title tokens.
                if not anchor:
                    want = normalize_title_for_match(index_title)
                    inferred_anchor = None
                    for cand in anchor_to_pos.keys():
                        if cand in used_anchor_names:
                            continue
                        c = normalize_title_for_match(cand)
                        if c and want and (c in want or want in c):
                            inferred_anchor = cand
                            break
                    if inferred_anchor and inferred_anchor in anchor_to_pos:
                        start = anchor_to_pos[inferred_anchor]
                        next_starts = [anchor_to_pos[a] for a in ordered_detected if anchor_to_pos[a] > start]
                        end = min(next_starts) if next_starts else len(body)
                        chunk = body[start:end].strip()
                        chunk = BACKLINK_RE.sub("", chunk).strip()
                        chunk = re.sub(r'^\s*<a\s+name="[^"]+"\s*>', "", chunk, flags=re.IGNORECASE).strip()
                        chunk = re.sub(r'^\s*</a>\s*', "", chunk, flags=re.IGNORECASE).strip()

                        title = index_title
                        post_slug = slugify(title) or slugify(inferred_anchor)
                        out = section_dir / f"{post_slug}.md"
                        if out.exists():
                            out = section_dir / f"{post_slug}-{slugify(inferred_anchor)}.md"
                        fm = build_post_front_matter(title, categoria, page_slug, inferred_anchor, i, draft=False)
                        out.write_text(fm + chunk + "\n", encoding="utf-8")
                        generated.append((inferred_anchor, out.name, title, False))
                        used_anchor_names.add(inferred_anchor)
                        continue

                missing.append((anchor or f"entry-{i}", index_title))
                draft_slug = slugify(index_title) or slugify(anchor or f"entry-{i}")
                draft_file = section_dir / f"{draft_slug}.md"
                fm = build_post_front_matter(index_title, categoria, page_slug, anchor or f"entry-{i}", i, draft=True)
                draft_file.write_text(
                    fm + f"_Bozza automatica: contenuto non individuato nella pagina sorgente._\n",
                    encoding="utf-8",
                )
                generated.append((anchor or f"entry-{i}", draft_file.name, index_title, True))
                continue

            start = anchor_to_pos[anchor]
            next_starts = [anchor_to_pos[a] for a in ordered_detected if anchor_to_pos[a] > start]
            end = min(next_starts) if next_starts else len(body)
            chunk = body[start:end].strip()
            chunk = BACKLINK_RE.sub("", chunk).strip()
            chunk = re.sub(r'^\s*<a\s+name="[^"]+"\s*>', "", chunk, flags=re.IGNORECASE).strip()
            chunk = re.sub(r'^\s*</a>\s*', "", chunk, flags=re.IGNORECASE).strip()

            title = index_title

            post_slug = slugify(title) or slugify(anchor)
            out = section_dir / f"{post_slug}.md"
            if out.exists():
                out = section_dir / f"{post_slug}-{slugify(anchor)}.md"
            fm = build_post_front_matter(title, categoria, page_slug, anchor, i, draft=False)
            out.write_text(fm + chunk + "\n", encoding="utf-8")
            generated.append((anchor, out.name, title, False))
            used_anchor_names.add(anchor)

        idx_lines = [
            "---",
            f'title: "{categoria}"',
            'sezione: "Le mie ricette"',
            f'categoria_principale: "{categoria}"',
            f'categories: ["Le mie ricette", "{categoria}"]',
            f'tags: ["{categoria}"]',
            'body_class: "no-header-page wsite-theme-light"',
            f'pagina_origine: "{page_slug}.html"',
            "---",
            "",
            f"Page migrated from `{page_slug}.html` with split posts.",
            "",
            "## Migrated entries",
            "",
        ]
        for _, fn, title, is_draft in generated:
            suffix = " (draft)" if is_draft else ""
            idx_lines.append(f"- [{title}]({fn[:-3]}){suffix}")
        idx_lines.append("")
        (section_dir / "_index.md").write_text("\n".join(idx_lines), encoding="utf-8")

        report.append(f"## {categoria}")
        report.append("")
        report.append(f"- Source page: `{page_slug}.html`")
        report.append(f"- Index items: {len(index_items)}")
        report.append(f"- Generated posts: {len(generated)}")
        report.append(f"- Draft placeholders: {len(missing)}")
        for a, t in missing:
            report.append(f"  - `{a}` ({t})")
        report.append("")
        for anchor, fn, title, is_draft in generated:
            flag = " [draft]" if is_draft else ""
            report.append(f"  - `{anchor}` -> `{page_slug}/{fn}` ({title}){flag}")
        report.append("")

    REPORT.write_text("\n".join(report), encoding="utf-8")
    print(f"Report written to {REPORT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
