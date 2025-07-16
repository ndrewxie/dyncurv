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
    with open(filename, 'r') as f:
        lines = f.readlines()

    n = int(lines[0].strip())
    snapshots = []
    total_lines = len(lines)
    i = 1  # Start after the first line

    while i < total_lines:
        frame = []
        for j in range(n):
            x, y = map(float, lines[i + j].strip().split())
            frame.append((x, y))
        snapshots.append(np.array(frame))
        i += 50  # Move to the next snapshot

    return snapshots


def animate_points(snapshots):
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
        interval=100, blit=True, repeat=True
    )

    plt.show()

import os
if __name__ == "__main__":
    outfile = "test.txt"
    if os.path.exists(outfile):
        os.remove(outfile)
    flock = Flock(4, 0.5, 0.2, 0.15)
    flock.simulate(500, filename=outfile)

    snapshots = load_data(outfile)
    animate_points(snapshots)
    
    pts = np.array(snapshots)
    constants.T_MIN = 0
    constants.T_MAX = flock.num_pts
    constants.DELTA = 1
    metric = partial(BOID, width=flock.width, height=flock.height)

    birth_mat, death_mat = analyze(pts, True)
    m = death_mat - birth_mat
    if np.count_nonzero(m) > 0:

    # print(birth_mat)
    # print(death_mat)

    # if not args.no_plot:
        print("Plotting")
        # TODO Fix plot function to only plot one thing
        plot_data(birth_mat, death_mat, birth_mat, death_mat)
    else:
        print("Crap")
    