# Weebly Mirror Workspace

This Hugo workspace serves a static mirror of:
- `https://aburativalentina.weebly.com/`

The mirrored files are stored under `hugo-mirror/static/` preserving host folders
(e.g. `aburativalentina.weebly.com/`, `cdn2.editmysite.com/`, ...).

## Local preview

```bash
hugo server --source hugo-mirror --port 1314
```

Open:
- `http://localhost:1314/` (redirects to mirror home)
- `http://localhost:1314/aburativalentina.weebly.com/index.html`

## Refresh the mirror

```bash
./scripts/update-weebly-mirror
```

This updates `mirror-source/` and syncs it to `hugo-mirror/static/`.

## Important

This workspace is separate from `hugo/`, which currently contains the
minimal `aburati.com - dominio registrato` page used for GitHub Pages.
