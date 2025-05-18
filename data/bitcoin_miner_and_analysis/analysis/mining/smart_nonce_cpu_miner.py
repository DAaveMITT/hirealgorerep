import json
import struct
import hashlib
import requests
import pandas as pd

# CONFIG
RPC_USER = "username"
RPC_PASSWORD = "password123"
RPC_PORT = 8332
CSV_PATH = "smart_nonce_ranges.csv"
MAX_NONCES_TO_TRY = 1_000_000  # Tune as needed

def sha256d(data: bytes) -> bytes:
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
    data = response.json()
    print("❗ RPC response:", data)  # DEBUG
    return data["result"]

def calculate_merkle_root(txids):
    tx_hashes = [bytes.fromhex(txid)[::-1] for txid in txids]
    while len(tx_hashes) > 1:
        if len(tx_hashes) % 2 != 0:
            tx_hashes.append(tx_hashes[-1])
        tx_hashes = [
            sha256d(tx_hashes[i] + tx_hashes[i + 1])
            for i in range(0, len(tx_hashes), 2)
        ]
    return tx_hashes[0][::-1]

def difficulty_to_target(difficulty: float) -> int:
    max_target = 0xffff * 2**(8*(0x1d - 3))  # from Bitcoin source
    return int(max_target / difficulty)

def build_header(template, nonce, version_override=None):
    version = struct.pack("<I", version_override if version_override is not None else int(template["version"]))
    prev_block = bytes.fromhex(template["previousblockhash"])[::-1]
    txids = [tx["txid"] for tx in template["transactions"]]
    merkle_root = calculate_merkle_root(txids)
    timestamp = struct.pack("<I", int(template["curtime"]))
    bits = bytes.fromhex(template["bits"])[::-1]
    nonce_bytes = struct.pack("<I", nonce)
    header = version + prev_block + merkle_root + timestamp + bits + nonce_bytes
    return header

def main():
    print("🧠 Fetching block template...")
    template = get_block_template()
    
    target_hex = template["target"]
    target_int = int(target_hex, 16)
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

    target = difficulty_to_target(difficulty)
    print(f"🎯 Target: {hex(target)}")

    print("⛏️  Mining...")
    for nonce in range(start_nonce, min(end_nonce, start_nonce + MAX_NONCES_TO_TRY)):
        header = build_header(template, nonce)
        hash_result = sha256d(header)[::-1].hex()
        if int(hash_result, 16) < target:
            print(f"💥 Success! Nonce: {nonce}, Hash: {hash_result}")
            break
        if nonce % 100_000 == 0:
            print(f"Checked nonce: {nonce}, Hash: {hash_result}")

    print("✅ Done.")

if __name__ == "__main__":
    main()
