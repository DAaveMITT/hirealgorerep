import os
import json
import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.graphics.tsaplots import plot_acf

BLOCK_DIR = "C:/Users/15162/Desktop/bitcoinScriptNew/block_batches"
FIELD = "nonce"  # Change to 'difficulty' or other fields as needed

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
    df = df[["height", FIELD]].dropna()
    df.sort_values("height", inplace=True)
    return df

def plot_autocorrelation(df):
    plt.figure(figsize=(10, 6))
    plot_acf(df[FIELD], lags=50)
    plt.title(f"Autocorrelation of {FIELD}")
    plt.xlabel("Lag")
    plt.ylabel("Autocorrelation")
    plt.tight_layout()
    plt.savefig(f"{FIELD}_autocorrelation.png")
    plt.close()

if __name__ == "__main__":
    print("🔍 Loading block data...")
    blocks = load_blocks()
    print(f"📦 Loaded {len(blocks):,} blocks")

    print("🧮 Building DataFrame...")
    df = build_dataframe(blocks)

    print(f"📊 Plotting autocorrelation for {FIELD}...")
    plot_autocorrelation(df)

    print("✅ Autocorrelation analysis complete. Plot saved.")
