import time
import argparse
import sys

from consts import *
from viz import plot_data
from support import analyze
from d2 import *

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="dyncurv", description="Script used to generate support of DMS given by Python functions and NOT boids text file")
    parser.add_argument("-t0", "--t_min", type=float, help="Smallest time value to consider for intervals")
    parser.add_argument("-t1", "--t_max", type=float, help="Largest time value to consider for intervals")
    parser.add_argument("-d", "--delta", type=float, help="Step size to increment by from t_min to t_max")
    parser.add_argument("-np", "--no-plot", help="Flag to not plot support", action="store_true")
    args = parser.parse_args()

    constants.T_MIN = args.t_min if args.t_min else constants.T_MIN
    constants.T_MAX = args.t_max if args.t_max else constants.T_MAX
    constants.DELTA = args.delta if args.delta else constants.DELTA
    if constants.T_MAX < constants.T_MIN:
        print("Error: t_min must be less than or equal to t_max")
        sys.exit(1)
    
    print("Computing support")
    analyze_start = time.perf_counter()
    # print("X") # I think these prints are affecting the counter a bit
    birth_mat_x, death_mat_x = analyze(x_pts)
    # print("Y")
    birth_mat_y, death_mat_y = analyze(y_pts)
    analyze_end = time.perf_counter()
    print(f"Support computation took {(analyze_end - analyze_start):.4f}")

    d2_start = time.perf_counter()
    d2 = compute_d2(birth_mat_x, death_mat_x, birth_mat_y, death_mat_y)
    di = compute_static_dI(0.0)
    print(f"d2(V, W) = {d2:.4f}")
    print(f"dI(V, W) = {di:.4f}")
    d2_end = time.perf_counter()

    if not args.no_plot:
        print("Plotting")
        plot_data(birth_mat_x, death_mat_x, birth_mat_y, death_mat_y)
    input("Press any key to exit")
