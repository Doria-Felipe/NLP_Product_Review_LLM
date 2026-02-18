# Data Exploration Summary

## Dataset

- **Source:** Datafiniti Amazon Consumer Reviews (Kaggle)
- **File:** `Datafiniti_Amazon_Consumer_Reviews_of_Amazon_Products_May19.csv`
- **Size:** 28,332 reviews, 24 columns
- **Products:** 65 unique Amazon-branded products
- **Review period:** 2009–2019

---

## Column Overview

### Retained Columns (14)

| Column | Type | Nulls | Notes |
|--------|------|-------|-------|
| `name` | string | 0 | Product name (65 unique) |
| `brand` | string | 0 | All "Amazon" or "AmazonBasics" |
| `manufacturer` | string | low | Amazon or similar |
| `categories` | string | 0 | Multi-label comma-separated (rich, useful for clustering) |
| `primaryCategories` | string | 0 | 9 unique values, dominated by Electronics (49.4%) and Health & Beauty (42.6%) |
| `reviews.text` | string | 0 | Review body text |
| `reviews.title` | string | low | Review title/headline |
| `reviews.rating` | float | 0 | 1–5 star rating |
| `reviews.date` | string | some | Date of review |
| `reviews.username` | string | some | Reviewer username |
| `reviews.numHelpful` | float | some | Helpfulness votes |
| `reviews.doRecommend` | bool | some | Would recommend (True/False) |
| `reviews.dateAdded` | string | some | Date review was added to dataset |
| `sentiment` | string | 0 | **Derived:** Positive/Neutral/Negative from star rating |

### Dropped Columns (10)

| Column | Reason |
|--------|--------|
| `reviews.didPurchase` | 99.97% null |
| `reviews.id` | 99.86% null |
| `reviews.userCity` | Mostly null, not useful |
| `reviews.userProvince` | Mostly null, not useful |
| `id` | Internal ID, no predictive value |
| `asins` | Amazon product ID, redundant with name |
| `keys` | Internal key, no predictive value |
| `dateAdded` | Dataset metadata, not review data |
| `dateSeen` | Dataset metadata, not review data |
| `sourceURLs` | URL metadata, not useful |

---

## Key Statistics

### Review Text

| Metric | Value |
|--------|-------|
| Median word count | 17 words |
| Median character count | 87 characters |
| Mean word count | ~40 words |
| Very short reviews dominate | "good", "great", "ok" are common |

### Ratings Distribution

| Rating | Count | Percentage |
|--------|-------|------------|
| 5 stars | ~18,000 | 63.5% |
| 4 stars | ~7,500 | 26.5% |
| 3 stars | ~1,200 | 4.2% |
| 2 stars | ~800 | 2.8% |
| 1 star | ~800 | 2.8% |
| **Mean rating** | **4.51/5** | |

### Sentiment Classes (derived from ratings)

| Sentiment | Star Rating | Count | Percentage |
|-----------|------------|-------|------------|
| Positive | 4–5 | 25,545 | 90.2% |
| Negative | 1–2 | 1,581 | 5.6% |
| Neutral | 3 | 1,206 | 4.3% |

**Heavily imbalanced** — major challenge for classification.

---

## Duplicate Analysis

| Type | Count | Decision |
|------|-------|----------|
| Full row duplicates | 0 | N/A |
| Duplicate review texts | 10,164 (35.87%) | **Keep** — legitimate short generic reviews ("good", "great", "ok") posted by different users across different products |

---

## Product Distribution

| Metric | Value |
|--------|-------|
| Total unique products | 65 |
| Median reviews per product | 21 |
| Max reviews per product | 8,343 (AmazonBasics AAA Batteries) |
| Bottom 25% products | ≤5 reviews each |
| Highly skewed | Top 5 products account for majority of reviews |

### Top Products by Review Count

| Product | Reviews |
|---------|---------|
| AmazonBasics AAA Performance Alkaline Batteries (36 Count) | 8,343 |
| AmazonBasics AA Performance Alkaline Batteries (48 Count) | 3,728 |
| Fire HD 8 Tablet with Alexa, 8" HD Display, 16 GB, Tangerine | 2,443 |
| All-New Fire HD 8 Tablet, 8" HD Display, Wi-Fi, 16 GB | 2,370 |
| Fire Kids Edition Tablet, 7" Display, Wi-Fi, 16 GB, Pink | 1,676 |

### Natural Product Groupings (visible before clustering)

1. **Batteries** — AmazonBasics AA/AAA (12,071 reviews, 42.6%)
2. **Fire Tablets** — HD 8, Fire 7 in various colors
3. **Kids Tablets** — Fire Kids Edition in various colors
4. **E-Readers** — Kindle Voyage, Kindle E-reader, Kindle Oasis
5. **Smart Speakers** — Amazon Tap, Echo

---

## Categories Column Analysis

- `primaryCategories`: 9 values but dominated by Electronics (49.4%) and Health & Beauty (42.6%) — not granular enough for clustering
- `categories`: Rich multi-label comma-separated data with dozens of unique labels — useful for clustering
- Unique individual category labels: 100+
- Top labels: "Fire Tablets", "Electronics", "Batteries", "Kindle E-readers", etc.

---

## Decisions Made During Exploration

| # | Decision | Reasoning |
|---|----------|-----------|
| 1 | Keep duplicate review texts | They are legitimate short reviews from different users/products (0 full row duplicates) |
| 2 | Drop 10 columns | Either >99% null or metadata with no predictive value |
| 3 | Sentiment mapping: 1-2→Negative, 3→Neutral, 4-5→Positive | Standard approach, aligns with common sentiment analysis practice |
| 4 | Use `categories` column for clustering (not `primaryCategories`) | Much richer, multi-label data vs only 9 generic categories |
| 5 | No text preprocessing for transformers | Transformers handle raw text; heavy preprocessing can hurt performance |
| 6 | No minimum review length filter | Even single-word reviews ("good", "great") carry sentiment signal |

---

## Files Produced

| File | Description |
|------|-------------|
| `01_data_exploration.ipynb` | Comprehensive exploration notebook with all analysis and charts |
| `data_cleaned.csv` | Cleaned dataset ready for modeling (sentiment column added, 10 columns dropped) |
