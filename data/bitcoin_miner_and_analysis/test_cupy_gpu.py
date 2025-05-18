import cupy as cp
import time

print("🔍 Running CuPy GPU test...")

# Create a large array on the GPU
N = 10_000_000
x = cp.arange(N, dtype=cp.float32)
start = time.time()

# Perform a GPU computation
y = x ** 2
cp.cuda.Device(0).synchronize()
elapsed = time.time() - start

# Validate the result
correct = cp.allclose(y[:5], cp.array([0, 1, 4, 9, 16], dtype=cp.float32))

print(f"✅ GPU computation complete in {elapsed:.4f} sec")
print(f"🧪 Validation result: {'PASS' if correct else 'FAIL'}")
