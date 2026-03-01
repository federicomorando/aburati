# Hugo Markdown Reconstruction (from Weebly mirror)

This workspace rebuilds the Weebly site as Hugo content files.

## What it contains

- Markdown pages in `content/aburativalentina.weebly.com/*.md`
- Each page keeps original body HTML inside Markdown
- Shared template in `layouts/_default/single.html`
- Static assets copied under `static/`

## Regenerate from mirror

```bash
./scripts/rebuild-weebly-markdown-site
```

This reads from:
- `hugo-mirror/static/aburativalentina.weebly.com/*.html`

And writes to:
- `hugo-weebly-md/content/aburativalentina.weebly.com/*.md`

## Run locally

```bash
hugo server --source hugo-weebly-md --port 1315
```

Open:
- `http://localhost:1315/aburativalentina.weebly.com/index.html`
