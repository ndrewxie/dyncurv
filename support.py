import numpy as np

from consts import *


def compute_Hn(dist_mat):
    # This is hilarious, I love numpy
    largest_two_dists = np.partition(dist_mat, -2)[:, -2:]
    t_b = np.max(largest_two_dists[:, 0])
    t_d = np.min(largest_two_dists[:, 1])

    if t_d - t_b > 1e-9 and t_d > 1e-9:
        return (t_b, t_d)
    else:
        return None

def compute_dist(t, pts):
    points = [pt(t) for pt in pts]
    pts_arr = np.array(points)
    dist_mat = np.linalg.norm(pts_arr[:, None] - pts_arr[None, :], axis=2)
    return dist_mat

def analyze(pts, sus_dumb_flag_aaaa=False):
    T_MIN, T_MAX, DELTA = constants

    t_pts = np.arange(T_MIN, T_MAX + DELTA, DELTA).tolist()
    n_steps = len(t_pts)
    # print(T_MIN, T_MAX, DELTA)
    birth_mat = np.zeros((n_steps, n_steps))
    death_mat = np.zeros((n_steps, n_steps))

    if not sus_dumb_flag_aaaa:
        dist_mats = [compute_dist(t, pts) for t in t_pts]  # O(n_steps**3), nothing can be done about that tbh
    else:
        dist_mats = [np.linalg.norm(pts_t[:, None] - pts_t[None, :], axis=2) for pts_t in pts] # Same here
    
    for i, min_dist in enumerate(dist_mats):
        for j, new_dist_mat in enumerate(dist_mats[i:], start=i):
            np.minimum(min_dist, new_dist_mat, out=min_dist)  # Idt seg tree helps here unfortunately

            h1_result = compute_Hn(min_dist)
            
            if h1_result is not None:
                birth, death = h1_result
                birth_mat[i, j] = birth
                death_mat[i, j] = death
            else:
                birth_mat[i, j] = 0
                death_mat[i, j] = 0
    
    return birth_mat, death_mat