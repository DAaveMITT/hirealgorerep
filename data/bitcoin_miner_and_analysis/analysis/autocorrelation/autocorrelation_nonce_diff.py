import os
import json
import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.graphics.tsaplots import plot_acf

BLOCK_DIR = "C:/Users/15162/Desktop/bitcoinScriptNew/block_batches"
FIELD = "nonce"

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

def build_nonce_diff_series(blocks):
    df = pd.DataFrame(blocks)
    df = df[["height", FIELD]].dropna()
    df.sort_values("height", inplace=True)
    df["nonce_diff"] = df[FIELD].diff()  # difference between consecutive nonces
    df = df.dropna()
    return df

def plot_autocorrelation(df):
    plt.figure(figsize=(10, 6))
    plot_acf(df["nonce_diff"], lags=50)
    plt.title("Autocorrelation of Nonce Differences")
    plt.xlabel("Lag")
    plt.ylabel("Autocorrelation")
    plt.tight_layout()
    plt.savefig("nonce_diff_autocorrelation.png")
    plt.close()

if __name__ == "__main__":
    print("🔍 Loading block data...")
    blocks = load_blocks()
    print(f"📦 Loaded {len(blocks):,} blocks")

    print("🧮 Computing nonce differences...")
    df = build_nonce_diff_series(blocks)

    print("📊 Plotting autocorrelation of nonce differences...")
    plot_autocorrelation(df)

    print("✅ Plot saved as nonce_diff_autocorrelation.png")
