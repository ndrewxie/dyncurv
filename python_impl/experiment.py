import random
import argparse
import subprocess
# import numpy as np
import matplotlib.pyplot as plt
from os import path, remove, makedirs, scandir, sep #, listdir
from sklearn.manifold import MDS
from scipy.cluster.hierarchy import dendrogram, linkage
# from functools import partial

# from consts import BOID, constants
# from support import analyze
from boids_sim import Flock


CUR_PATH = path.dirname(path.abspath(__file__))
OUTPUT_PATH = path.join(CUR_PATH, "..", "data")
CPP_PATH = path.join(CUR_PATH, "..", "cpp_impl")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="experiment", description="Script to tie together full experiment")
    parser.add_argument("-b", "--no_boids", help="Don't generate new boids samples", action="store_true")
    parser.add_argument("-d", "--no_dist_mat", help="Don't generate distance matrix with cpp implementation", action="store_true")
    parser.add_argument("-a", "--no_analysis", help="Don't analyze data from distance computations", action="store_true")
    parser.add_argument("-bf", "--behavior_file", type=str, default=path.join(OUTPUT_PATH, "behaviors.txt"), help="File with behaviors to test")
    parser.add_argument("-nf", "--num_flocks", type=int, default=5, help="Number of flocks to generate per behavior")
    parser.add_argument("-ns", "--num_samples", type=int, default=500, help="Number of 2k+2 subsets to sample per flock")
    parser.add_argument("-nb", "--num_boids", type=int, default=50, help="Number of boids to simulate")
    parser.add_argument("-ts", "--time_steps", type=int, default=600, help="Number of time steps to simulate boids")
    parser.add_argument("-k", "--k", type=int, default=1, help="k for 2k+2 to determine number of boids to sample")
    args = parser.parse_args()

    
    # if args.seed != -1:
    #     np.random.seed(args.seed) # Does this affect other files

    if not args.no_boids:
        print("Generating boids...")

        with open(args.behavior_file, "r") as f:
            behaviors = [list(map(float, line.split())) for line in f.readlines()]
        num_behaviors = len(behaviors)

        # constants.T_MIN = 0
        # constants.T_MAX = args.time_steps+1 # pts.shape[0]
        # constants.DELTA = 1
        # metric = partial(BOID, width=500, height=250)

        for i, parameters in enumerate(behaviors):
            if len(parameters) == 3:
                parameters.extend([50, 100, 150])
            sep, ali, coh, sep_rad, ali_rad, coh_rad = parameters

            folder = path.join(OUTPUT_PATH, f"behavior{i}")
            if not path.exists(folder):
                makedirs(folder)

            for j in range(args.num_flocks):
                flock = Flock(args.num_boids, sep, ali, coh, sep_rad, ali_rad, coh_rad)
                sampled_indices = set()

                cur_folder = path.join(folder, f"flock{j}")
                if not path.exists(cur_folder):
                    makedirs(cur_folder)

                for k in range(args.num_samples):
                    while True:
                        indices = random.sample(range(args.num_boids), 2*args.k+2)
                        tuple_indices = tuple(indices)
                        if tuple_indices not in sampled_indices:
                            sampled_indices.add(tuple_indices)
                            break
                    filename = path.join(cur_folder, f"sample{k}.txt")
                    flock.simulate(args.time_steps, indices=indices, filename=filename)

        print("Boids generated!")
            
    cpp_output_file = path.join(OUTPUT_PATH, "dist_mat_tmp.txt")
    dist_mat_file = path.join(OUTPUT_PATH, "dist_mat.txt")
    if not args.no_dist_mat:
        print("Generating distance matrix...")

        if path.exists(cpp_output_file):
            remove(cpp_output_file)
        flock_paths = []
        for folder in scandir(OUTPUT_PATH):
            if folder.is_dir() and "behavior" in folder.name:
                for folder in scandir(folder):
                    if folder.is_dir() and "flock" in folder.name:
                        flock_paths.append(folder.path)
        # print(flock_paths)
        # subprocess.run(["cd", CPP_PATH], shell=True)
        # subprocess.run(["make"], shell=True)
        # import sys
        n = len(flock_paths)
        dist_mat = [[float('inf')]*n for _ in flock_paths]
        for i, path_i in enumerate(flock_paths):
            dist_mat[i][i] = 0
            for j, path_j in enumerate(flock_paths[i+1:], start=i+1):
                subprocess.run([path.join(CPP_PATH, "dyncurv.exe"), cpp_output_file, path_i, path_j], shell=True)#, stdout=sys.stdout)
                
                with open(cpp_output_file, "r") as f:
                    tmp_dist_mat = [list(map(float, line.split())) for line in f.readlines()]
                
                dist_ij = max(min(row)                            for row in tmp_dist_mat)
                dist_ji = max(min(row[j] for row in tmp_dist_mat) for j in range(n))
                dist_mat[i][j] = dist_mat[j][i] = max(dist_ij, dist_ji)
                print(i, j, dist_mat[i][j])
                
        with open(dist_mat_file, "w") as f:
            for row in dist_mat:
                f.write(" ".join(map(str, row)) + "\n")
        print("Distance matrix generated!")
    
    if not args.no_analysis:
        COLORS = ["red", "green"]#, "blue", "purple"]

        print("Analyzing results...")
        with open(dist_mat_file, "r") as f:
            dist_mat = [list(map(float, line.split())) for line in f.readlines()]
        
        cmds = MDS(n_components=2, dissimilarity="precomputed")
        X_cmds = cmds.fit_transform(dist_mat)
        plt.scatter(X_cmds[:, 0], X_cmds[:, 1], c=sum([[col]*args.num_flocks for col in COLORS], start=[]))
        plt.show()

        Z = linkage(dist_mat, 'single')
        # fig = plt.figure(figsize=(25, 10))
        dn = dendrogram(Z)
        plt.show()
        

        
            

