import struct
import hashlib

def sha256d(data: bytes) -> bytes:
    return hashlib.sha256(hashlib.sha256(data).digest()).digest()

# Your 4 blocks
block_headers = [
    {
        "height": 782922,
        "block_hash": "000000000000000000041cf502c1170b61e7278c57c9ef72997572adac553827",
        "prev_block": "000000000000000000057b1645c4ef4745a9f308c4d43848c4c6337d1ef44492",
        "merkle_root": "5565150dfb2dd2cceee9b78b8ebdb223d37bd48f3730e477d9e89dcbd6ab36d5",
        "time": 1680025043,
        "bits": "1706023e",
        "nonce": 196152130,
        "version": 538968064
    },
    {
        "height": 782923,
        "block_hash": "000000000000000000019e1ed73bbb6fa53fc600c7eb93b3ad7b469a8c4941a6",
        "prev_block": "000000000000000000041cf502c1170b61e7278c57c9ef72997572adac553827",
        "merkle_root": "ea33cc40ad3917e31809f1d51b66058b69278fc9a43f2e53d3bf18f7ace38e5b",
        "time": 1680025952,
        "bits": "1706023e",
        "nonce": 2469610112,
        "version": 637820928
    },
    {
        "height": 782924,
        "block_hash": "0000000000000000000180f3659ccd4db353b5dad594385a6d172636835a8df6",
        "prev_block": "000000000000000000019e1ed73bbb6fa53fc600c7eb93b3ad7b469a8c4941a6",
        "merkle_root": "f81ad4329c1360f1c09d3b98a813fa60d2d31053f4817ef9517f42247168081d",
        "time": 1680026191,
        "bits": "1706023e",
        "nonce": 478447965,
        "version": 547512320
    },
    {
        "height": 782925,
        "block_hash": "000000000000000000002fc78e86fa4367f8d004a5e944010884f72871227fd1",
        "prev_block": "0000000000000000000180f3659ccd4db353b5dad594385a6d172636835a8df6",
        "merkle_root": "bccca5644d9857c9e1b91285d7466659c7bdcdf08b39bacd3c183853fef8ed4d",
        "time": 1680026424,
        "bits": "1706023e",
        "nonce": 3119286825,
        "version": 538968064
    }
]

for block in block_headers:
    print(f"\n🔎 Verifying block height {block['height']}...")

    # Construct the 80-byte header (fields must be little-endian)
    version = struct.pack("<I", block["version"])
    prev_block = bytes.fromhex(block["prev_block"])[::-1]
    merkle_root = bytes.fromhex(block["merkle_root"])[::-1]
    timestamp = struct.pack("<I", block["time"])
    bits = bytes.fromhex(block["bits"])[::-1]
    nonce = struct.pack("<I", block["nonce"])

    header = version + prev_block + merkle_root + timestamp + bits + nonce

    # Double SHA256
    hash1 = hashlib.sha256(header).digest()
    hash2 = hashlib.sha256(hash1).digest()
    computed_hash = hash2[::-1].hex()

    print(f"✅ Computed: {computed_hash}")
    print(f"🧾 Expected: {block['block_hash']}")
    print("🎯 MATCH ✅" if computed_hash == block["block_hash"] else "❌ MISMATCH")
