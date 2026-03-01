# Migration Completeness Report

Date: 2026-03-01
Branch: `work/migrazione-weebly`

## Scope

Verification of Weebly-to-Hugo migration completeness for:

- page coverage
- content fidelity
- split-content coverage (recipes/reviews)
- link/path integrity

## Results

### 1) Base page coverage

- Mirror HTML pages: **19**
- Hugo base markdown pages (`content/aburativalentina.weebly.com`): **19**
- Missing converted base pages: **0**

### 2) Source fidelity (mirror vs markdown pages)

- Checked pages: **19**
- Average similarity on `#wsite-content`: **100.00%**
- Pages below threshold: **0**

### 3) Split sections

- Recipes split: completed across `antipasti`, `primi`, `secondi`, `contorni`, `dolci`, `ricette-di-base`
- Reviews split: completed for `piemonte`, `giapponesi-in-piemonte`, `nord-italia`, `estero`; manual set present for `sud-italia`
- Remaining drafts in split content: **2** (both in Piemonte reviews)

Remaining draft files:

- `hugo-weebly-md/content/recensioni/piemonte/belvedere-pessinate.md`
- `hugo-weebly-md/content/recensioni/piemonte/la-credenza-san-maurizio-canavese.md`

Interpretation: these two entries are present in index links but the corresponding source content blocks are not present in the mirrored page body.

### 4) Link and asset integrity (markdown source)

- Relative internal `.html` links: **0**
- Relative `uploads/...` paths: **0**
- Cross-links from split content to rooted mirror pages: present (expected for a small subset of references to non-split/index pages)

### 5) Build verification

- Hugo build status: **PASS**
- Latest check: `hugo --source hugo-weebly-md`
- Pages generated: **96**

## Completeness assessment

Migration is **functionally complete** for local Hugo usage and fidelity goals.

Open residuals are limited to **2 known missing-source review entries** (`belvedere`, `credenza`), currently tracked as drafts.
