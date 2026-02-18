# Web Deployment Summary

## Live URL

**https://giwojno.pl/review-analyzer/**

Hosted on OVH shared hosting (giwojno.pl), deployed via SFTP.

---

## Architecture

**Static single-page application** — pure HTML/CSS/JS with pre-computed JSON data. No backend, no database, no API keys at runtime.

| Component | Technology |
|-----------|-----------|
| Frontend | Single HTML file, vanilla CSS + JS |
| Data | 4 JSON files generated from project outputs |
| Fonts | Google Fonts (DM Sans + DM Serif Display) |
| Hosting | OVH shared hosting |
| Deployment | SFTP via `deploy.sh` (credentials in `.env`) |
| Theme | Dark editorial design, responsive layout |

---

## Features

### Dashboard
- Overview stat cards: total reviews (28,332), products (65), categories (6), average rating (4.51/5)
- Sentiment distribution bar (90.2% positive, 4.3% neutral, 5.6% negative)
- Rating distribution chart (1–5 stars)
- Reviews by category bar chart
- Average rating by category bar chart

### Categories
- 6 clickable cluster cards with review count, product count, avg rating, sentiment bar
- Click to expand full AI-generated recommendation article per cluster
- Each article includes: category overview, top 3 products, common complaints, worst product, buying recommendation

### Products
- Filterable table of all 65 products
- Filter buttons by category (Fire Tablets, Batteries & Household, E-Readers, Smart Speakers, Accessories, Media & Home)
- Columns: product name, category, review count, star rating, sentiment percentage
- Click any product to view AI-generated summary (verdict, strengths, weaknesses, best-for)
- 33 products have individual summaries (those with ≥ 20 reviews)

### Reviews
- Interactive review explorer with 500 sample reviews
- Filters: category, sentiment (positive/negative/neutral), star rating (1–5), text search
- Each review card shows: product name, star rating, sentiment badge, review text, cluster, confidence score
- Paginated (20 reviews per page)

### About
- Model details for classification (RoBERTa), clustering (TF-IDF + K-Means), and summarization (Claude Sonnet API)
- Project info: Group 4, IronHack AI Engineering Bootcamp, team members

---

## Data Pipeline

```
Project notebooks → generate_webapp.py → JSON files → index.html renders in browser
```

### Generation Script (`generate_webapp.py`)

Reads from parent directory (project root):
- `data_with_clusters.csv` — 28,332 reviews with cluster assignments
- `data_with_predictions_v2.csv` — model predictions and confidence scores
- `summaries_api.json` — AI-generated cluster and product summaries
- `product_clusters.csv` — product-level clustering info

Produces in `webapp/data/`:
- `stats.json` — dashboard overview numbers, distributions, model info
- `clusters.json` — cluster metadata + full recommendation articles
- `products.json` — all 65 products with stats and AI summaries
- `reviews_sample.json` — 500 sample reviews with predictions (diverse sampling across clusters and sentiments)

### Deployment Script (`deploy.sh`)

- Reads OVH credentials from `.env` (not committed to git)
- Validates all required config and data files exist
- Uploads via SFTP: `index.html` + `data/*.json`

---

## File Structure

```
webapp/
├── index.html              # Single-page app (~15KB)
├── generate_webapp.py      # Data generation script
├── deploy.sh               # SFTP deployment script
├── .env.example            # Credential template (committed to git)
├── .env                    # Actual credentials (git-ignored)
├── .gitignore              # Excludes .env and data/
├── README.md               # Setup instructions
└── data/                   # Generated JSON (git-ignored, reproducible)
    ├── stats.json
    ├── clusters.json
    ├── products.json
    └── reviews_sample.json
```

---

## Design

- **Theme:** Dark editorial — `#0f1117` background, blue accent (`#4f8fff`), green/red/yellow for sentiment
- **Typography:** DM Serif Display (headings) + DM Sans (body)
- **Layout:** Responsive, max-width 1200px, card-based UI
- **Interactions:** Tab navigation, clickable cards with detail panels, filterable tables, paginated review explorer
- **No framework dependencies** — pure HTML/CSS/JS, works on any hosting

---

## How to Reproduce

```bash
# 1. Generate data (from inside webapp/)
cd webapp
python generate_webapp.py

# 2. Test locally
python -m http.server 8000
# Open http://localhost:8000

# 3. Deploy
cp .env.example .env
# Edit .env with OVH credentials
./deploy.sh
```
