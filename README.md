# Talsu Kultūras centrs events

Static site generator that fetches events from `bilesuparadize.lv` using Playwright (stealth) and renders a mobile-friendly events page with remaining ticket counts.

## Local usage

1. Install dependencies:
   - `npm install`
   - `npx playwright install chromium`
2. Generate the static site:
   - `npm run generate`
3. Open `dist/index.html` in a browser.

## Data mapping

- `id` -> event id (used in `https://www.bilesuparadize.lv/lv/event/{id}`)
- `performance_titles.lv` -> title
- `date_time` -> event date/time
- `small_image_url.lv` (fallback `poster_image_url.lv`) -> image
- `price_groups[].count` -> remaining tickets (summed)

## Automation

The GitHub Actions workflow in `.github/workflows/generate.yml` runs every 6 hours (and on manual dispatch), generates `dist/`, and uploads the site as a workflow artifact. You can adapt it to deploy to GitHub Pages, S3, or another static host.
`