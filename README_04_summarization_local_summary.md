# Summarization (Local) Results Summary

## Method

### Approach
- **Model:** Google Flan-T5-base (`google/flan-t5-base`) — 250M parameter seq2seq transformer
- **GPU:** NVIDIA GeForce RTX 4050 Laptop GPU
- **Strategy:** Build structured "evidence briefs" per category, then prompt T5 to generate shopper-friendly articles
- **Environment:** Python 3.10.19, PyTorch with CUDA

### Data Pipeline

1. Merged `data_with_clusters.csv` + `data_with_predictions_v2.csv` on review ID, text, date, and username
2. Computed per-product stats: review count, avg rating, negative rate, positive rate
3. Ranked products using `avg_rating × log(review_count)` — balances quality with volume
4. Selected top 3 products per cluster and worst product (minimum 20 reviews)
5. Extracted top complaints from negative reviews using TF-IDF on negative review text
6. Built structured "category briefs" combining all evidence
7. Fed briefs to Flan-T5 with prompt engineering to generate articles

### Ranking Formula

```
rank_score = avg_rating × log(1 + review_count)
```

This is a smart design — a product with 4.7 rating and 500 reviews ranks higher than a 5.0 product with 9 reviews, preventing low-volume products from dominating.

### Complaint Extraction

Used TF-IDF vectorization on negative reviews per product to identify top recurring complaint terms:
- Unigrams + bigrams, English stop words removed
- Minimum 5 negative reviews required (returns empty otherwise)
- Top 5–8 terms extracted per product

---

## Results

### Category Briefs (Input to T5)

The evidence briefs were well-structured and informative. Example for Accessories:

```
CATEGORY: Accessories

TOP 3 PRODUCTS:
1) Amazon 9W PowerFast Official OEM USB Charger | rating=4.67 | reviews=39
   complaints: (not enough negative reviews)
2) AmazonBasics 15.6-Inch Laptop and Tablet Bag | rating=4.52 | reviews=21
   complaints: (not enough negative reviews)
3) AmazonBasics Ventilated Adjustable Laptop Stand | rating=4.33 | reviews=24
   complaints: (not enough negative reviews)

WORST PRODUCT: AmazonBasics Backpack for Laptops up to 17-inches | rating=4.16 | reviews=25
avoid because: low ratings / frequent negatives
```

### Generated Articles (T5 Output)

The article generation was the weakest part of the pipeline. Flan-T5-base consistently failed to produce structured, readable articles:

| Category | T5 Output | Quality |
|----------|-----------|---------|
| Accessories | Echoed the brief back verbatim — no actual article generated | Poor |
| Batteries & Household | Single line: product name + "Avoid because: batteries; long; don" | Poor |
| E-Readers | Echoed product names without writing prose | Poor |
| Fire Tablets | "Fire Tablets: 3 products: Fire HD 8 Tablet with..." — list, not an article | Poor |
| Media & Home | "The top 3 products in the Media & Home category." — one sentence total | Poor |

The prompt asked for structured output with `===TITLE===`, `===SUMMARY===`, `===TOP3===`, `===AVOID===` sections. T5 failed to follow this format in any category — it either echoed the input, produced a single sentence, or generated a flat list of product names.

### Root Cause

Flan-T5-base (250M parameters) lacks the capacity for structured multi-paragraph generation. It excels at short factual QA tasks but cannot:
- Follow complex output formatting instructions
- Write coherent multi-sentence paragraphs from structured data
- Maintain context across a 200+ word generation
- Distinguish between "summarize" and "echo back"

Flan-T5-large (780M) or Flan-T5-xl (3B) would likely perform significantly better, though at higher compute cost.

---

## Comparison: API vs Local Summarization

| Aspect | API (Claude Sonnet) | Local (Flan-T5-base) |
|--------|-------------------|---------------------|
| Output quality | Rich, structured 600-word articles | 1–2 sentences, often echoes input |
| Prompt structure followed | Yes — all 5 sections present | Failed to produce any sections |
| Complaint analysis | Integrated into readable narrative | Raw TF-IDF terms ("batteries; long; don") |
| Top 3 products | Named, explained, with review evidence | Listed but not discussed |
| Worst product | Identified with reasoning from reviews | Named but no explanation |
| Article readability | Ready for shoppers | Not usable as-is |
| Cost | $0.43 USD (39 API calls) | Free (GPU compute only) |
| Infrastructure needed | API key, internet connection | GPU (RTX 4050), ~1GB model download |
| Latency per article | ~2–3 seconds | <1 second on GPU |

**Conclusion:** The local approach has a solid data pipeline (ranking, complaint extraction, brief building) but the generation model is too small for the task. The API approach produces vastly superior output at minimal cost. For the project, the API-generated summaries are used in the web deployment.

---

## What Worked Well

1. **Product ranking formula** — `avg_rating × log(review_count)` is a clean, defensible approach
2. **Minimum review threshold** (20) for worst product prevents noise from low-volume products
3. **TF-IDF complaint extraction** — automated identification of recurring issues from negative reviews
4. **Complaint caching** — avoids redundant TF-IDF computation across calls
5. **Evidence brief structure** — the category briefs are well-organized and reusable
6. **Negative review snippet sampling** — includes actual review excerpts in the enhanced brief version

## What Didn't Work

1. **Flan-T5-base is too small** — 250M parameters cannot handle structured multi-paragraph generation
2. **Article output is unusable** — echoes input, produces single sentences, or generates flat lists
3. **Complaint terms are raw TF-IDF** — outputs like "batteries; long; don; battery; amazon" are not human-readable
4. **No Smart Speakers cluster** — only 5 of 6 categories appear in the output (Smart Speakers missing from briefs)

---

## Files Produced

| File | Description |
|------|-------------|
| `04_summarization_local.ipynb` | Full notebook with data pipeline, T5 generation, and Gradio app |
| `category_blog_posts.csv` | Generated articles per category (5 rows: category, brief, article) |
