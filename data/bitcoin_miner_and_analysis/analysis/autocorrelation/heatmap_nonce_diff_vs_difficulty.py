import os
import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

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

def build_nonce_diff_and_difficulty_df(blocks):
    df = pd.DataFrame(blocks)
    df = df[["height", "nonce", "difficulty"]].dropna().sort_values("height")
    df["nonce_diff"] = df["nonce"].diff()
    df = df.dropna()
    return df

def plot_heatmap(df, bins_nonce=50, bins_difficulty=50):
    plt.figure(figsize=(12, 8))
    heatmap_data = pd.DataFrame({
        "nonce_diff": df["nonce_diff"],
        "difficulty": df["difficulty"]
    })

    heatmap_data["nonce_bin"] = pd.cut(heatmap_data["nonce_diff"], bins=bins_nonce)
    heatmap_data["difficulty_bin"] = pd.cut(heatmap_data["difficulty"], bins=bins_difficulty)

    grouped = heatmap_data.groupby(["nonce_bin", "difficulty_bin"]).size().unstack().fillna(0)

    sns.heatmap(grouped, cmap="viridis", norm=None)
    plt.title("Heatmap: Nonce Diff vs. Difficulty")
    plt.xlabel("Difficulty Bin")
    plt.ylabel("Nonce Diff Bin")
    plt.tight_layout()
    plt.savefig("heatmap_nonce_diff_vs_difficulty.png")
    plt.close()

if __name__ == "__main__":
    print("🔍 Loading block data...")
    blocks = load_blocks()
    print(f"📦 Loaded {len(blocks):,} blocks")

    print("🧮 Preparing DataFrame...")
    df = build_nonce_diff_and_difficulty_df(blocks)

    print("📊 Plotting heatmap of nonce_diff vs difficulty...")
    plot_heatmap(df)

    print("✅ Heatmap saved as heatmap_nonce_diff_vs_difficulty.png")
