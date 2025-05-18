import json
import struct
import hashlib
import requests
import pandas as pd
import cupy as cp

# CONFIG
RPC_USER = "username"
RPC_PASSWORD = "password123"
RPC_PORT = 8332
CSV_PATH = "smart_nonce_ranges.csv"
NONCES_PER_BATCH = 1_000_000  # Try 1 million nonces per batch on GPU

def sha256d_cpu(data: bytes) -> bytes:
    return hashlib.sha256(hashlib.sha256(data).digest()).digest()

def get_block_template():
    url = f"http://localhost:{RPC_PORT}"
    headers = {'content-type': 'application/json'}
    payload = {
        "method": "getblocktemplate",
        "params": [{"rules": ["segwit"]}],
        "jsonrpc": "2.0",
        "id": 0,
    }
    response = requests.post(url, data=json.dumps(payload), headers=headers, auth=(RPC_USER, RPC_PASSWORD))
    return response.json()["result"]

def difficulty_to_target(difficulty: float) -> int:
    max_target = 0xffff * 2**(8*(0x1d - 3))
    return int(max_target / difficulty)

def calculate_merkle_root(txids):
    tx_hashes = [bytes.fromhex(txid)[::-1] for txid in txids]
    while len(tx_hashes) > 1:
        if len(tx_hashes) % 2 != 0:
            tx_hashes.append(tx_hashes[-1])
        tx_hashes = [
            sha256d_cpu(tx_hashes[i] + tx_hashes[i + 1])
            for i in range(0, len(tx_hashes), 2)
        ]
    return tx_hashes[0][::-1]

def build_header_prefix(template, version_override=None):
    version = struct.pack("<I", version_override if version_override is not None else int(template["version"]))
    prev_block = bytes.fromhex(template["previousblockhash"])[::-1]
    txids = [tx["txid"] for tx in template["transactions"]]
    merkle_root = calculate_merkle_root(txids)
    timestamp = struct.pack("<I", int(template["curtime"]))
    bits = bytes.fromhex(template["bits"])[::-1]
    return version + prev_block + merkle_root + timestamp + bits

def uint256_to_u32_array(value: int):
    return cp.array([(value >> (32 * i)) & 0xffffffff for i in reversed(range(8))], dtype=cp.uint32)

def run_gpu_mining(header_prefix: bytes, start_nonce: int, end_nonce: int, target: int):
    nonce_range = cp.arange(start_nonce, end_nonce, dtype=cp.uint32)
    target_words = uint256_to_u32_array(target)

    print(f"🚀 Trying {len(nonce_range):,} nonces on GPU...")

    found_nonce = -1
    for nonce in nonce_range:
        full_header = header_prefix + struct.pack("<I", int(nonce.get()))
        digest = sha256d_cpu(full_header)
        hash_words = cp.array(struct.unpack(">8L", digest), dtype=cp.uint32)
        if cp.all(hash_words < target_words):
            found_nonce = int(nonce.get())
            break

    return found_nonce

def main():
    print("🧠 Fetching block template...")
    template = get_block_template()
    target_int = int(template["target"], 16)
    max_target = 0xffff * 2**(8*(0x1d - 3))
    difficulty = max_target / target_int
    version = int(template["version"])

    print(f"📊 Block difficulty: {difficulty}")
    print(f"🔢 Block version: {version}")

    df = pd.read_csv(CSV_PATH)
    difficulty_bin = int(difficulty // 10000000)
    version_bin = (version >> 24) & 0xFF

    matching = df[(df["difficulty_bin"] == difficulty_bin) & (df["version_bin"] == version_bin)]
    if matching.empty:
        print("⚠️ No smart range found. Using full range...")
        start_nonce = 0
        end_nonce = 0xFFFFFFFF
    else:
        row = matching.iloc[0]
        start_nonce = int(row["recommended_start"])
        end_nonce = int(row["recommended_end"])
        print(f"🎯 Using smart nonce range: {start_nonce} - {end_nonce}")

    print("⚙️ Building header prefix...")
    header_prefix = build_header_prefix(template)

    print("⚡ Mining on GPU...")
    nonce = run_gpu_mining(header_prefix, start_nonce, start_nonce + NONCES_PER_BATCH, target_int)

    if nonce != -1:
        print(f"💥 Success! Found nonce: {nonce}")
    else:
        print("❌ No valid nonce found in batch.")

if __name__ == "__main__":
    main()
