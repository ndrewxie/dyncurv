from mat_ops import *

A0_1, A0_2 = read_mats("dist_mat_0.dat")
A1_1, A1_2 = read_mats("dist_mat_1.dat")
write_matrix("dE_0", A0_1)
write_matrix("d2_0", A0_2)
write_matrix("dE_1", A1_1)
write_matrix("d2_1", A1_2)
choice = input("Matrix dE or d2: ").strip()
rescale = input("Rescale: ").strip().lower()
should_rescale = (rescale == "yes")
if choice == "dE":
    M1 = A1_1
    M0 = A0_1
else:
    M1 = A1_2
    M0 = A0_2
A = M1.copy()
B = M0.copy()
if should_rescale:
    A, B = rescale_mats(A, B)
result = np.maximum(A, B)
write_matrix("dist_mat.dat", result)