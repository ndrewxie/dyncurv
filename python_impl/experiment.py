import random
import argparse
import subprocess
import numpy as np
import matplotlib.pyplot as plt
from os import path, remove, makedirs, scandir, sep, listdir
from sklearn.manifold import MDS
from scipy.cluster.hierarchy import dendrogram, linkage
from functools import partial

from consts import BOID, constants
from support import analyze
from boids_sim import Flock


CUR_PATH = path.dirname(path.abspath(__file__))
OUTPUT_PATH = path.join(CUR_PATH, "..", "data")
CPP_PATH = path.join(CUR_PATH, "..", "cpp_impl")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="experiment", description="Script to tie together full experiment")
    parser.add_argument("-b", "--no_boids", help="Don't generate new boids samples", action="store_true")
    parser.add_argument("-d", "--no_dist_mat", help="Don't generate distance matrix with cpp implementation", action="store_true")
    parser.add_argument("-bf", "--behavior_file", type=str, default=path.join(OUTPUT_PATH, "behaviors.txt"), help="File with behaviors to test")
    parser.add_argument("-ns", "--num_samples", type=int, default=20, help="Number of samples to generate per behavior")
    parser.add_argument("-nb", "--num_boids", type=int, default=16, help="Number of boids to simulate")
    parser.add_argument("-ts", "--time_steps", type=int, default=1000, help="Number of time steps to simulate boids")
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

            flock = Flock(args.num_boids, sep, ali, coh, sep_rad, ali_rad, coh_rad)
            for j in range(args.num_samples):
                indices = random.sample(range(args.num_boids), 2*args.k+2)
                filename = path.join(OUTPUT_PATH, f"behavior{i}", f"boids{j}.txt")
                flock.simulate(args.time_steps, indices=indices, filename=filename)

        print("Boids generated!")
            
    cpp_output_file = path.join(OUTPUT_PATH, "dist_mat.txt")
    if not args.no_dist_mat:
        print("Generating distance matrix...")

        if path.exists(cpp_output_file):
            remove(cpp_output_file)
        filenames = []
        for folder in scandir(OUTPUT_PATH):
            if folder.is_dir() and "behavior" in folder.name:
                for file in scandir(folder):
                    if file.is_file():
                        filenames.append(file.path)

        # subprocess.run(["cd", CPP_PATH], shell=True)
        # subprocess.run(["make"], shell=True)
        # import sys
        subprocess.run([path.join(CPP_PATH, "dyncurv.exe"), cpp_output_file] + filenames, shell=True)#, stdout=sys.stdout)
        print("Distance matrix generated!")
    
    if True: # I'm just putting this here for right now during the meeting
        print("Analyzing results...")
        with open(cpp_output_file, "r") as f:
            dist_mat = [list(map(float, line.split())) for line in f.readlines()]
        
        cmds = MDS(n_components=2, dissimilarity="precomputed")
        X_cmds = cmds.fit_transform(dist_mat)
        plt.scatter(X_cmds[:, 0], X_cmds[:, 1], c=["red"]*4 + ["green"]*4 + ["blue"]*4 + ["purple"]*4 + ["orange"]*4)
        plt.show()

        Z = linkage(dist_mat, 'single')
        # fig = plt.figure(figsize=(25, 10))
        dn = dendrogram(Z)
        plt.show()
        

        
            

