# Hugo Workspace

Minimal Hugo setup for GitHub Pages.

## Domain

- Canonical URL: `https://aburati.com/`
- Custom domain file: `static/CNAME`
- Jekyll bypass file: `static/.nojekyll`

## Build locally

```bash
hugo --source hugo --minify
```

Output is generated in `hugo/public`.

## Deploy via GitHub Actions

Workflow: `.github/workflows/hugo-pages.yml`
