"""
generate_webapp.py — Static site data generator
Project 3: NLP Business Case | Group 4 | IronHack AI Engineering Bootcamp
Team: Krzysztof Giwojno & Felipe Doria

Usage:
    python generate_webapp.py

Reads:
    - data_cleaned.csv (or data_with_clusters.csv)
    - data_with_predictions_v2.csv
    - summaries_api.json
    - product_clusters.csv

Produces (in webapp/data/):
    - stats.json          Dashboard overview numbers
    - clusters.json       Cluster summaries + metadata
    - products.json       Product summaries + stats
    - reviews_sample.json Sample reviews with predictions for the explorer
"""

import json
import os
import random
import pandas as pd
import numpy as np

# ---------- CONFIG ----------
DATA_DIR = os.path.join(os.path.dirname(__file__), "..")  # project root (parent of webapp/)
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "data")
REVIEWS_SAMPLE_SIZE = 200  # reviews to include in explorer (per cluster, capped)

os.makedirs(OUTPUT_DIR, exist_ok=True)

# ---------- LOAD DATA ----------
print("Loading data...")

# Try clustered data first, fall back to cleaned
clustered_path = os.path.join(DATA_DIR, "data_with_clusters.csv")
cleaned_path = os.path.join(DATA_DIR, "data_cleaned.csv")

if os.path.exists(clustered_path):
    df = pd.read_csv(clustered_path)
    print(f"  Loaded data_with_clusters.csv: {len(df):,} rows")
elif os.path.exists(cleaned_path):
    df = pd.read_csv(cleaned_path)
    print(f"  Loaded data_cleaned.csv: {len(df):,} rows")
else:
    raise FileNotFoundError(
        f"No data file found. Expected one of:\n"
        f"  {clustered_path}\n"
        f"  {cleaned_path}"
    )

# Load predictions
pred_path = os.path.join(DATA_DIR, "data_with_predictions_v2.csv")
if os.path.exists(pred_path):
    pred_df = pd.read_csv(pred_path)
    if "predicted_label" in pred_df.columns:
        df["predicted_label"] = pred_df["predicted_label"]
        df["predicted_score"] = pred_df["predicted_score"]
        print(f"  Merged v2 predictions")

# Load summaries
summaries = {}
summaries_path = os.path.join(DATA_DIR, "summaries_api.json")
if os.path.exists(summaries_path):
    with open(summaries_path, "r", encoding="utf-8") as f:
        summaries = json.load(f)
    print(f"  Loaded summaries_api.json")

# Load product clusters
product_clusters = None
clusters_path = os.path.join(DATA_DIR, "product_clusters.csv")
if os.path.exists(clusters_path):
    product_clusters = pd.read_csv(clusters_path)
    print(f"  Loaded product_clusters.csv: {len(product_clusters)} products")

# ---------- 1. STATS.JSON ----------
print("\nGenerating stats.json...")

sentiment_col = "predicted_label" if "predicted_label" in df.columns else "sentiment"
sentiment_counts = df[sentiment_col].value_counts().to_dict()

# Normalize sentiment keys
norm_sentiment = {}
for k, v in sentiment_counts.items():
    key = k.upper() if isinstance(k, str) else str(k)
    norm_sentiment[key] = int(v)

cluster_col = "cluster_name" if "cluster_name" in df.columns else None
cluster_dist = {}
if cluster_col:
    for name, group in df.groupby(cluster_col):
        cluster_dist[name] = {
            "review_count": int(len(group)),
            "product_count": int(group["name"].nunique()),
            "avg_rating": round(float(group["reviews.rating"].mean()), 2),
        }

stats = {
    "total_reviews": int(len(df)),
    "total_products": int(df["name"].nunique()),
    "total_clusters": len(cluster_dist),
    "avg_rating": round(float(df["reviews.rating"].mean()), 2),
    "sentiment_distribution": norm_sentiment,
    "cluster_distribution": cluster_dist,
    "rating_distribution": {
        str(int(k)): int(v) for k, v in
        df["reviews.rating"].value_counts().sort_index().items()
    },
    "model_info": {
        "classification": "RoBERTa-base (Yelp→Amazon fine-tuned, class weights)",
        "clustering": "TF-IDF + K-Means (K=6)",
        "summarization": summaries.get("model", "Claude Sonnet"),
        "provider": summaries.get("provider", "anthropic"),
    }
}

with open(f"{OUTPUT_DIR}/stats.json", "w") as f:
    json.dump(stats, f, indent=2)
print(f"  Saved stats.json")

# ---------- 2. CLUSTERS.JSON ----------
print("Generating clusters.json...")

clusters_out = {}
cluster_summaries = summaries.get("cluster_summaries", {})

if cluster_col:
    for name, group in df.groupby(cluster_col):
        sentiment_dist = {}
        if sentiment_col in group.columns:
            for label, count in group[sentiment_col].value_counts().items():
                sentiment_dist[str(label).upper()] = int(count)

        top_products = (
            group.groupby("name")
            .agg(reviews=("reviews.text", "count"), avg_rating=("reviews.rating", "mean"))
            .sort_values("reviews", ascending=False)
            .head(5)
        )

        clusters_out[name] = {
            "review_count": int(len(group)),
            "product_count": int(group["name"].nunique()),
            "avg_rating": round(float(group["reviews.rating"].mean()), 2),
            "sentiment": sentiment_dist,
            "top_products": [
                {"name": pname, "reviews": int(row["reviews"]),
                 "avg_rating": round(float(row["avg_rating"]), 2)}
                for pname, row in top_products.iterrows()
            ],
            "summary": cluster_summaries.get(name, "Summary not available."),
        }

with open(f"{OUTPUT_DIR}/clusters.json", "w") as f:
    json.dump(clusters_out, f, indent=2, ensure_ascii=False)
print(f"  Saved clusters.json ({len(clusters_out)} clusters)")

# ---------- 3. PRODUCTS.JSON ----------
print("Generating products.json...")

product_summaries_raw = summaries.get("product_summaries", {})
products_out = []

for product_name in df["name"].unique():
    product_df = df[df["name"] == product_name]
    review_count = len(product_df)
    avg_rating = round(float(product_df["reviews.rating"].mean()), 2)

    sentiment_dist = {}
    if sentiment_col in product_df.columns:
        for label, count in product_df[sentiment_col].value_counts().items():
            sentiment_dist[str(label).upper()] = int(count)

    cluster = product_df[cluster_col].iloc[0] if cluster_col else "Unknown"

    # Get summary if available
    summary_data = product_summaries_raw.get(product_name, {})
    summary_text = summary_data.get("summary", "") if isinstance(summary_data, dict) else ""

    products_out.append({
        "name": product_name,
        "cluster": cluster,
        "review_count": int(review_count),
        "avg_rating": avg_rating,
        "sentiment": sentiment_dist,
        "summary": summary_text,
    })

products_out.sort(key=lambda x: x["review_count"], reverse=True)

with open(f"{OUTPUT_DIR}/products.json", "w") as f:
    json.dump(products_out, f, indent=2, ensure_ascii=False)
print(f"  Saved products.json ({len(products_out)} products)")

# ---------- 4. REVIEWS_SAMPLE.JSON ----------
print("Generating reviews_sample.json...")

sample_reviews = []
random.seed(42)

if cluster_col:
    for cluster_name, group in df.groupby(cluster_col):
        # Sample per sentiment for diversity
        for label in ["POSITIVE", "NEGATIVE", "NEUTRAL"]:
            if sentiment_col in group.columns:
                label_df = group[group[sentiment_col].str.upper() == label]
            else:
                label_df = pd.DataFrame()

            if len(label_df) == 0:
                continue

            n = min(20, len(label_df))
            sampled = label_df.sample(n=n, random_state=42)

            for _, row in sampled.iterrows():
                text = str(row.get("reviews.text", ""))
                if len(text.strip()) < 5:
                    continue
                sample_reviews.append({
                    "text": text[:500],
                    "rating": int(row.get("reviews.rating", 0)),
                    "sentiment": str(label),
                    "product": str(row.get("name", "Unknown"))[:80],
                    "cluster": str(cluster_name),
                    "confidence": round(float(row.get("predicted_score", 0.0)), 3)
                        if "predicted_score" in row.index else None,
                })

random.shuffle(sample_reviews)
sample_reviews = sample_reviews[:500]  # cap total

with open(f"{OUTPUT_DIR}/reviews_sample.json", "w") as f:
    json.dump(sample_reviews, f, indent=2, ensure_ascii=False)
print(f"  Saved reviews_sample.json ({len(sample_reviews)} reviews)")

# ---------- DONE ----------
print(f"\n{'='*50}")
print(f"Webapp data generated in {OUTPUT_DIR}/")
print(f"  stats.json          - Dashboard overview")
print(f"  clusters.json       - Cluster summaries")
print(f"  products.json       - Product data + summaries")
print(f"  reviews_sample.json - Sample reviews for explorer")
print(f"\nNext: Copy webapp/ folder to your OVH hosting")
