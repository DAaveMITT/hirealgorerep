import os
import json
import pandas as pd
import numpy as np

# === CONFIG ===
BLOCK_DIR = "C:/Users/15162/Desktop/bitcoinScriptNew/block_batches"
OUTPUT_FILE = "smart_nonce_ranges.csv"
DIFFICULTY_BINS = 10
VERSION_BINS = 5

# === Load All Blocks ===
def load_blocks():
    blocks = []
    for fname in os.listdir(BLOCK_DIR):
        if fname.endswith(".jsonl"):
            with open(os.path.join(BLOCK_DIR, fname), "r") as f:
                for line in f:
                    try:
                        block = json.loads(line)
                        blocks.append(block)
                    except:
                        continue
    return pd.DataFrame(blocks)

# === Build Prediction Table ===
def build_smart_nonce_table(df):
    df = df[["height", "difficulty", "version", "nonce"]].dropna()
    df = df[df["nonce"] > 0]
    df = df.sort_values("height")
    df["nonce_diff"] = df["nonce"].diff().fillna(0)
    df["difficulty_bin"] = pd.qcut(df["difficulty"], DIFFICULTY_BINS, labels=False, duplicates="drop")
    df["version_bin"] = pd.qcut(df["version"], VERSION_BINS, labels=False, duplicates="drop")

    grouped = df.groupby(["difficulty_bin", "version_bin"])
    summary = grouped["nonce"].agg([
        ("recommended_start", "min"),
        ("recommended_end", "max"),
        ("avg_nonce", "mean"),
        ("stddev", "std"),
        ("samples", "count")
    ]).reset_index()

    summary.to_csv(OUTPUT_FILE, index=False)
    print(f"✅ Saved smart nonce range table to: {OUTPUT_FILE}")

# === Run ===
if __name__ == "__main__":
    print("🔍 Loading blocks...")
    df = load_blocks()
    if df.empty:
        print("❌ No blocks found. Check your BLOCK_DIR.")
    else:
        print(f"📦 Loaded {len(df):,} blocks")
        build_smart_nonce_table(df)
