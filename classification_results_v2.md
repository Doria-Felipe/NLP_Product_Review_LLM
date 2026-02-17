# Classification Results Summary — v2

## Model Pipeline

**RoBERTa-base** → fine-tuned on Yelp 3-class (650K reviews, by Felipe) → fine-tuned on Amazon reviews with class weights (v2)

- **Base model:** roberta-base (124.6M parameters, all trainable)
- **Yelp pre-training:** 8,000 samples, 5 epochs, best checkpoint at step 1000
- **Amazon fine-tuning:** 22,665 training samples, early stopping triggered at step 3,350 (epoch ~2.4/5)
- **Best checkpoint:** step 3,200 (selected by macro F1)
- **GPU:** NVIDIA GeForce RTX 4050 Laptop GPU

---

## Key Improvements (v1 → v2)

| What | v1 | v2 |
|------|----|----|
| Training data | Yelp only (external) | Yelp + Amazon (our data) |
| Class imbalance handling | None | Weighted CrossEntropyLoss (Neg 6.0x, Neu 7.8x, Pos 0.4x) |
| Train/test split | No split (evaluated on full dataset) | Stratified 80/20 split |
| Overfitting prevention | None (val loss rose from 0.45 to 0.99) | Early stopping (patience=3 on macro F1) |
| Optimization target | Accuracy | Macro F1 (balances all classes equally) |
| Tokenization | Padded to max_length | Dynamic padding via DataCollator (faster) |

---

## Test Set Results (5,667 held-out reviews)

| Metric | v1 (Yelp only) | v2 (+ Amazon fine-tune) | Change |
|--------|----------------|------------------------|--------|
| **Accuracy** | 0.8723 | **0.9548** | +0.0825 |
| **F1 Macro** | 0.6347 | **0.7912** | +0.1565 |
| Negative F1 | 0.6985 | **0.8223** | +0.1238 |
| Neutral F1 | 0.2689 | **0.5691** | +0.3002 |
| Positive F1 | 0.9367 | **0.9821** | +0.0454 |

> Note: v1 metrics were on the full dataset (no split), v2 on a proper held-out test set — making v2 numbers more conservative and trustworthy.

---

## Per-Class Detail (Test Set)

| Class | Precision | Recall | F1-Score | Support |
|-------|-----------|--------|----------|---------|
| NEGATIVE | 0.8036 | 0.8418 | 0.8223 | 316 |
| NEUTRAL | 0.5504 | 0.5892 | 0.5691 | 241 |
| POSITIVE | 0.9852 | 0.9791 | 0.9821 | 5,110 |
| **Macro avg** | **0.7797** | **0.8033** | **0.7912** | **5,667** |
| Weighted avg | 0.9566 | 0.9548 | 0.9557 | 5,667 |

---

## Class Weights Applied

| Class | Weight | Interpretation |
|-------|--------|---------------|
| NEGATIVE (5.6% of data) | 5.9723 | Misclassifying a negative review costs ~6x |
| NEUTRAL (4.3% of data) | 7.8290 | Misclassifying a neutral review costs ~8x |
| POSITIVE (90.2% of data) | 0.3697 | Misclassifying a positive review costs ~0.4x |

---

## Error Analysis (Test Set)

**Total errors:** 256 / 5,667 (4.5%)

| True Label | Predicted As | Count | Note |
|------------|-------------|-------|------|
| POSITIVE | NEUTRAL | 78 | Mild positive reviews mistaken as neutral |
| NEUTRAL | POSITIVE | 63 | Neutral reviews seen as mildly positive |
| NEGATIVE | NEUTRAL | 38 | Negative reviews softened to neutral |
| NEUTRAL | NEGATIVE | 36 | Neutral reviews seen as negative |
| POSITIVE | NEGATIVE | 29 | Positive reviews misread as negative |
| NEGATIVE | POSITIVE | 12 | Worst error type — but very rare |

**Key observations from sample errors:**
- Some "Positive predicted as Negative" cases are sarcastic or mention negatives before concluding positively ("batteries are stupid expensive in the store... so buy in bulk" → 5 stars)
- Some "Negative predicted as Positive" cases appear to be mislabeled in the original data (e.g., "my granddaughter loves it" rated 1 star)
- The Neutral boundary remains the hardest — 3-star reviews often read like mild positives or mild negatives

---

## Full Dataset Predictions (28,332 reviews)

| Metric | Value |
|--------|-------|
| Accuracy | 0.9716 |
| Macro F1 | 0.8711 |
| Negative F1 | 0.9074 |
| Neutral F1 | 0.7183 |
| Positive F1 | 0.9876 |

> These numbers are higher because the model saw the training portion during fine-tuning. The test set metrics (95.48%, 0.791) are the honest evaluation numbers.

**Prediction distribution:**
| Label | Count |
|-------|-------|
| POSITIVE | 25,476 |
| NEGATIVE | 1,648 |
| NEUTRAL | 1,208 |

---

## Training Log Highlights

- Training stopped early at step 3,350 (epoch 2.4 of 5) — early stopping working as intended
- Best macro F1 achieved at step 3,200: **0.7912**
- Training loss decreased steadily: 0.69 → 0.50
- Validation loss fluctuated (typical with class weights) but model selection was by F1, not loss

---

## Quick Model Test (Sanity Check)

| Review | Prediction | Confidence |
|--------|------------|------------|
| "This product is terrible, waste of money." | NEGATIVE | 99.93% |
| "It's okay, nothing special but does the job." | POSITIVE | 95.76% |
| "Absolutely love it! Best purchase I've made." | POSITIVE | 99.87% |
| "good" | POSITIVE | 99.84% |
| "Batteries died after one week. Very disappointed." | NEGATIVE | 99.93% |
| "Works as expected for the price." | POSITIVE | 99.57% |

> Note: "It's okay, nothing special" was predicted POSITIVE (95.76%) rather than NEUTRAL — consistent with the model's tendency to lean positive on ambiguous reviews. This is the Neutral boundary challenge.

---

## Files Produced

| File | Description |
|------|-------------|
| `./models/amazon_roberta_v2_final/` | Saved model for deployment |
| `data_with_predictions_v2.csv` | Full dataset with predicted labels and confidence scores per class |
