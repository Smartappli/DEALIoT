# DEAL public website

Static website for presenting DEALIoT, DealHost and DealData.

## Local preview

```bash
python -m http.server 8080 --directory website
```

Open `http://localhost:8080`.

## SEO And GEO Assets

The public website ships with:

- `index.html`: canonical page, meta description, Open Graph, Twitter Card and schema.org JSON-LD.
- `robots.txt`: crawler access plus sitemap discovery.
- `sitemap.xml`: canonical GitHub Pages URL for search engines.
- `llms.txt`: concise machine-readable context for generative engines and AI agents.
- `humans.txt`: maintainer and repository reference.
- `site.webmanifest`: installable site metadata and theme colors.
- `assets/social-card.png`: primary 1200x630 social preview image for link sharing.
- `assets/social-card.svg`: editable vector source for the social preview.

`llms.txt` is included as helpful machine-readable guidance. It should not be treated as a guaranteed ranking factor.

## Deployment

The GitHub Pages workflow publishes the `website/` directory as a static artifact on pushes to `main` when website files or the workflow change.
