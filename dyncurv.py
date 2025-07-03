import numpy as np
import time

from consts import *
from viz import *
from support import *

print("Computing support")
analyze_start = time.time()
print("X")
birth_mat_x, death_mat_x = analyze(x_pts)
print("Y")
birth_mat_y, death_mat_y = analyze(y_pts)
analyze_end = time.time()
print(f"Support computation took {(analyze_end - analyze_start):.4f}")

print("Plotting")
plot_data(birth_mat_x, death_mat_x, birth_mat_y, death_mat_y)
input("Press any key to exit")
