import struct
import hashlib

# Function to compute double SHA-256 hash
def sha256d(data: bytes) -> bytes:
    return hashlib.sha256(hashlib.sha256(data).digest()).digest()

# List of block header data
block_headers = [
    {"height": 838845, "block_hash": "000000000000000000004d064568b0da3f4f6eaeed748ac81990eeb96bb55756", "prev_block": "000000000000000000032bc4346b6f80d8b2d7d9bf9cf4d755b6ce5bc47c25f1", "merkle_root": "85aaec003afe0a32a94d5e8901c895f736f75213e78c69daa63eabcdb65e5093", "time": 1712909444, "bits": "17034219", "nonce": 1194633778, "version": 820183040},
    # ... add more blocks as needed ...
]

# Verify each block header
for block in block_headers:
    print(f"\nVerifying block height {block['height']}...")

    # Construct the header (all fields must be little-endian)
    version = struct.pack("<I", block["version"])
    prev_block = bytes.fromhex(block["prev_block"])[::-1]
    merkle_root = bytes.fromhex(block["merkle_root"])[::-1]
    timestamp = struct.pack("<I", block["time"])
    bits = bytes.fromhex(block["bits"])[::-1]
    nonce = struct.pack("<I", block["nonce"])

    # 🔧 Combine all parts into the final 80-byte header
    header = version + prev_block + merkle_root + timestamp + bits + nonce

    # Hashing
    first_hash = hashlib.sha256(header).digest()
    second_hash = hashlib.sha256(first_hash).digest()
    computed_hash = second_hash[::-1].hex()
    expected_hash = block["block_hash"]

    print(f"Computed hash: {computed_hash}")
    print(f"Expected hash: {expected_hash}")
    print("MATCH ✅" if computed_hash == expected_hash else "MISMATCH ❌")
