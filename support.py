from consts import *
import numpy as np

def compute_Hn(dist_mat):
    n = len(dist_mat)
    t_b = 0.0
    t_d = float('inf')
    
    for x0 in range(n):
        dists = []
        for i in range(n):
            if i != x0:
                dists.append(dist_mat[x0, i])
        
        dists.sort(reverse=True)
        
        t_b = max(t_b, dists[1])
        t_d = min(t_d, dists[0])
    
    if t_d - t_b > 1e-9 and t_d > 1e-9:
        return (t_b, t_d)
    else:
        return None

def compute_dist(t, pts):
    points = [pts[i](t) for i in range(len(pts))]
    pts_arr = np.array(points)
    dist_mat = np.linalg.norm(pts_arr[:, None] - pts_arr[None, :], axis=2)
    return dist_mat

def analyze(pts):
    t_pts = np.arange(T_MIN, T_MAX + DELTA, DELTA)
    n_steps = len(t_pts)
    
    birth_mat = np.zeros((n_steps, n_steps))
    death_mat = np.zeros((n_steps, n_steps))
    
    for i in range(n_steps):
        for j in range(i, n_steps):
            a = t_pts[i]
            b = t_pts[j]
            
            min_dist = None
            int_times = np.arange(a, b + DELTA, DELTA)
            
            for t in int_times:
                if t > T_MAX:
                    break
                new_dist = compute_dist(t, pts)
                if min_dist is None:
                    min_dist = new_dist
                else:
                    np.minimum(min_dist, new_dist, out=min_dist)
            
            h1_result = compute_Hn(min_dist)
            
            if h1_result is not None:
                birth, death = h1_result
                birth_mat[i, j] = birth
                death_mat[i, j] = death
            else:
                birth_mat[i, j] = 0
                death_mat[i, j] = 0
    
    return birth_mat, death_mat