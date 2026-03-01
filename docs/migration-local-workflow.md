# Local Migration Workflow (Weebly -> Hugo)

This repository uses a dual-track workflow:

- `master`: production GitHub Pages branch (currently static notice only).
- `work/migrazione-weebly`: migration workspace branch for mirrored/imported content.

## Publishing policy

- Migration work is committed and pushed to `work/migrazione-weebly` for backup/history.
- No migration content is merged to `master` until explicitly approved.
- `master` must keep the minimal "domain registered" page for now.

## Local rebuild pipeline

From repository root:

```bash
./scripts/update-weebly-mirror
./scripts/extract-weebly-to-hugo-md.py
./scripts/split-recensioni-pages.py
./scripts/split-ricette-pages.py
./scripts/normalize-hugo-links.py
```

## Local preview

Bind locally for safety:

```bash
hugo server --source hugo-weebly-md --bind 127.0.0.1 --baseURL http://127.0.0.1:1314/ --appendPort
```

## Notes on split quality

- `scripts/split-recensioni-pages.py` and `scripts/split-ricette-pages.py` generate per-item Markdown pages under:
  - `hugo-weebly-md/content/recensioni/`
  - `hugo-weebly-md/content/ricette/`
- If an item exists in the Weebly index but no matching source anchor is found, a `draft: true` placeholder is generated.
- Check migration QA reports:
  - `docs/migrazione-recensioni-report.md`
  - `docs/migrazione-ricette-report.md`
