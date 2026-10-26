# Copilot Dashboard

Static dashboard for Copilot news and internal updates.

## Local

- Open `index.html` in a browser, or
- Use a small static server:

```bash
python3 -m http.server 8080
```

## Deploy

The GitHub Actions workflow in `.github/workflows/deploy.yml` builds the site and deploys it to GitHub Pages.

## Data source

- Microsoft 365 Copilot Blog RSS
