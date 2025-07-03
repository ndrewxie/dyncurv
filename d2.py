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
def filter_intervals(segs, range_int=(float('-inf'), float('inf'))):
    new_segs = []
    for s in segs:
        low = max(range_int[0], s[0])
        high = min(range_int[1], s[1])
        if low < high:
            new_segs.append((low, high))
    return new_segs

def compute_max_rad(i, j, seg, birth_mat_v, death_mat_v):
    m = len(birth_mat_v)
    n = len(birth_mat_v[0])
    low = 0
    high = min((j - i)//2, n - j - 1, i)
    max_rad = 0
    while low <= high:
        mid = low + (high-low)//2
        midf = float(mid)
        mid_seg_low = (
            birth_mat_v[i+mid][j-mid] + constants.DELTA * midf, 
            death_mat_v[i+mid][j-mid] + constants.DELTA * midf
        )
        mid_seg_high = (
            birth_mat_v[i-mid][j+mid] - constants.DELTA * midf, 
            death_mat_v[i-mid][j+mid] - constants.DELTA * midf
        )
        new_seg = filter_intervals(filter_intervals(seg, mid_seg_low), mid_seg_high)
        if len(new_seg) > 0:
            max_rad = mid
            low = mid + 1
        else:
            high = mid - 1
    return max_rad * constants.DELTA

def compute_left_d2(birth_mat_v, death_mat_v, birth_mat_w, death_mat_w):
    m = len(birth_mat_v)
    n = len(birth_mat_v[0])
    max_d2 = 0
    for i in range(0, m):
        for j in range(i, n):
            int_v = (birth_mat_v[i][j], death_mat_v[i][j])
            int_w = (birth_mat_w[i][j], death_mat_w[i][j])
            delta = filter_intervals(subtract_ints(int_v, int_w))
            if len(delta) == 0:
                continue
            max_rad = compute_max_rad(i, j, delta, birth_mat_v, death_mat_v)
            max_d2 = max(max_d2, max_rad)
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