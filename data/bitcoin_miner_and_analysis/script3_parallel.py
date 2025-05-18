import subprocess
import json
import time
import os
from multiprocessing import Process, cpu_count
from math import ceil

# CONFIG
RPC_USER = "username"
RPC_PASSWORD = "password123"
START_HEIGHT = 0
END_HEIGHT = 894763
NUM_WORKERS = 16  # or use: cpu_count()
OUTPUT_DIR = "block_batches"
BATCH_SIZE = ceil((END_HEIGHT - START_HEIGHT + 1) / NUM_WORKERS)

os.makedirs(OUTPUT_DIR, exist_ok=True)

def run_bitcoin_cli(command, retries=3, delay=2, timeout=30):
    cmd = ["bitcoin-cli", f"-rpcuser={RPC_USER}", f"-rpcpassword={RPC_PASSWORD}"] + command
    for attempt in range(retries):
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=timeout)
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            if "Block not available" in e.stderr:
                return None
            print(f"[ERROR] {command}: {e.stderr.strip()}")
        except subprocess.TimeoutExpired:
            print(f"[TIMEOUT] {command}")
        time.sleep(delay * (attempt + 1))
    return None

def fetch_block_data(height):
    block_hash = run_bitcoin_cli(["getblockhash", str(height)])
    if not block_hash:
        return None

    header_data = run_bitcoin_cli(["getblockheader", block_hash])
    if not header_data:
        return None

    try:
        header = json.loads(header_data)
        block_info = {
            "height": header["height"],
            "block_hash": header["hash"],
            "prev_block": header.get("previousblockhash", ""),
            "merkle_root": header["merkleroot"],
            "time": header["time"],
            "bits": header["bits"],
            "nonce": header["nonce"],
            "version": header["version"],
            "difficulty": header["difficulty"],
            "chainwork": header["chainwork"],
            "tx_count": 0
        }

        block_data = run_bitcoin_cli(["getblock", block_hash, "1"])
        if block_data:
            block = json.loads(block_data)
            block_info["tx_count"] = block.get("nTx", 0)

        return block_info
    except Exception as e:
        print(f"[ERROR] Parsing block {height}: {e}")
        return None

def get_last_saved_height(file_path, fallback_start):
    if not os.path.exists(file_path):
        return fallback_start
    try:
        with open(file_path, "r") as f:
            lines = f.readlines()
            for line in reversed(lines):
                try:
                    obj = json.loads(line)
                    return obj["height"] + 1
                except:
                    continue
        return fallback_start
    except:
        return fallback_start

def run_worker(start, end):
    output_file = os.path.join(OUTPUT_DIR, f"block_headers_{start}_{end}.jsonl")
    resume_height = get_last_saved_height(output_file, start)

    print(f"[Worker {start}-{end}] Starting at {resume_height}")

    with open(output_file, "a") as f:
        for height in range(resume_height, end + 1):
            block_data = fetch_block_data(height)
            if block_data:
                f.write(json.dumps(block_data) + "\n")
                print(f"✅ [{start}-{end}] Height {height}")
            else:
                print(f"⚠️ [{start}-{end}] Skipped {height}")
            time.sleep(0.25)  # prevent CLI overload

def main():
    jobs = []
    for i in range(NUM_WORKERS):
        chunk_start = START_HEIGHT + i * BATCH_SIZE
        chunk_end = min(chunk_start + BATCH_SIZE - 1, END_HEIGHT)
        p = Process(target=run_worker, args=(chunk_start, chunk_end))
        jobs.append(p)
        p.start()
        time.sleep(2)  # stagger to avoid overload

    for job in jobs:
        job.join()

if __name__ == "__main__":
    main()
