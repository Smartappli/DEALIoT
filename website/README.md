# DEAL Website

Static marketing website for DEALIoT, DealHost and DealData.

## Local Preview

```bash
python -m http.server 8080 --directory website
```

Open `http://localhost:8080`.

## Deployment

The GitHub Pages workflow publishes the `website/` directory as a static artifact on pushes to `main` when website files or the workflow change.
