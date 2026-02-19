"""
Cluster Visualization — Run in VS Code
Reads: data_with_clusters.csv, product_clusters.csv
Generates: cluster_scatter.png (matches presentation dark theme)
"""

import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import PCA

# ============================================================
# CONFIG — matches presentation theme
# ============================================================
BG = "#0f1117"
CARD_BG = "#1a1d27"
WHITE = "#e2e4ea"
MUTED = "#8b8f9e"
GRID = "#2a2e3a"

CLUSTER_COLORS = {
    "Fire Tablets":           "#4f8fff",  # blue
    "Batteries & Household":  "#fbbf24",  # yellow
    "E-Readers":              "#34d399",  # green
    "Smart Speakers":         "#a78bfa",  # purple
    "Accessories":            "#f87171",  # red
    "Media & Home":           "#06b6d4",  # cyan
}

# ============================================================
# LOAD DATA
# ============================================================
df = pd.read_csv("data_with_clusters.csv")
products = df.groupby("name").agg({
    "cluster_name": "first",
    "categories": "first",
    "reviews.rating": "mean",
    "reviews.text": "count"
}).reset_index()
products.columns = ["name", "cluster", "categories", "avg_rating", "review_count"]

# ============================================================
# TF-IDF + PCA (same method as clustering notebook)
# ============================================================
text_features = products["name"] + " " + products["categories"].fillna("")
tfidf = TfidfVectorizer(max_features=200, ngram_range=(1, 2), stop_words="english")
X = tfidf.fit_transform(text_features)

pca = PCA(n_components=2, random_state=42)
coords = pca.fit_transform(X.toarray())
products["x"] = coords[:, 0]
products["y"] = coords[:, 1]

# ============================================================
# PLOT — tall format for slide half
# ============================================================
fig, ax = plt.subplots(figsize=(12, 7))
fig.patch.set_facecolor(BG)
ax.set_facecolor(BG)

for cluster_name, group in products.groupby("cluster"):
    color = CLUSTER_COLORS.get(cluster_name, MUTED)
    sizes = np.clip(group["review_count"] / 30, 20, 300)
    
    ax.scatter(group["x"], group["y"],
               c=color, s=sizes, alpha=0.7,
               edgecolors=color, linewidths=1.5,
               label=f"{cluster_name} ({len(group)})", zorder=3)

# Label top products (largest per cluster)
for cluster_name, group in products.groupby("cluster"):
    top = group.nlargest(1, "review_count").iloc[0]
    # Shorten name for display
    short_name = top["name"]
    if len(short_name) > 30:
        short_name = short_name[:28] + "..."
    color = CLUSTER_COLORS.get(cluster_name, MUTED)
    ax.annotate(short_name, xy=(top["x"], top["y"]),
                xytext=(8, 8), textcoords="offset points",
                fontsize=7, color=color, alpha=0.9,
                fontweight="bold")

ax.set_title("Product Clusters (TF-IDF + PCA)", fontsize=14,
             fontweight="bold", color=WHITE, pad=15)
ax.set_xlabel("PCA Component 1", fontsize=11, color=MUTED)
ax.set_ylabel("PCA Component 2", fontsize=11, color=MUTED)

ax.legend(loc="upper left", fontsize=8.5, facecolor=CARD_BG,
          edgecolor=GRID, labelcolor=WHITE, markerscale=0.7)

ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.spines["bottom"].set_color(GRID)
ax.spines["left"].set_color(GRID)
ax.tick_params(colors=MUTED)
ax.grid(color=GRID, alpha=0.3)

plt.tight_layout(pad=1.0)
plt.savefig("cluster_scatter.png", dpi=250, bbox_inches="tight", facecolor=BG)
plt.close()
print("Saved cluster_scatter.png")
