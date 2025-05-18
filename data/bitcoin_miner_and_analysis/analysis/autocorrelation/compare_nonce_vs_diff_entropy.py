import os
import json
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import entropy

BLOCK_DIR = "../../block_batches"  # adjust path as needed
WINDOW_SIZE = 1000

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

def main():
    print("🔍 Loading block data...")
    blocks = load_blocks()
    df = pd.DataFrame(blocks)[["height", "nonce"]].dropna()
    df.sort_values("height", inplace=True)
    df["nonce_diff"] = df["nonce"].diff()

    heights = []
    nonce_entropy = []
    diff_entropy = []

    for i in range(0, len(df) - WINDOW_SIZE, WINDOW_SIZE):
        chunk = df.iloc[i:i+WINDOW_SIZE]
        heights.append(chunk["height"].iloc[-1])

        n_entropy = compute_entropy(chunk["nonce"])
        d_entropy = compute_entropy(chunk["nonce_diff"].dropna())

        nonce_entropy.append(n_entropy)
        diff_entropy.append(d_entropy)

    # Plot both
    plt.figure(figsize=(12, 6))
    plt.plot(heights, nonce_entropy, label="Entropy(nonce)", color="orange")
    plt.plot(heights, diff_entropy, label="Entropy(nonce_diff)", color="purple")
    plt.title(f"Nonce vs Nonce Diff Entropy Over Time ({WINDOW_SIZE}-block windows)")
    plt.xlabel("Block Height")
    plt.ylabel("Shannon Entropy (bits)")
    plt.legend()
    plt.tight_layout()
    plt.savefig("compare_nonce_vs_diff_entropy.png")
    plt.close()

    print("✅ Saved as compare_nonce_vs_diff_entropy.png")

if __name__ == "__main__":
    main()
