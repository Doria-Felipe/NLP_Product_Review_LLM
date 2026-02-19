# Summarization (API) Results Summary

## Method

### Approach
- **Provider:** Anthropic Claude Sonnet (`claude-sonnet-4-20250514`)
- **Temperature:** 0.3 (consistent, factual output)
- **Strategy:** Sample representative reviews per product, send structured prompts to LLM
- Switchable to OpenAI GPT-4o-mini via `PROVIDER` flag

### Review Sampling Strategy
For each product, we selected the most informative reviews rather than sending all 28K to the API:
- **5 positive, 5 negative, 3 neutral** reviews per product
- Filtered out very short reviews (< 5 words)
- Prioritized longer reviews (sorted by word count, truncated at 500 chars)
- Included aggregate stats (avg rating, sentiment distribution, review count)

### Prompt Design
Two structured prompt templates:
1. **Cluster summary prompt** — requests: category overview, top 3 products, common complaints, worst product, buying recommendation (max 600 words)
2. **Product summary prompt** — requests: overall verdict (Buy/Consider/Avoid), strengths, weaknesses, best-for (max 200 words)

---

## Results Overview

| Metric | Value |
|--------|-------|
| Total API calls | 39 |
| Cluster summaries | 6 |
| Product summaries | 33 (products with ≥ 20 reviews) |
| Total output | 66,552 characters |
| Total cost | **$0.43 USD** (from Anthropic console) |
| Cost per summary | ~$0.011 |

---

## Cluster Summaries Generated

### 1. Fire Tablets (14,396 reviews, 4.56 avg rating)

**Top 3 recommended:**
1. Fire HD 8 Tablet (16GB, Tangerine) — 2,443 reviews, best balance of performance and value at ~$89
2. All-New Fire HD 8 Tablet (16GB) — 2,370 reviews, superior screen vs 7" models
3. Fire Kids Edition (Pink) — 1,676 reviews, exceptional durability with 2-year replacement warranty

**Common complaints:** Limited app selection (no Google Play), slow performance especially gaming, charging port failures, poor sunlight readability, storage management confusion

**Worst rated:** Fire Kids Edition models — slightly higher complaint rates (3.2-3.5% negative) mainly due to charging port failures

### 2. Batteries & Household (12,086 reviews, 4.45 avg rating)

**Top 3 recommended:**
1. AmazonBasics AAA Batteries (36 Count) — 8,343 reviews, capacity rivals name brands
2. AmazonBasics AA Batteries (48 Count) — 3,728 reviews, ~25¢/battery vs 50-58¢ for Duracell/Energizer
3. Expanding Accordion File Folder — 9 reviews, perfect 5.0/5 rating

**Common complaints:** Battery leakage damaging devices, inconsistent quality control (undervoltage out of box), fit issues in some devices, premature failure

**Worst rated:** AmazonBasics Double-Door Dog Crate — 3.5/5 but only 2 reviews

### 3. E-Readers (1,049 reviews, 4.66 avg rating)

**Top 3 recommended:**
1. Kindle Voyage (300 ppi) — 505 reviews, 96.8% positive, best auto-brightness and screen quality
2. Kindle E-reader (White) — 287 reviews, best value, simple and effective
3. Kindle Oasis (Walnut charging cover) — 62 reviews, 96.8% positive, premium with physical buttons

**Common complaints:** Screen discoloration (yellow tinge), charging failures, software update issues, fragile screens, inconsistent customer service

**Worst rated:** All-New Kindle Oasis (7", waterproof) — 9.1% negative rate

### 4. Smart Speakers (632 reviews, 4.54 avg rating)

**Top 3 recommended:**
1. Amazon Tap — 601 reviews, excellent sound quality, 9-hour battery, portable
2. Certified Refurbished Echo — 7 reviews, perfect 5.0/5, great value
3. Amazon Echo (1st Gen, White) — 13 reviews, reliable for shopping lists and smart home

**Common complaints:** Amazon Prime dependency for features, limited music streaming options, voice recognition requires specific phrasing, connectivity issues, Tap requires button press (not hands-free)

**Worst rated:** Amazon Echo (1st Gen) — 84.6% positive but lowest in category

### 5. Accessories (138 reviews, 4.31 avg rating)

**Top 3 recommended:**
1. Amazon 9W PowerFast USB Charger — 39 reviews, 4.67/5, reliable OEM charger
2. AmazonBasics 15.6" Laptop Bag — 21 reviews, 4.52/5, well-constructed with good padding
3. AmazonBasics USB 3.0 Cable — 6 reviews, perfect 5.0/5

**Common complaints:** Charger durability (~1 year lifespan), missing cables, cheap-feeling materials on backpack, size limitations not matching specs

**Worst rated:** OEM Kindle Power USB Adapter — 1.0/5, 100% negative (third-party, avoid)

### 6. Media & Home (31 reviews, 4.39 avg rating)

**Top 3 recommended:**
1. Fire TV Stick Pair Kit — 6 reviews, perfect 5.0/5, cable-cutting savings highlighted
2. Fire TV Gaming Edition — 3 reviews, 4.67/5, strong gaming + streaming combo
3. AmazonBasics External Hard Drive Case — 6 reviews, 4.5/5, sturdy and well-fitting

**Common complaints:** Setup difficulties, product discrepancies vs photos, limited functionality (mirror casting), small review sample sizes

**Worst rated:** Certified Refurbished Fire TV — 2.8/5, 40% negative

---

## Product Summaries Generated (33 total)

Individual summaries were generated for all products with ≥ 20 reviews:

| Cluster | Products Summarized |
|---------|-------------------|
| Fire Tablets | 20 products |
| Batteries & Household | 2 products |
| E-Readers | 7 products |
| Smart Speakers | 1 product (Amazon Tap) |
| Accessories | 3 products |
| Media & Home | 0 products (all < 20 reviews) |

Each product summary includes:
- **Overall Verdict** — Buy / Consider / Avoid
- **Top 3 Strengths** from positive reviews
- **Top 3 Weaknesses** from negative reviews
- **Best For** — target buyer profile

---

## Quality Assessment

**Strengths of the generated summaries:**
- Factual and grounded in actual review data
- Consistent structure across all clusters
- Identified genuine product issues (battery leakage, charging port failures, app limitations)
- Price comparisons and value assessments are accurate
- Appropriate caveats for products with limited reviews

**Limitations:**
- Small clusters (Media & Home: 31 reviews, Accessories: 138) have less material to work with
- Model occasionally fills gaps with reasonable but unverifiable inferences
- Some product names are truncated in the output
- No cross-cluster comparisons

---

## Files Produced

| File | Description | Size |
|------|-------------|------|
| `summaries_api.json` | Structured JSON with all summaries (for web app) | — |
| `summaries_report.md` | Readable markdown report with all summaries | 70,879 chars |
| `04_summarization_api.ipynb` | Full notebook with code and outputs | — |

---

## Cost Breakdown

| Item | Value |
|------|-------|
| Provider | Anthropic (Claude Sonnet) |
| Total API calls | 39 |
| Total cost | $0.43 USD |
| Per-call cost | ~$0.011 |
| Input tokens dominate | Review samples in prompts are the main cost driver |
| GPT-4o-mini equivalent | Would cost ~$0.01-0.02 total (much cheaper) |
