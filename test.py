from numba import njit
import numpy as np

@njit
def add_arrays(a, b):
    return a + b

a = np.array([1, 2, 3])
b = np.array([4, 5, 6])
print(add_arrays(a, b))
