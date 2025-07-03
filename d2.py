import numpy as np
from consts import *
from support import *
import math

def subtract_ints(i1, i2):
    a1, b1 = i1
    a2, b2 = i2
    if a1 > b1:
        return []
    if a2 > b2:
        return [i1]
    if b2 < a1 or a2 > b1:
        return [i1]
    if a2 <= a1 and b1 <= b2:
        return []
    segments = []
    if a1 < a2:
        segments.append((a1, min(b1, a2)))
    if b2 < b1:
        segments.append((max(a1, b2), b1))
    return segments

def compute_left_d2(birth_mat_v, death_mat_v, birth_mat_w, death_mat_w):
    max_d2 = float('inf')
    # TODO
    return max_d2

def compute_d2(birth_mat_v, death_mat_v, birth_mat_w, death_mat_w):
    return max(
        compute_left_d2(birth_mat_v, death_mat_v, birth_mat_w, death_mat_w),
        compute_left_d2(birth_mat_w, death_mat_w, birth_mat_v, death_mat_v)
    )

def compute_static_dI(t):
    dgm_x = compute_Hn(compute_dist(t, x_pts))
    dgm_y = compute_Hn(compute_dist(t, y_pts))
    if dgm_x is None and dgm_y is None:
        return 0.0
    if dgm_x is None:
        return (dgm_y[1] - dgm_y[0]) / 2.0
    if dgm_y is None:
        return (dgm_x[1] - dgm_x[0]) / 2.0
    max_pers = max((dgm_y[1] - dgm_y[0]) / 2.0, (dgm_x[1] - dgm_x[0]) / 2.0)
    dist_match = max(math.fabs(dgm_x[0] - dgm_y[0]), math.fabs(dgm_x[1] - dgm_y[1]))
    return min(max_pers, dist_match)