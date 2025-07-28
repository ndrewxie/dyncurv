import numpy as np
from consts import *
from support import *
import math

def make_3d_lifespan_mask(birth: np.ndarray,
                          death: np.ndarray,
                          d0: float,
                          d1: float,
                          delta: float) -> np.ndarray:
    """
    Returns an (n, n, K) array `arr` where
      arr[i,j,k] == 1  iff  t_k = d0 + k*delta is between birth[i,j] and death[i,j],
      arr[i,j,k] == 0  otherwise.
    
    Assumes birth.shape == death.shape == (n,n).
    """
    assert birth.shape == death.shape, "birth and death must be same shape"
    n = birth.shape[0]

    # build the 1D time‐axis
    times = np.arange(d0, d1 + 1e-12, delta)            # +tiny to include d1 if it falls exactly
    K = times.size

    # broadcast comparison: shape (n, n, K)
    start_mask = times[np.newaxis, np.newaxis, :] >= birth[:, :, np.newaxis]
    end_mask   = times[np.newaxis, np.newaxis, :] <= death[:, :, np.newaxis]

    arr = (start_mask & end_mask).astype(int)

    for i in range(0, n):
        for j in range(0, n):
            for k in range(0, K):
                if(arr[i][j][k] == 1):
                    assert (birth[i][j] <= d0 + k*delta <= death[i][j])
                else:
                    assert not (birth[i][j] <= d0 + k*delta <= death[i][j])

    return arr

def compute_dE(birth_mat_v, death_mat_v, birth_mat_w, death_mat_w):

    d = constants.DELTA
    scalemax = max(death_mat_v.max(), death_mat_w.max())+2*d

    support_v = make_3d_lifespan_mask(birth_mat_v, death_mat_v, 0, scalemax, d)
    support_w = make_3d_lifespan_mask(birth_mat_w, death_mat_w, 0, scalemax, d)

    n1, n2, n3 = support_v.shape
    print("n=" + str(n1-1))

    down_v = np.zeros((n1, n2, n3))
    down_w = np.zeros((n1, n2, n3))

    for i in range(n1-1, -1, -1):
        for j in range(i, n2):
            for k in range(0, n3):
                if(k > 0):
                    if(support_v[i][j][k] == 1 and support_w[i][j][k] == 0):
                        down_v[i][j][k] = down_v[i+1 if i+1 < j else i][j-1 if i != j else j][k-1]+1
                    if(support_v[i][j][k] == 0 and support_w[i][j][k] == 1):
                        down_w[i][j][k] = down_w[i+1 if i+1 < j else i][j-1 if i != j else j][k-1]+1

    up_v = np.zeros((n1, n2, n3))
    up_w = np.zeros((n1, n2, n3))

    for i in range(0, n1):
        for j in range(n2-1, i-1, -1):
            for k in range(n3-1, -1, -1):
                if(k < n3-1):
                    if(support_v[i][j][k] == 1 and support_w[i][j][k] == 0):
                        up_v[i][j][k] = up_v[i-1 if i>0 else 0][j+1 if j<n2-1 else j][k+1]+1
                    if(support_v[i][j][k] == 0 and support_w[i][j][k] == 1):
                        up_w[i][j][k] = up_w[i-1 if i>0 else 0][j+1 if j<n2-1 else j][k+1]+1

    suff_v = np.zeros((n1, n2, n3))
    suff_w = np.zeros((n1, n2, n3))

    for i in range(0, n1):
        for j in range(n2-1, i-1, -1):
            for k in range(n3-1, -1, -1):
                imax_v = suff_v[i-1][j][k] if i > 0 else up_v[i][j][k]
                jmax_v = suff_v[i][j+1][k] if j < n2-1 else up_v[i][j][k]
                kmax_v = suff_v[i][j][k+1] if k < n3-1 else up_v[i][j][k]
                imax_w = suff_w[i-1][j][k] if i > 0 else up_w[i][j][k]
                jmax_w = suff_w[i][j+1][k] if j < n2-1 else up_w[i][j][k]
                kmax_w = suff_w[i][j][k+1] if k < n3-1 else up_w[i][j][k]

                suff_v[i][j][k] = max(imax_v, jmax_v, kmax_v, up_v[i][j][k])
                suff_w[i][j][k] = max(imax_w, jmax_w, kmax_w, up_w[i][j][k])
                    
    shift = 0
    for i in range(0, n1):
        for j in range(i, n2):
            for k in range(0, n3):
                shift = max(shift, min(down_v[i][j][k], suff_v[i][j][k]), min(down_w[i][j][k], suff_w[i][j][k]))
    
    return shift * d

