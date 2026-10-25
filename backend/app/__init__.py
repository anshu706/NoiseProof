"""backend/app/__init__.py"""
import os

# Mitigate OpenBLAS Windows memory allocation error with numpy/scipy
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
