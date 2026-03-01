# Backup and Branch Workflow (Weebly Migration)

This document defines how we keep:

1. `master` stable (GitHub Pages: static "domain registered" page only)
2. continuous GitHub backup for migration work
3. a clear separation between "live site" and "work in progress"

## Main rule

- `master` stays dedicated to the minimal live site.
- All Weebly migration work stays on dedicated branches (for example: `work/migrazione-weebly`).

## What not to do

- Do not commit/push migration content to `master`.
- Do not repoint the Pages workflow on `master` to migration content.

## What to do every time

1. Create/use a dedicated work branch:
   - `git switch -c work/migrazione-weebly` (first time)
   - `git switch work/migrazione-weebly` (next times)
2. Commit frequently.
3. Push the work branch to GitHub for backup:
   - `git push -u origin work/migrazione-weebly` (first push)
   - `git push` (next pushes)

## Current structure (WIP)

- Live site (`master`): `hugo/`
- Local static mirror: `hugo-mirror/`
- Markdown reconstruction: `hugo-weebly-md/`
- Mirror source files: `mirror-source/`
- Scripts: `scripts/`
- Migration notes/reports: `docs/`

## Useful operational commands

Rebuild markdown migration:

```bash
./scripts/rebuild-weebly-markdown-site
```

Run fidelity check:

```bash
./scripts/check-weebly-fidelity.py
```

Split reviews:

```bash
./scripts/split-recensioni-pages.py
```

Preview migration locally:

```bash
hugo server --source /home/federico/Codex/aburati.github.io/hugo-weebly-md --port 1315 --bind 127.0.0.1
```

## Checklist before pushing the work branch

1. Build passes (`hugo-weebly-md`).
2. No unwanted temporary files.
3. Clear commit message (migrated page/section + QA notes).

## When to publish migration online

Only after explicit approval:

1. content review completed
2. final approval
3. merge/deploy plan handled separately from this workflow
