import os
import json
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import skew, kurtosis

BLOCK_DIR = "block_batches"
NUMERIC_FIELDS = ["height", "version", "time", "nonce", "difficulty", "tx_count"]

def load_blocks():
    all_blocks = []
    for fname in os.listdir(BLOCK_DIR):
        if fname.endswith(".jsonl"):
            with open(os.path.join(BLOCK_DIR, fname), "r") as f:
                for line in f:
                    try:
                        block = json.loads(line)
                        all_blocks.append(block)
                    except json.JSONDecodeError:
                        continue
    return all_blocks

def build_dataframe(blocks):
    df = pd.DataFrame(blocks)
    df = df[NUMERIC_FIELDS].dropna()
    return df

def advanced_statistics(df):
    print("\n📈 Descriptive Statistics:")
    print(df.describe().T)

    print("\n📊 Skewness:")
    print(df.apply(skew).round(3))

    print("\n📐 Kurtosis:")
    print(df.apply(kurtosis).round(3))

    print("\n🎯 Nonce Range Insight:")
    print(f"Min: {df['nonce'].min()}, Max: {df['nonce'].max()}")
    print(f"Percentiles: 25%={np.percentile(df['nonce'], 25)}, 50%={np.percentile(df['nonce'], 50)}, 75%={np.percentile(df['nonce'], 75)}")

def plot_matrix(df):
    corr = df.corr()
    plt.figure(figsize=(12, 10))
    sns.heatmap(corr, annot=True, cmap="coolwarm", fmt=".2f")
    plt.title("🔥 Correlation Matrix: Bitcoin Block Header Intelligence")
    plt.tight_layout()
    plt.show()

def plot_nonce_distribution(df):
    plt.figure(figsize=(10, 6))
    sns.histplot(df['nonce'], bins=100, kde=True, color='orange')
    plt.axvline(x=df['nonce'].mean(), color='blue', linestyle='--', label='Mean')
    plt.axvline(x=df['nonce'].median(), color='green', linestyle='--', label='Median')
    plt.title("🎲 Nonce Value Distribution Across Blocks")
    plt.xlabel("Nonce")
    plt.ylabel("Frequency")
    plt.legend()
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    print("🔍 Loading block data...")
    blocks = load_blocks()
    print(f"📦 Loaded {len(blocks):,} blocks")

    df = build_dataframe(blocks)

    print("🧠 Performing statistical analysis...")
    advanced_statistics(df)

    print("📊 Plotting correlation matrix...")
    plot_matrix(df)

    print("📉 Plotting nonce distribution...")
    plot_nonce_distribution(df)
