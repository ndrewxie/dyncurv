from mat_ops import *
import numpy as np

N_TRIALS = 10_000
N_SAMPLES = 10
N_CLASSES = 5
N_PTS = N_SAMPLES * N_CLASSES

def metric_1_nn(dist_mat):
    c_metric = 0.0
    for _ in range(0, N_TRIALS):
        n_correct = 0
        centers = []
        for c in range(0, N_CLASSES):
            centers.append(c * N_SAMPLES + np.random.randint(0, N_SAMPLES))
        for i in range(0, N_PTS):
            true_label = i // N_SAMPLES
            center_dists = [dist_mat[i][j] for j in centers]
            cluster_label = np.argmin(center_dists)
            if true_label == cluster_label:
                n_correct += 1
        c_metric = max(c_metric, float(n_correct) / float(N_PTS))
    return c_metric

dE_0_r, d2_0_r = read_mats("dist_mat_0.dat")
dE_1_r, d2_1_r = read_mats("dist_mat_1.dat")
dE_0, dE_1 = rescale_mats(dE_0_r, dE_1_r)
d2_0, d2_1 = rescale_mats(d2_0_r, d2_1_r)

dE = np.maximum(dE_0, dE_1)
d2 = np.maximum(d2_0, d2_1)

print(f"dE accuracy: {metric_1_nn(dE)}")
print(f"d2 accuracy: {metric_1_nn(d2)}")
