import os

# Prevent OpenBLAS thread allocation issues on Windows
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
