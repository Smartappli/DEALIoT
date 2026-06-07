# DEAL public website

Static Progressive Web App for presenting DEALIoT, DealHost and DealData.

## Local preview

```bash
python -m http.server 8080 --directory website
```

Open `http://localhost:8080`.

## Languages

- Default language: English US at `/`.
- French version: `/fr/`.
- `sitemap.xml` and page headers expose `hreflang` alternates.

## PWA Assets

The website ships with:

- `site.webmanifest`: app identity, icons, shortcuts, language and display mode.
- `sw.js`: service worker with static asset caching and offline fallback.
- `offline.html`: offline fallback for failed navigation requests.
- `assets/icon-192.png`: install icon.
- `assets/icon-512.png`: high-resolution install icon.
- `assets/icon-maskable-512.png`: maskable install icon.

## SEO And GEO Assets

The public website ships with:

- `index.html`: default English canonical page, Open Graph, Twitter Card and schema.org JSON-LD.
- `fr/index.html`: French localized page with its own canonical and JSON-LD.
- `robots.txt`: crawler access plus sitemap discovery.
- `sitemap.xml`: canonical GitHub Pages URLs and language alternates.
- `llms.txt`: concise machine-readable context for generative engines and AI agents.
- `humans.txt`: maintainer and repository reference.
- `assets/social-card.png`: primary 1200x630 social preview image for link sharing.
- `assets/social-card.svg`: editable vector source for the social preview.

`llms.txt` is included as helpful machine-readable guidance. It should not be treated as a guaranteed ranking factor.

## Deployment

The GitHub Pages workflow publishes the `website/` directory as a static artifact on pushes to `main` when website files or the workflow change.
