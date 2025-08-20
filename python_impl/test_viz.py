import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import os
from functools import partial

from boids_sim import Flock
from support import analyze
from consts import constants, BOID
from viz import plot_data

# Ty chatgpt kinda

# Load data from the file
def load_data(filename):
    pts = []
    with open(filename, "r") as f:
        n = int(f.readline().strip())
        f.readline()
        w, h = map(int, f.readline().split())
        cur_pts = []
        for i, line in enumerate(f):
            xi, yi = map(float, line.split())
            cur_pts.append([xi, yi])
            if i % n == n-1:
                pts.append(cur_pts)
                cur_pts = []
    return np.array(pts)

def animate_points(snapshots, name):
    fig, ax = plt.subplots()
    ax.set_aspect('equal')

    all_points = np.vstack(snapshots)
    x_min, x_max = np.min(all_points[:, 0]), np.max(all_points[:, 0])
    y_min, y_max = np.min(all_points[:, 1]), np.max(all_points[:, 1])
    padding = 0.1 * max(x_max - x_min, y_max - y_min)

    ax.set_xlim(x_min - padding, x_max + padding)
    ax.set_ylim(y_min - padding, y_max + padding)

    # Initialize scatter with first frame's data
    scatter = ax.scatter(snapshots[0][:, 0], snapshots[0][:, 1])

    def init():
        scatter.set_offsets(snapshots[0])
        return scatter,

    def update(frame):
        scatter.set_offsets(snapshots[frame+1])
        return scatter,

    ani = animation.FuncAnimation(
        fig, update, frames=len(snapshots)-1, init_func=init,
        interval=20, blit=True, repeat=True
    )
    ani.save(name)

import os
if __name__ == "__main__":
    # outfile = "test.txt"
    # if os.path.exists(outfile):
    #     os.remove(outfile)
    # flock = Flock(4, 0.5, 0.2, 0.15)
    # flock.simulate(500, filename=outfile)
    # good, bad = [], []
    g, b = 0, 0
    q = 50
    # bbb = 20
    # n = 100#bbb*5

    for i in range(0, 10):
        for j in range(0, 5):
            animate_points(load_data(f"./data/behavior{j}/flock{i}.txt"), f"data/movies/b{j}f{i}.mp4")
    #animate_points(load_data(f"./data/behavior{0}/flock{0}.txt"))
    #animate_points(load_data(f"./data/behavior{1}/flock{0}.txt"))
    #animate_points(load_data(f"./data/behavior{2}/flock{0}.txt"))
    #animate_points(load_data(f"./data/behavior{3}/flock{0}.txt"))
    # for i in range(200):
    #     # if i%bbb == 0:
    #     #     print(i//bbb)
    #     snapshots = load_data(f"./data/behavior{1}/flock{0}/sample{i}.txt")
    #     if i % q == 0: animate_points(snapshots)
    #     pts = np.array(snapshots)
        
    #     constants.T_MIN = 0
    #     constants.T_MAX = len(snapshots)
    #     constants.DELTA = 1
    #     metric = partial(BOID, width=500, height=250)

    #     birth_mat, death_mat = analyze(pts, metric=metric, file_flag=True)
    #     m = death_mat - birth_mat
    #     if np.count_nonzero(m) > 0:
    #         g += 1
    #         # print(f"\t{i} - Good")
    #     # print(birth_mat)
    #     # print(death_mat)

    #     # if not args.no_plot:
    #         # print("Plotting")
    #         # plot_data(birth_mat, death_mat, birth_mat, death_mat)
    #     else:
    #         b += 1
    #         # print(f"\t{i} - Bad")
        
    #     # if (i+1)%bbb == 0:
    #     #     good.append(g)
    #     #     bad.append(b)
    #     #     g, b = 0, 0
    # print(f"{g=}, {b=}")
    