import numpy as np
from consts import *
from support import *
import math

def make_support_tensor(birth_mat, death_mat, K=50):
    """
    Returns an (n x n x K) integer array where entry [i,j,k] is 1
    exactly when birth_mat[i,j] < k < death_mat[i,j], else 0.
    """
    n = birth_mat.shape[0]
    mat = np.zeros((n, n, K), dtype=int)

    # vectorized over i,j for each k
    for k in range(K):
        mat[:, :, k] = ((birth_mat < k) & (k < death_mat)).astype(int)

    return mat

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
                    assert (birth[i][j] <= d0 + k*delta and d0 + k*delta <= death[i][j])
                else:
                    assert not (birth[i][j] <= d0 + k*delta and d0 + k*delta <= death[i][j])

    return arr

import numpy as np

def make_6d_relation(arr1: np.ndarray) -> np.ndarray:
    """
    Given arr1 of shape (n, n, m), returns arr2 of shape
    (n, n, m, n, n, m) with
      arr2[i1,j1,k1,i2,j2,k2] = 1
    exactly when
      i2 <= i1, j2 >= j1, k1 <= k2,
      and both arr1[i1,j1,k1] and arr1[i2,j2,k2] are 1.
    """
    # infer dimensions
    n1, n2, m = arr1.shape
    assert n1 == n2, "arr1 must be square in first two dims"
    n = n1


    # boolean mask of where arr1 is 1
    A = (arr1 == 1)

    # reshape to broadcast the two copies of A across a 6D grid
    A1 = A[:, :, :, None, None, None]   # shape (n, n, m, 1, 1, 1)
    A2 = A[None, None, None, :, :, :]   # shape (1, 1, 1, n, n, m)

    # build index‐comparison masks
    i1 = np.arange(n)[:, None, None, None, None, None]
    j1 = np.arange(n)[None, :, None, None, None, None]
    k1 = np.arange(m)[None, None, :, None, None, None]

    i2 = np.arange(n)[None, None, None, :, None, None]
    j2 = np.arange(n)[None, None, None, None, :, None]
    k2 = np.arange(m)[None, None, None, None, None, :]

    cond_idx = (i2 <= i1) & (j2 >= j1) & (k1 <= k2)

    # combine all conditions and cast to int
    arr2 = (A1 & A2 & cond_idx).astype(int)
    return arr2

def gpt_test1(runs, m):

    for _ in range(0, runs):

        arr = np.random.randint(0, 2, size=(m, m, m))
        test = make_6d_relation(arr)
        for i1 in range(0, 3):
            for j1 in range(i1, 3):
                for k1 in range(0, 3):
                    for i2 in range(0, 3):
                        for j2 in range(i1, 3):
                            for k2 in range(0, 3):
                                if(test[i1][j1][k1][i2][j2][k2] == 1):
                                    assert (arr[i1][j1][k1] == 1 and arr[i2][j2][k2] == 1 and i2 <= i1 and j1 <= j2 and k1 <= k2)
                                else:
                                    assert not (arr[i1][j1][k1] == 1 and arr[i2][j2][k2] == 1 and i2 <= i1 and j1 <= j2 and k1 <= k2)


def compute_dE(birth_mat_v, death_mat_v, birth_mat_w, death_mat_w):

    eps = 0
    n = len(birth_mat_v)
    print("following value is n")
    print(n)
    d = constants.DELTA
    scalemax = 3

    support_v = make_3d_lifespan_mask(birth_mat_v, death_mat_v, 0, scalemax, d)
    support_w = make_3d_lifespan_mask(birth_mat_w, death_mat_w, 0, scalemax, d)

    n1, n2, n3 = support_v.shape

    rank_v = make_6d_relation(support_v)
    rank_w = make_6d_relation(support_w)

    for i1 in range(0, n):
        for j1 in range(i1, n):
            for k1 in range(0, n3):
                for i2 in range(0, n):
                    for j2 in range(i2, n):
                        for k2 in range(0, n3):
                            #if(rank_v[i1][j1][k1][i2][j2][k2] == 1 or rank_w[i1][j1][k1][i2][j2][k2] == 1):
                                #print("test 5")
                            if(rank_v[i1][j1][k1][i2][j2][k2] == 1 and rank_w[i1][j1][k1][i2][j2][k2] == 0):
                                shift = 1
                                #print("test 1")
                                while(i1+shift<n and j1-shift>=0 and k1-shift>=0 and i2-shift>=0 and j2+shift<n and k2+shift<n3 and rank_v[i1+shift][j1-shift][k1-shift][i2-shift][j2+shift][k2+shift] == 1):
                                    shift += 1
                                    #print("test 3")
                                eps = max(eps, shift-1)
                            elif(rank_v[i1][j1][k1][i2][j2][k2] == 0 and rank_w[i1][j1][k1][i2][j2][k2] == 1):
                                shift = 1
                                #print("test 2")
                                while(i1+shift<n and j1-shift>=0 and k1-shift>=0 and i2-shift>=0 and j2+shift<n and k2+shift<n3 and rank_w[i1+shift][j1-shift][k1-shift][i2-shift][j2+shift][k2+shift] == 1):
                                    shift += 1
                                    #print("test 4")
                                eps = max(eps, shift-1)
                            
    return eps * constants.DELTA

