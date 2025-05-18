import os
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import zscore

# === CONFIG ===
BLOCK_DIR = "C:/Users/15162/Desktop/bitcoinScriptNew/block_batches"
FIELD = "nonce"
WINDOW_SIZE = 1000
Z_THRESHOLD = 2.5

# === Load blocks ===
def load_blocks():
    blocks = []
    for fname in os.listdir(BLOCK_DIR):
        if fname.endswith(".jsonl"):
            with open(os.path.join(BLOCK_DIR, fname), "r") as f:
                for line in f:
                    try:
                        block = json.loads(line)
                        blocks.append(block)
                    except json.JSONDecodeError:
                        continue
    return blocks

# === Compute sliding entropy ===
def compute_entropy(values):
    value_counts = pd.Series(values).value_counts(normalize=True)
    entropy = -np.sum(value_counts * np.log2(value_counts))
    return entropy

def compute_sliding_entropy(blocks, field, window):
    df = pd.DataFrame(blocks)
    df = df[["height", field]].dropna()
    df = df.sort_values("height")
    df["diff"] = df[field].diff()
    entropies = []
    heights = []
    for i in range(0, len(df) - window):
        window_values = df["diff"].iloc[i:i+window].dropna()
        entropy = compute_entropy(window_values)
        entropies.append(entropy)
        heights.append(df["height"].iloc[i + window])
    return pd.DataFrame({"height": heights, "entropy": entropies})

# === Detect anomalies ===
def detect_anomalies(entropy_df, z_thresh=2.5):
    entropy_df["zscore"] = zscore(entropy_df["entropy"])
    return entropy_df[np.abs(entropy_df["zscore"]) > z_thresh]

# === Plot ===
def plot_entropy_with_anomalies(entropy_df, anomalies):
    plt.figure(figsize=(12, 6))
    plt.plot(entropy_df["height"], entropy_df["entropy"], label="Entropy", color="purple")
    plt.scatter(anomalies["height"], anomalies["entropy"], color="red", label="Anomaly")
    plt.axhline(entropy_df["entropy"].mean(), color="gray", linestyle="--", label="Mean")
    plt.title(f"Nonce Diff Entropy with Anomalies (Z > {Z_THRESHOLD})")
    plt.xlabel("Block Height")
    plt.ylabel("Entropy (bits)")
    plt.legend()
    plt.tight_layout()
    plt.savefig("nonce_diff_entropy_anomalies.png")
    plt.close()

# === Run ===
if __name__ == "__main__":
    print("🔍 Loading blocks...")
    blocks = load_blocks()
    print("📈 Calculating entropy...")
    entropy_df = compute_sliding_entropy(blocks, FIELD, WINDOW_SIZE)
    print("🚨 Detecting anomalies...")
    anomalies = detect_anomalies(entropy_df)
    print(f"🧠 Found {len(anomalies)} anomalous regions")

    print("💾 Saving to CSV...")
    anomalies.to_csv("nonce_diff_entropy_anomalies.csv", index=False)

    print("📊 Plotting...")
    plot_entropy_with_anomalies(entropy_df, anomalies)

    print("✅ Done. Results saved.")
