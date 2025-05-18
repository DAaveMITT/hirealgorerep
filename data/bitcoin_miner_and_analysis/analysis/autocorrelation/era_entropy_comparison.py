import os
import json
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import entropy

BLOCK_DIR = "C:/Users/15162/Desktop/bitcoinScriptNew/block_batches"

# Define eras by block height (approximate)
ERAS = {
    "2010–2013": (0, 250000),
    "2014–2016": (250001, 420000),
    "2017–2020": (420001, 650000),
    "2021–2024": (650001, 900000),
}

def load_blocks():
    blocks = []
    for fname in os.listdir(BLOCK_DIR):
        if fname.endswith(".jsonl"):
            with open(os.path.join(BLOCK_DIR, fname), "r") as f:
                for line in f:
                    try:
                        blocks.append(json.loads(line))
                    except:
                        continue
    return blocks

def compute_entropy(series, bins=256):
    counts, _ = np.histogram(series, bins=bins)
    probs = counts / counts.sum()
    return entropy(probs, base=2)

def filter_era(df, start, end):
    return df[(df["height"] >= start) & (df["height"] <= end)].copy()

def main():
    print("🔍 Loading block data...")
    blocks = load_blocks()
    df = pd.DataFrame(blocks)[["height", "nonce"]].dropna()
    df.sort_values("height", inplace=True)

    results = []

    for era, (start, end) in ERAS.items():
        era_df = filter_era(df, start, end)
        era_df["nonce_diff"] = era_df["nonce"].diff()
        entropy_val = compute_entropy(era_df["nonce_diff"].dropna())
        results.append((era, entropy_val))
        print(f"{era}: {entropy_val:.3f} bits")

    # Plot
    eras = [r[0] for r in results]
    entropy_vals = [r[1] for r in results]

    plt.figure(figsize=(10, 6))
    bars = plt.bar(eras, entropy_vals, color="skyblue")
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, yval + 0.1, f"{yval:.2f}", ha="center", va="bottom")

    plt.title("Nonce Diff Entropy by Era")
    plt.ylabel("Shannon Entropy (bits)")
    plt.ylim(0, 9)
    plt.tight_layout()
    plt.savefig("era_nonce_entropy.png")
    plt.close()
    print("✅ Saved as era_nonce_entropy.png")

if __name__ == "__main__":
    main()
