import os
import json
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from collections import Counter
from math import log2

BLOCK_DIR = "block_batches"

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

def calculate_entropy(data):
    counter = Counter(data)
    total = sum(counter.values())
    entropy = -sum((count/total) * log2(count/total) for count in counter.values())
    return entropy

def plot_nonce_entropy(df):
    nonces = df["nonce"].dropna().astype(int)
    entropy = calculate_entropy(nonces)
    plt.figure(figsize=(6, 4))
    plt.bar(["Nonce Entropy"], [entropy], color='skyblue')
    plt.title("Shannon Entropy of Nonce Values")
    plt.ylabel("Entropy (bits)")
    plt.tight_layout()
    plt.savefig("nonce_entropy.png")
    plt.close()
    print(f"🔢 Calculated Shannon entropy: {entropy:.4f} bits")

def build_dataframe(blocks):
    df = pd.DataFrame(blocks)
    df = df[["nonce"]].dropna()
    return df

if __name__ == "__main__":
    print("🔍 Loading block data...")
    blocks = load_blocks()
    print(f"📦 Loaded {len(blocks):,} blocks")

    print("🧮 Building DataFrame...")
    df = build_dataframe(blocks)

    print("📊 Calculating entropy of nonce values...")
    plot_nonce_entropy(df)

    print("✅ Entropy analysis complete. Plot saved.")
