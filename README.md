# NLP Business Case — Automated Customer Reviews Analysis (Review Analyzer)

## Project Overview

**Objective:** Build an end-to-end NLP pipeline that classifies customer sentiment, clusters products into categories, and generates AI-powered recommendation articles from product reviews.

**Team:** Krzysztof Giwojno & Felipe Doria — Group 4

**Course:** IronHack AI Engineering Bootcamp — Project 3

**Live Demo:** [https://giwojno.pl/review-analyzer/](https://giwojno.pl/review-analyzer/)

**Dataset:** [Datafiniti Amazon Consumer Reviews](https://www.kaggle.com/datasets/datafiniti/consumer-reviews-of-amazon-products) — 28,332 reviews across 65 Amazon-branded products

---

## Results at a Glance

| Component | Method | Key Result |
|-----------|--------|------------|
| Classification | RoBERTa fine-tuned (Yelp → Amazon) | **95.48% accuracy**, 0.791 macro F1 |
| Clustering | TF-IDF + K-Means | **6 clusters**, silhouette 0.2364 |
| Summarization (API) | Claude Sonnet via Anthropic API | 6 cluster + 33 product summaries, **$0.43** |
| Summarization (Local) | Flan-T5-base (250M params, GPU) | 6 cluster summaries, **$0 cost** |
| Deployment | Static site on OVH shared hosting | **Live at giwojno.pl/review-analyzer** |

---

## Pipeline

```
Raw Reviews (28,332)
    │
    ▼
[1. Data Exploration]  →  data_cleaned.csv
    │
    ▼
[2. Classification]    →  data_with_predictions_v2.csv
    │                      RoBERTa: 95.48% accuracy
    ▼
[3. Clustering]        →  data_with_clusters.csv, product_clusters.csv
    │                      K=6: Tablets, Batteries, E-Readers, Speakers, Accessories, Media
    ▼
[4. Summarization]     →  summaries_api.json, summaries_local_full.json
    │                      API (Claude) + Local (Flan-T5)
    ▼
[5. Web Deployment]    →  Static HTML + JSON → giwojno.pl/review-analyzer
```

---

## 1. Data Exploration

**Notebook:** `notebooks/01_data_exploration.ipynb` | **Details:** `docs/README_01_data_exploration_summary.md`

- 28,332 reviews, 65 unique Amazon products, 24 columns
- Dropped 10 columns (>99% null or metadata)
- Sentiment mapping: 1–2 stars → Negative (5.6%), 3 stars → Neutral (4.3%), 4–5 stars → Positive (90.2%)
- Heavily imbalanced — major challenge for classification
- 35.87% duplicate review texts retained (legitimate short reviews like "good", "great" from different users)
- Top products by volume: AmazonBasics AAA Batteries (8,343 reviews), AA Batteries (3,728), Fire HD 8 (2,443)

---

## 2. Sentiment Classification

**Notebooks:** `notebooks/02_review_classification_transformers.ipynb` (v1), `notebooks/02_review_classification_v2.ipynb` (v2)
**Details:** `docs/README_02_classification_results_v2.md`

Two-stage training: pre-trained on 650K Yelp reviews (3-class), then fine-tuned on Amazon data with class weights.

| Metric | v1 | v2 | Change |
|--------|----|----|--------|
| Accuracy | 87.23% | **95.48%** | +8.25% |
| Macro F1 | 0.635 | **0.791** | +0.156 |
| Neutral F1 | 0.269 | **0.569** | +0.300 |

### What fixed it (v2)

- Stratified 80/20 train/test split (v1 had no split)
- Class weights: Negative 6.0x, Neutral 7.8x, Positive 0.4x
- Early stopping (patience 3) — best checkpoint at step 3,200
- Training on Amazon data, not just Yelp

### Per-class results (v2 test set, 5,667 reviews)

| Class | Precision | Recall | F1 |
|-------|-----------|--------|----|
| Positive | 0.985 | 0.979 | 0.982 |
| Negative | 0.804 | 0.842 | 0.822 |
| Neutral | 0.550 | 0.589 | 0.569 |

Only 256 errors on the test set (4.5% error rate). Most errors occur at the Positive↔Neutral boundary — genuinely ambiguous reviews.

---

## 3. Product Clustering

**Notebook:** `notebooks/03_clustering.ipynb` | **Details:** `docs/README_03_clustering_summary.md`

### Method: TF-IDF + K-Means

- Aggregated to product level (65 rows)
- Combined product names + cleaned category labels
- TF-IDF: unigrams + bigrams, 200 features
- Tested K=2 to K=10 — chose K=6 (best silhouette within required 4–6 range)

### 6 Clusters

| Cluster | Products | Reviews | Avg Rating | % Positive |
|---------|----------|---------|------------|------------|
| Fire Tablets | 20 | 14,396 | 4.56 | 93.2% |
| Batteries & Household | 7 | 12,086 | 4.45 | 86.1% |
| E-Readers | 10 | 1,049 | 4.66 | 95.2% |
| Smart Speakers | 9 | 632 | 4.54 | 91.9% |
| Accessories | 11 | 138 | 4.31 | 82.6% |
| Media & Home | 8 | 31 | 4.39 | 83.9% |

E-Readers have the highest satisfaction (95.2% positive, 1.5% negative). Batteries & Household has the highest negative rate (9.5%) among major clusters.

---

## 4. Review Summarization

Two parallel approaches — API-based and local model.

### 4a. API Summarization

**Notebook:** `notebooks/04_summarization_api.ipynb` | **Details:** `docs/README_04_summarization_api_summary.md`

- **Model:** Claude Sonnet (`claude-sonnet-4-20250514`) via Anthropic API
- **Strategy:** Sample representative reviews per product (5 positive, 5 negative, 3 neutral), send with product stats to LLM
- **Output:** 6 cluster recommendation articles (~600 words each) + 33 individual product summaries
- **Cost:** $0.43 USD total (39 API calls, ~$0.011 per summary)
- **Quality:** Rich, structured articles with top products, complaints, worst product, buying advice

### 4b. Local Summarization

**Notebook:** `notebooks/04_summarization_local.ipynb` | **Details:** `docs/README_04_summarization_local_summary.md`

- **Model:** Google Flan-T5-base (250M params) running on NVIDIA RTX 4050
- **Strategy:** Build structured "evidence briefs" per category with product rankings and TF-IDF complaint extraction, then prompt T5 to generate articles
- **Ranking formula:** `avg_rating × log(1 + review_count)` — balances quality with volume
- **Output:** 6 cluster summaries + 18 product summaries
- **Cost:** $0 (fully local, GPU compute only)
- **Quality:** Shorter factual outputs — T5-base lacks capacity for structured multi-paragraph generation

### Comparison

| Aspect | API (Claude Sonnet) | Local (Flan-T5-base) |
|--------|-------------------|---------------------|
| Output quality | Full recommendation articles | 1–2 sentences, factual |
| Prompt structure followed | All sections present | Failed to produce sections |
| Cost | $0.43 | Free |
| Infrastructure | API key + internet | GPU (RTX 4050) |

---

## 5. Web Deployment

**Location:** `webapp/` | **Details:** `docs/README_05_webapp_summary.md`

**Live:** [https://giwojno.pl/review-analyzer/](https://giwojno.pl/review-analyzer/)

Static single-page app — pure HTML/CSS/JS with pre-computed JSON data. No backend needed.

### Features

- **Dashboard** — stats overview, sentiment distribution, rating charts, reviews by category
- **Categories (API)** — browse Claude-generated recommendation articles per cluster
- **Categories (Local)** — browse Flan-T5 generated summaries for comparison
- **Products** — filterable table of all 65 products, click for AI summaries
- **Reviews** — explorer with filters (category, sentiment, rating, text search)
- **About** — model details and project info

### Deployment

```bash
cd webapp
python generate_webapp.py    # reads CSVs + JSONs → produces data/*.json
python -m http.server 8000   # test locally at http://localhost:8000
./deploy.sh                  # uploads to OVH via SFTP (credentials in .env)
```

---

## Project Structure

```
.
├── README.md                                       # This file
├── NLP_Review_Analyzer_Group4.pdf                  # Presentation (PDF export)
├── .gitignore
│
├── data/                                           # All data files
│   ├── data_cleaned.csv                            #  Cleaned dataset (28,332 reviews)
│   ├── data_with_clusters.csv                      #  Reviews with cluster assignments
│   ├── data_with_predictions_v2.csv                #  Reviews with sentiment predictions
│   ├── product_clusters.csv                        #  Product-level cluster info (65 products)
│   ├── predictions.csv                             #  Raw model predictions
│   ├── category_blog_posts.csv                     #  Local T5 generated articles
│   ├── summaries_api.json                          #  API-generated summaries
│   └── summaries_local_full.json                   #  Local T5 summaries
│
├── notebooks/                                      # Core pipeline (run in order)
│   ├── 01_data_exploration.ipynb                   #  Data exploration and cleaning
│   ├── 02_review_classification_transformers.ipynb  #  Classification v1 (Felipe)
│   ├── 02_review_classification_v2.ipynb           #  Classification v2 with class weights
│   ├── 03_clustering.ipynb                         #  TF-IDF + K-Means clustering
│   ├── 04_summarization_api.ipynb                  #  API summarization (Claude Sonnet)
│   └── 04_summarization_local.ipynb                #  Local summarization (Flan-T5)
│
├── docs/                                           # Documentation and reports
│   ├── NLP_Product_Review_Project_report_basic.pdf #  PDF report (basic)
│   ├── NLP_Product_Review_Project_report_full.pdf  #  PDF report (full with charts)
│   ├── NLP_Review_Analyzer_Group4.pptx             #  Presentation source file
│   ├── README_01_data_exploration_summary.md       #  Exploration findings
│   ├── README_02_classification_results_v2.md      #  Classification metrics
│   ├── README_03_clustering_summary.md             #  Clustering results
│   ├── README_04_summarization_api_summary.md      #  API summarization details
│   ├── README_04_summarization_local_summary.md    #  Local summarization details
│   ├── README_05_webapp_summary.md                 #  Web deployment docs
│   └── summaries_report.md                         #  Full readable summary report
│
├── extras/                                         # Support scripts and presentation assets
│   ├── generate_cluster_scatter.py                 #  Cluster visualization script
│   ├── generate_cluster_scatter_half.py            #  Cluster viz (half-page variant)
│   ├── cluster_scatter.png                         #  Generated cluster visualization
│   ├── demo_script.md                              #  Demo recording script
│   └── slides/                                     #  Generated slide visuals
│       ├── slide02_before_after.png
│       ├── slide03_funnel.png
│       ├── slide04_methods.png
│       ├── slide05_classification.png
│       ├── slide06_confusion.png
│       ├── slide07_silhouette.png
│       ├── slide08_clusters.png
│       ├── slide09_comparison.png
│       ├── slide10b_bars.png
│       ├── slide10b_cards.png
│       └── slide11_qr.png
│
└── webapp/                                         # Deployed web application
    ├── index.html                                  #  Single-page app
    ├── generate_webapp.py                          #  Data generation script
    ├── deploy.sh                                   #  SFTP deployment script
    ├── app_gradio.py                               #  Gradio app (Felipe)
    ├── README.md                                   #  Webapp setup instructions
    ├── .env                                        #  Deployment credentials (git-ignored)
    └── data/                                       #  Generated JSON files
        ├── stats.json
        ├── clusters.json
        ├── clusters_local.json
        ├── products.json
        └── reviews_sample.json
```

---

## Technical Stack

| Component | Technology |
|-----------|-----------|
| Language | Python 3.10 / 3.14 |
| Classification | RoBERTa-base, Transformers, PyTorch |
| Clustering | scikit-learn (TF-IDF, K-Means) |
| Summarization (API) | Anthropic Claude Sonnet API |
| Summarization (Local) | Google Flan-T5-base, HuggingFace |
| Data processing | pandas, NumPy |
| Web app | HTML, CSS, JavaScript (no framework) |
| Hosting | OVH shared hosting (static files) |
| GPU | NVIDIA RTX 4050 (Felipe), RTX 2080 (Krzysztof) |

---

## How to Reproduce

### Prerequisites

```bash
pip install pandas numpy scikit-learn transformers torch anthropic openai python-dotenv matplotlib seaborn
```

### Setup

```bash
git clone https://github.com/Doria-Felipe/NLP_Product_Review_LLM.git
cd NLP_Product_Review_LLM
cp .env.example .env   # Add your API keys
```

### Run Notebooks (in order)

Run notebooks in order from `notebooks/`. Each notebook reads from `data/` and writes back to `data/`. Classification and local summarization require a CUDA-capable GPU. API summarization requires an Anthropic API key in `.env`.

1. `01_data_exploration.ipynb` — produces `data_cleaned.csv`
2. `02_review_classification_v2.ipynb` — produces `data_with_predictions_v2.csv` (requires GPU)
3. `03_clustering.ipynb` — produces `data_with_clusters.csv`, `product_clusters.csv`
4. `04_summarization_api.ipynb` — produces `summaries_api.json` (requires API key)
5. `04_summarization_local.ipynb` — produces `summaries_local_full.json` (requires GPU)

### Deploy Web App

```bash
cd webapp
python generate_webapp.py
python -m http.server 8000   # test locally at http://localhost:8000
./deploy.sh                  # deploy to OVH
```

---

## Key Learnings

- **Class weights are critical** for imbalanced datasets — Neutral F1 jumped from 0.269 to 0.569
- **Early stopping** prevented overfitting and found the best checkpoint automatically (epoch 2.4 of 5)
- **Simpler models can surprise** — the ranking formula `avg_rating × log(review_count)` is more defensible than complex alternatives
- **Model size matters for generation** — Flan-T5-base (250M) cannot handle structured article generation; API models (Claude Sonnet) produce vastly superior output at minimal cost ($0.43)
- **Static sites work** — pre-computing results removes the need for backend infrastructure, making deployment trivial on shared hosting

---

*Krzysztof Giwojno & Felipe Doria — Group 4, IronHack AI Engineering Bootcamp, February 2026*
