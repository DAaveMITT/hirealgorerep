import os
import json
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Directory containing JSONL files
BLOCK_DIR = "block_batches"

# Fields you want to analyze
NUMERIC_FIELDS = ["height", "version", "time", "nonce", "difficulty", "tx_count"]

# Step 1: Load all blocks
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

# Step 2: Convert to DataFrame
def build_dataframe(blocks):
    df = pd.DataFrame(blocks)
    df = df[NUMERIC_FIELDS]  # Keep only relevant fields
    df = df.dropna()  # Drop any rows with missing values
    return df

# Step 3: Generate correlation matrix
def plot_correlation_matrix(df):
    corr = df.corr()
    plt.figure(figsize=(10, 8))
    sns.heatmap(corr, annot=True, cmap="coolwarm", fmt=".2f")
    plt.title("Correlation Matrix of Bitcoin Block Data")
    plt.tight_layout()
    plt.show()

# Run the pipeline
if __name__ == "__main__":
    print("🔍 Loading block data...")
    blocks = load_blocks()
    print(f"📦 Loaded {len(blocks):,} blocks")
    df = build_dataframe(blocks)
    print("📊 Computing correlation matrix...")
    plot_correlation_matrix(df)
