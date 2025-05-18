
import os
import json
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans

# === CONFIG ===
BLOCK_DIR = "C:/Users/15162/Desktop/bitcoinScriptNew/block_batches"
NUMERIC_FIELDS = ["height", "version", "time", "nonce", "difficulty", "tx_count"]

# === Step 1: Load all blocks ===
def load_blocks():
    all_blocks = []
    for fname in os.listdir(BLOCK_DIR):
        if fname.endswith(".jsonl"):
            with open(os.path.join(BLOCK_DIR, fname), "r") as f:
                for line in f:
                    try:
                        block = json.loads(line)
                        all_blocks.append(block)
                    except json.JSONDecodeError:
                        continue
    return all_blocks

# === Step 2: Convert to DataFrame ===
def build_dataframe(blocks):
    df = pd.DataFrame(blocks)
    df = df[NUMERIC_FIELDS]
    df = df.dropna()
    return df

# === Step 3: Correlation Matrix ===
def plot_correlation_matrix(df):
    corr = df.corr()
    plt.figure(figsize=(10, 8))
    sns.heatmap(corr, annot=True, cmap="coolwarm", fmt=".2f")
    plt.title("Correlation Matrix of Bitcoin Block Data")
    plt.tight_layout()
    plt.savefig("correlation_matrix.png")
    plt.close()

# === Step 4: PCA + Clustering ===
def run_pca_and_cluster(df, n_clusters=4):
    features = df[["version", "nonce", "difficulty"]]
    pca = PCA(n_components=2)
    pca_result = pca.fit_transform(features)

    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    labels = kmeans.fit_predict(pca_result)

    plt.figure(figsize=(10, 6))
    plt.scatter(pca_result[:, 0], pca_result[:, 1], c=labels, cmap="Set2", alpha=0.7)
    plt.title("PCA + KMeans Clustering of Block Headers")
    plt.xlabel("PCA Component 1")
    plt.ylabel("PCA Component 2")
    plt.tight_layout()
    plt.savefig("pca_kmeans_clusters.png")
    plt.close()

# === Step 5: Trend Visualization ===
def plot_field_trends(df):
    plt.figure(figsize=(12, 6))
    for field in ["difficulty", "nonce", "version"]:
        plt.plot(df["height"], df[field], label=field, alpha=0.6)
    plt.title("Bitcoin Block Field Trends Over Time")
    plt.xlabel("Block Height")
    plt.ylabel("Value")
    plt.legend()
    plt.tight_layout()
    plt.savefig("field_trends.png")
    plt.close()

# === MAIN PIPELINE ===
if __name__ == "__main__":
    print("🔍 Loading block data...")
    blocks = load_blocks()
    print(f"📦 Loaded {len(blocks):,} blocks")

    print("🧮 Building DataFrame...")
    df = build_dataframe(blocks)

    print("📊 Generating correlation matrix...")
    plot_correlation_matrix(df)

    print("🧠 Running PCA + KMeans clustering...")
    run_pca_and_cluster(df)

    print("📈 Plotting field trends over height...")
    plot_field_trends(df)

    print("✅ Analysis complete. Plots saved to working directory.")
