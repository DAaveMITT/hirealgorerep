import os
import json
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import entropy
import numpy as np

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

def compute_entropy(series, bins=256):
    counts, _ = np.histogram(series, bins=bins)
    probs = counts / counts.sum()
    return entropy(probs, base=2)

def build_nonce_diff_entropy_series(df, window=1000):
    entropies = []
    heights = []

    for i in range(0, len(df) - window, window):
        chunk = df.iloc[i:i + window]
        diffs = chunk["nonce"].diff().dropna()
        e = compute_entropy(diffs)
        entropies.append(e)
        heights.append(chunk["height"].iloc[-1])

    return pd.DataFrame({"height": heights, "entropy": entropies})

def main():
    print("🔍 Loading block data...")
    blocks = load_blocks()
    print(f"📦 Loaded {len(blocks):,} blocks")

    df = pd.DataFrame(blocks)[["height", "nonce"]].dropna()
    df = df.sort_values("height")

    print("📊 Computing entropy of nonce_diff in sliding windows...")
    result_df = build_nonce_diff_entropy_series(df, window=1000)

    print("📈 Plotting entropy over time...")
    plt.figure(figsize=(12, 6))
    plt.plot(result_df["height"], result_df["entropy"], label="Entropy (nonce_diff)", color="purple")
    plt.xlabel("Block Height")
    plt.ylabel("Shannon Entropy (bits)")
    plt.title("Sliding Window Entropy of Nonce Differences (1000-block chunks)")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("entropy_nonce_diff_over_time.png")
    plt.close()
    print("✅ Plot saved as entropy_nonce_diff_over_time.png")

if __name__ == "__main__":
    main()
