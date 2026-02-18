# Clustering Results Summary

## Objective

Group 65 Amazon products into 4–6 meaningful meta-categories to enable per-category review summarization and analysis.

---

## Method

**TF-IDF Vectorization → K-Means Clustering**

1. **Aggregated to product level** — 65 rows (one per product), not 28K review rows
2. **Combined text feature** per product: `product_name + cleaned_category_labels`
3. **Category cleaning:** Parsed comma-separated `categories` column, removed noise labels ("Robot Check", "Frys", "Back to College", etc.), deduplicated
4. **TF-IDF:** Unigrams and bigrams, max 200 features, English stop words removed
5. **K-Means:** n_init=20 for stable centroids

---

## Cluster Selection

Tested K=2 to K=10 using elbow method and silhouette analysis.

| K | Inertia | Silhouette |
|---|---------|------------|
| 2 | 45.52 | 0.1543 |
| 3 | 40.21 | 0.1649 |
| 4 | 36.07 | 0.1963 |
| **5** | **33.05** | **0.2190** |
| **6** | **30.31** | **0.2364** |
| 7 | 28.16 | 0.2526 |
| 8 | 25.80 | 0.2531 |
| 9 | 23.98 | 0.2770 |
| 10 | 22.86 | 0.2479 |

- Best overall silhouette: K=9 (0.2770)
- **Chosen: K=6** — best silhouette within the required 4–6 range (0.2364)
- Silhouette scores are modest overall due to overlapping category labels across products (e.g., Fire Tablets and Kids Tablets share many terms like "tablets", "computers", "electronics")

---

## Cluster Results (K=6)

| Cluster | Products | Reviews | Avg Rating | % Positive | % Neutral | % Negative |
|---------|----------|---------|------------|------------|-----------|------------|
| **Fire Tablets** | 20 | 14,396 | 4.56 | 93.2% | 4.1% | 2.6% |
| **Batteries & Household** | 7 | 12,086 | 4.45 | 86.1% | 4.4% | 9.5% |
| **E-Readers** | 10 | 1,049 | 4.66 | 95.2% | 3.2% | 1.5% |
| **Smart Speakers** | 9 | 632 | 4.54 | 91.9% | 4.4% | 3.6% |
| **Accessories** | 11 | 138 | 4.31 | 82.6% | 9.4% | 8.0% |
| **Media & Home** | 8 | 31 | 4.39 | 83.9% | 3.2% | 12.9% |

---

## Cluster Details

### Cluster 0: Fire Tablets (20 products, 14,396 reviews)
**Top TF-IDF terms:** tablets, hd, display, computers, gb

Key products:
- Fire HD 8 Tablet (16GB, Tangerine) — 2,443 reviews
- All-New Fire HD 8 Tablet (16GB, Black) — 2,370 reviews
- Fire Kids Edition (Pink/Blue/Green) — 1,676 / 1,425 / 1,212 reviews
- Fire Tablet 7" (16GB, Black) — 1,024 reviews
- Various HD 8 and Fire 7 color variants

Includes both adult and kids tablet variants across multiple generations and colors.

### Cluster 1: E-Readers (10 products, 1,049 reviews)
**Top TF-IDF terms:** readers, kindle, kindle readers, resolution display, 300

Key products:
- Kindle Voyage (300 ppi) — 505 reviews
- Kindle E-reader (White, 6") — 287 reviews
- Kindle Oasis (Walnut/Black/Merlot) — 62/55/54 reviews
- All-New Kindle Oasis (Waterproof) — 22/7/4 reviews
- All-New Kindle E-reader (Black) — 17 reviews

Highest average rating across all clusters (4.66) and lowest negative rate (1.5%).

### Cluster 2: Smart Speakers (9 products, 632 reviews)
**Top TF-IDF terms:** smart, home, speakers, echo, assistants

Key products:
- Amazon Tap — 601 reviews (dominates this cluster)
- Amazon Echo (1st gen, certified) — 13 reviews
- Certified Refurbished Echo — 7 reviews
- Echo (2nd gen), Echo Spot, Echo Show, Echo Dot — 1–3 reviews each

Heavily dominated by Amazon Tap reviews.

### Cluster 3: Batteries & Household (7 products, 12,086 reviews)
**Top TF-IDF terms:** supplies, pet, batteries, household, health

Key products:
- AmazonBasics AAA Alkaline Batteries (36 Count) — 8,343 reviews
- AmazonBasics AA Alkaline Batteries (48 Count) — 3,728 reviews
- Expanding Accordion File Folder — 9 reviews
- Dog Crate (Medium/Large) — 2/1 reviews
- Cat Litter Box — 2 reviews
- Pet Kennel Travel Crate — 1 review

99.9% of reviews are batteries. Non-battery products (pet/office supplies) grouped here due to shared "Health & Household" Amazon categories — minimal impact with only 15 reviews combined.

### Cluster 4: Accessories (11 products, 138 reviews)
**Top TF-IDF terms:** accessories, cables, power, laptop, adapters, usb

Key products:
- Amazon 9W PowerFast USB Charger — 39 reviews
- AmazonBasics Laptop Backpack (17") — 25 reviews
- AmazonBasics Laptop and Tablet Bag (15.6") — 21 reviews
- AmazonBasics Laptop Stand — 12 reviews
- Kindle Charger/Power Adapter — 9/5/4 reviews
- Bluetooth Keyboard, Laptop Sleeve, USB Cable — 6 reviews each

Lowest average rating (4.31) and highest Neutral rate (9.4%) among major clusters.

### Cluster 5: Media & Home (8 products, 31 reviews)
**Top TF-IDF terms:** tv, video, kitchen, media, streaming

Key products:
- AmazonBasics External Hard Drive Case — 6 reviews
- Fire TV Stick Pair Kit — 6 reviews
- Certified Refurbished Fire TV — 5 reviews
- AmazonBasics Speaker Wire (16-Gauge) — 5 reviews
- AmazonBasics CD/DVD Binder — 4 reviews
- Amazon Fire TV Gaming Edition — 3 reviews
- Nespresso Pod Storage Drawer — 1 review
- Silicone Hot Handle Cover — 1 review

Smallest cluster by far. Highest negative rate (12.9%) but very small sample size (31 reviews). Catch-all for miscellaneous products that don't fit elsewhere.

---

## Key Observations

1. **Fire Tablets** and **Batteries & Household** dominate with 93% of all reviews combined (26,482 out of 28,332)
2. **E-Readers** have the highest customer satisfaction — 4.66 avg rating, 95.2% positive, only 1.5% negative
3. **Batteries & Household** has the highest negative rate among major clusters (9.5%) — likely driven by battery performance complaints
4. **Accessories** and **Media & Home** are small clusters (138 and 31 reviews) — the summarization model will have limited material for these
5. The **Batteries & Household** cluster includes a few non-battery products (pet crates, file organizer) grouped by shared Amazon category labels — these contribute only 15 reviews total so the impact is negligible
6. **Smart Speakers** cluster is dominated by Amazon Tap (601 of 632 reviews) — cluster characteristics essentially reflect Tap reviews

---

## Visualization

- **PCA 2D scatter plot** shows clear separation between Batteries, Tablets, and E-Readers clusters
- Smart Speakers and Accessories overlap somewhat in PCA space due to shared "Electronics" category labels
- Point sizes proportional to review count highlight the dominance of batteries and tablets

---

## Files Produced

| File | Description |
|------|-------------|
| `03_clustering.ipynb` | Full clustering notebook with analysis and visualizations |
| `data_with_clusters.csv` | Full review dataset (28,332 rows) with `cluster` and `cluster_name` columns |
| `product_clusters.csv` | Product-level summary (65 products) with cluster assignments |
