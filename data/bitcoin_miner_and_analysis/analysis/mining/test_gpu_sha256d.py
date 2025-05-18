import cupy as cp
import hashlib
import struct
import time

# === CONFIG ===
START_NONCE = 0
END_NONCE = 1_000_000
TARGET_PREFIX = "000fffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff"
TARGET_BYTES = bytes.fromhex(TARGET_PREFIX.rjust(64, "0"))
TARGET_ARRAY = cp.asarray(list(TARGET_BYTES), dtype=cp.uint8)

# === Block Header Template (80 bytes) ===
version = struct.pack("<I", 536870912)
prev_block = bytes.fromhex("00" * 32)
merkle_root = bytes.fromhex("11" * 32)
timestamp = struct.pack("<I", 1710000000)
bits = bytes.fromhex("1d00ffff")[::-1]

header_prefix = version + prev_block + merkle_root + timestamp + bits  # 76 bytes
assert len(header_prefix) == 76, "Header prefix must be 76 bytes before nonce"

# === CPU SHA256d for now ===
def sha256d_batch(data):
    return [hashlib.sha256(hashlib.sha256(x.tobytes()).digest()).digest() for x in data]

# === Mining Function ===
def run_gpu_nonce_search():
    print("⚙️ Launching CuPy mining test on 1M nonces...")

    nonce_range = cp.arange(START_NONCE, END_NONCE, dtype=cp.uint32)
    header_matrix = cp.repeat(cp.frombuffer(header_prefix, dtype=cp.uint8)[cp.newaxis, :], END_NONCE - START_NONCE, axis=0)
    nonce_bytes = nonce_range.view(cp.uint8).reshape(-1, 4)
    full_headers = cp.concatenate((header_matrix, nonce_bytes), axis=1)

    assert full_headers.shape[1] == 80

    print("⚡ Running GPU hashing...")
    t0 = time.time()
    hashes = sha256d_batch(full_headers)
    elapsed = time.time() - t0
    print(f"✅ Completed in {elapsed:.4f} sec")

    # Convert hashes to byte arrays
    hash_array = cp.asarray([list(h[::-1]) for h in hashes], dtype=cp.uint8)  # shape (N, 32)

    # Compare each hash with the target byte-wise
    matches = cp.all(hash_array < TARGET_ARRAY, axis=1)
    matching_indices = cp.where(matches)[0]

    if len(matching_indices) > 0:
        print(f"🎯 Found {len(matching_indices)} matches under fake target:")
        for i in matching_indices.tolist():
            nonce = int(nonce_range[i].get())
            hash_hex = ''.join(f'{b:02x}' for b in hash_array[i].get()[::-1])
            print(f" - Nonce: {nonce}, Hash: {hash_hex}")
    else:
        print("❌ No matching hashes found.")

if __name__ == "__main__":
    run_gpu_nonce_search()
