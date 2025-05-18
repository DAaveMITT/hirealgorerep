import os
import json
import pandas as pd
import numpy as np

BLOCK_DIR = "block_batches"
OUTPUT_FILE = "engineered_block_features.csv"

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

def build_dataframe(blocks):
    df = pd.DataFrame(blocks)
    df = df[["height", "version", "nonce", "difficulty"]].dropna()
    df.sort_values("height", inplace=True)
    return df

def engineer_features(df):
    df["nonce_diff"] = df["nonce"].diff().fillna(0)
    df["difficulty_log"] = np.log(df["difficulty"])
    df["version_jump"] = (df["version"].diff() != 0).astype(int)
    return df

if __name__ == "__main__":
    print("🔍 Loading block data...")
    blocks = load_blocks()
    print(f"📦 Loaded {len(blocks):,} blocks")

    print("🧮 Building DataFrame...")
    df = build_dataframe(blocks)

    print("🛠️ Engineering features...")
    df = engineer_features(df)

    print(f"💾 Saving engineered features to {OUTPUT_FILE}...")
    df.to_csv(OUTPUT_FILE, index=False)

    print("✅ Feature engineering complete.")
