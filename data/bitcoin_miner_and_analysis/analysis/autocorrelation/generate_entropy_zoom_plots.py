import os
import json
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np  # ✅ ADD THIS


# === CONFIG ===
BLOCK_DIR = "C:/Users/15162/Desktop/bitcoinScriptNew/block_batches"
ANOMALY_CSV = "nonce_diff_entropy_anomalies.csv"  # Output from previous script
OUTPUT_DIR = "zoom_anomaly_plots"
WINDOW = 500  # Blocks before and after anomaly

os.makedirs(OUTPUT_DIR, exist_ok=True)

# === Load block data ===
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

# === Main Zoom-In Plot Generator ===
def generate_zoom_plots(df, anomalies):
    for _, row in anomalies.iterrows():
        anomaly_height = int(row["height"])
        start = anomaly_height - WINDOW
        end = anomaly_height + WINDOW

        zoom_df = df[(df["height"] >= start) & (df["height"] <= end)].copy()
        if zoom_df.empty:
            print(f"⚠️ Skipping anomaly at {anomaly_height}, no data in range.")
            continue

        plt.figure(figsize=(10, 5))
        plt.plot(zoom_df["height"], zoom_df["nonce_diff_entropy"], color="purple")
        plt.axvline(anomaly_height, color="red", linestyle="--", label="Anomaly")
        plt.title(f"Zoomed-In Entropy Around Anomaly @ Height {anomaly_height}")
        plt.xlabel("Block Height")
        plt.ylabel("Nonce Diff Entropy")
        plt.legend()
        plt.tight_layout()

        fname = f"anomaly_zoom_{anomaly_height}.png"
        plt.savefig(os.path.join(OUTPUT_DIR, fname))
        plt.close()
        print(f"📸 Saved zoom plot: {fname}")

# === Main Execution ===
if __name__ == "__main__":
    print("🔍 Loading block data...")
    blocks = load_blocks()
    df = pd.DataFrame(blocks)
    df["nonce_diff"] = df["nonce"].diff()
    df["height"] = pd.to_numeric(df["height"], errors="coerce")
    df = df.dropna()

    # === Load anomalies ===
    print("📁 Loading anomalies...")
    anomalies = pd.read_csv(ANOMALY_CSV)

    # === Recompute rolling entropy for accuracy ===
    def entropy(series):
        probs = series.value_counts(normalize=True)
        return -(probs * np.log2(probs.where(probs > 0, 1))).sum()


    print("🧠 Recomputing sliding entropy...")
    entropy_list = []
    heights = []
    for i in range(0, len(df) - 1000, 1000):
        chunk = df.iloc[i:i + 1000]
        e = entropy(chunk["nonce_diff"])
        entropy_list.append(e)
        heights.append(int(chunk["height"].iloc[-1]))

    entropy_df = pd.DataFrame({"height": heights, "nonce_diff_entropy": entropy_list})

    print("📊 Generating zoomed-in anomaly plots...")
    generate_zoom_plots(entropy_df, anomalies)

    print("✅ All zoom plots saved.")
