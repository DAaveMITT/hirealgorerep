import os
import json
import pandas as pd
import matplotlib.pyplot as plt

BLOCK_DIR = "C:/Users/15162/Desktop/bitcoinScriptNew/block_batches"

def load_blocks():
    blocks = []
    for fname in os.listdir(BLOCK_DIR):
        if fname.endswith(".jsonl"):
            with open(os.path.join(BLOCK_DIR, fname), "r") as f:
                for line in f:
                    try:
                        blocks.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
    return blocks

def build_nonce_diff_series(blocks):
    df = pd.DataFrame(blocks)
    df = df[["height", "nonce"]].dropna().sort_values("height")
    df["nonce_diff"] = df["nonce"].diff()
    return df["nonce_diff"].dropna()

def plot_nonce_diff_histogram(nonce_diff_series):
    plt.figure(figsize=(12, 6))
    plt.hist(nonce_diff_series, bins=100, color="purple", alpha=0.75, edgecolor="black")
    plt.title("Histogram of Nonce Differences")
    plt.xlabel("Nonce Difference")
    plt.ylabel("Frequency")
    plt.tight_layout()
    plt.savefig("nonce_diff_histogram.png")
    plt.close()

if __name__ == "__main__":
    print("🔍 Loading block data...")
    blocks = load_blocks()
    print(f"📦 Loaded {len(blocks):,} blocks")

    print("🧮 Computing nonce differences...")
    nonce_diff_series = build_nonce_diff_series(blocks)

    print("📊 Plotting histogram of nonce_diff...")
    plot_nonce_diff_histogram(nonce_diff_series)

    print("✅ Histogram saved as nonce_diff_histogram.png")
