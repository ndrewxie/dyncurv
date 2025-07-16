import argparse
import time
from functools import partial

from support import *
from viz import *
from consts import BOID


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("filename", help="Filename in which boids data was stored")
    parser.add_argument("-np", "--no-plot", help="Flag to not plot support", action="store_true")
    args = parser.parse_args()

    filename = args.filename
    pts = []

    with open(filename, "r") as f:
        n = int(f.readline().strip())
        w, h = map(int, f.readline().split())
        cur_pts = []
        for i, line in enumerate(f):
            xi, yi = map(float, f.readline().split())
            cur_pts.append([xi, yi])
            if i % n == n-1:
                pts.append(cur_pts)
                cur_pts = []
    pts = np.array(pts)
    # print(pts[:4])
    constants.T_MIN = 0
    constants.T_MAX = pts.shape[0]
    constants.DELTA = 1
    metric = partial(BOID, width=w, height=h)

    print("Computing support")
    analyze_start = time.perf_counter()
    birth_mat, death_mat = analyze(pts, metric=metric, file_flag=True)
    analyze_end = time.perf_counter()
    print(f"Support computation took {(analyze_end - analyze_start):.4f}")
    
    # print(birth_mat)
    # print(death_mat)
    
    m = death_mat - birth_mat
    if np.count_nonzero(m) > 0:
        print("Good")
    else:
        print("Bad")

    if not args.no_plot:
        print("Plotting")
        # TODO Fix plot function to only plot one thing
        plot_data(birth_mat, death_mat, birth_mat, death_mat)