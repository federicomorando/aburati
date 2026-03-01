#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path("hugo-weebly-md")
CONTENT_ROOT = ROOT / "content"
REPORT = Path("docs/migrazione-link-normalization-report.md")

FRONT_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)
KEY_RE = re.compile(r'^([a-zA-Z_][a-zA-Z0-9_]*):\s*"(.*?)"\s*$', re.MULTILINE)
DRAFT_RE = re.compile(r"^draft:\s*true\s*$", re.MULTILINE)

# Only relative links like "foo.html" or "foo.html#bar"
REL_HTML_HREF_RE = re.compile(
    r'href="(?!(?:https?:|mailto:|/|#))([a-z0-9\-]+)\.html(?:#([a-zA-Z0-9_\-]+))?"',
    re.IGNORECASE,
)
REL_UPLOAD_RE = re.compile(r'((?:src|href))="uploads/([^"]+)"', re.IGNORECASE)


def parse_front_matter(text: str):
    m = FRONT_RE.match(text)
    if not m:
        return {}
    raw = m.group(1)
    data = {k: v for k, v in KEY_RE.findall(raw)}
    data["draft"] = bool(DRAFT_RE.search(raw))
    return data


def content_file_to_url(path: Path) -> str:
    rel = path.relative_to(CONTENT_ROOT).as_posix()
    if rel.endswith("/_index.md"):
        return "/" + rel[: -len("_index.md")] + "index.html"
    if rel.endswith(".md"):
        return "/" + rel[:-3] + ".html"
    return "/" + rel


def build_split_map():
    mapping = {}
    # Build from all split posts that preserve original page+anchor metadata.
    for p in CONTENT_ROOT.rglob("*.md"):
        rel = p.relative_to(CONTENT_ROOT).as_posix()
        if not (rel.startswith("ricette/") or rel.startswith("recensioni/")):
            continue
        fm = parse_front_matter(p.read_text(encoding="utf-8"))
        page = fm.get("pagina_origine", "").strip()
        anchor = fm.get("ancora_origine", "").strip()
        if not page.endswith(".html") or not anchor or fm.get("draft"):
            continue
        key = (page[:-5], anchor)
        mapping[key] = content_file_to_url(p)
    return mapping


def normalize_file(path: Path, split_map: dict):
    text = path.read_text(encoding="utf-8")
    original = text

    split_hits = 0
    fallback_hits = 0
    upload_hits = 0

    def repl_href(m):
        nonlocal split_hits, fallback_hits
        page = m.group(1)
        anchor = m.group(2)
        if anchor and (page, anchor) in split_map:
            split_hits += 1
            return f'href="{split_map[(page, anchor)]}"'
        fallback_hits += 1
        url = f"/aburativalentina.weebly.com/{page}.html"
        if anchor:
            url += f"#{anchor}"
        return f'href="{url}"'

    text = REL_HTML_HREF_RE.sub(repl_href, text)

    def repl_upload(m):
        nonlocal upload_hits
        upload_hits += 1
        return f'{m.group(1)}="/aburativalentina.weebly.com/uploads/{m.group(2)}"'

    text = REL_UPLOAD_RE.sub(repl_upload, text)

    changed = text != original
    if changed:
        path.write_text(text, encoding="utf-8")
    return changed, split_hits, fallback_hits, upload_hits


def main() -> int:
    split_map = build_split_map()
    changed_files = 0
    total_split = 0
    total_fallback = 0
    total_upload = 0

    for p in CONTENT_ROOT.rglob("*.md"):
        changed, split_hits, fallback_hits, upload_hits = normalize_file(p, split_map)
        if changed:
            changed_files += 1
        total_split += split_hits
        total_fallback += fallback_hits
        total_upload += upload_hits

    lines = [
        "# Link Normalization Report",
        "",
        "Normalize relative internal links and upload paths for Hugo.",
        "",
        f"- Files changed: {changed_files}",
        f"- Internal links rewritten to split posts: {total_split}",
        f"- Internal links rewritten to rooted mirror pages: {total_fallback}",
        f"- Upload paths rewritten to rooted paths: {total_upload}",
        "",
        "## Notes",
        "",
        "- Links matching migrated split items (`pagina_origine` + `ancora_origine`) are redirected to split post URLs.",
        "- Other relative `.html` links are rewritten to rooted mirror URLs under `/aburativalentina.weebly.com/`.",
        "- Relative `uploads/...` links are rewritten to `/aburativalentina.weebly.com/uploads/...`.",
        "",
    ]
    REPORT.write_text("\n".join(lines), encoding="utf-8")
    print(f"Report written to {REPORT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
