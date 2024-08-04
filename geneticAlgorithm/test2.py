import numpy as np

array1 = [0, 1, 100, 2, 3]
array2 = [-1, -2, -234, -3, -4]

sorted_index = np.argsort(array1)
print([array2[i] for i in sorted_index])