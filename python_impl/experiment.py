import sys
import argparse
import subprocess
from os import path, remove, makedirs, scandir, sep #, listdir
from scipy.spatial.distance import squareform

from boids_sim import Flock


CUR_PATH = path.dirname(path.abspath(__file__))
OUTPUT_PATH = path.join(CUR_PATH, "..", "data")
CPP_PATH = path.join(CUR_PATH, "..", "cpp_impl")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="experiment", description="Script to tie together full experiment")
    parser.add_argument("-b", "--no_boids", help="Don't generate new boids samples", action="store_true")
    parser.add_argument("-d", "--no_dist_mat", help="Don't generate distance matrix with cpp implementation", action="store_true")
    parser.add_argument("-a", "--no_analysis", help="Don't analyze data from distance computations", action="store_true")
    parser.add_argument("-c", "--recompile", help="Recompile the cpp code", action="store_false")
    parser.add_argument("-bf", "--behavior_file", type=str, default=path.join(OUTPUT_PATH, "behaviors.dat"), help="File with behaviors to test")
    parser.add_argument("-nf", "--num_flocks", type=int, default=5, help="Number of flocks to generate per behavior")
    parser.add_argument("-nts", "--num_target_samples", type=int, default=250, help="Target number of 2k+2 subsets to sample per flock")
    parser.add_argument("-nms", "--num_max_samples", type=int, default=2000, help="Maximum number of 2k+2 subsets to sample per flock")
    parser.add_argument("-nb", "--num_boids", type=int, default=50, help="Number of boids to simulate")
    parser.add_argument("-ts", "--time_steps", type=int, default=600, help="Number of time steps to simulate boids")
    parser.add_argument("-ets", "--equilib_time_steps", type=int, default=100, help="Number of time steps to equilibriate system")
    parser.add_argument("-k", "--k", type=int, default=1, help="k for 2k+2 to determine number of boids to sample")
    parser.add_argument("-s", "--scale", type=float, default=1.0, help="Scale to increment delta by")
    parser.add_argument("-rs", "--rand_seed", type=int, default=None, help="Seed for RNG")
    parser.add_argument("-wnth", "--write_nth", type=int, default=1, help="Write every nth timestep")
    args = parser.parse_args()

    # if args.recompile:
    #     subprocess.run("g++ -std=c++17 -Wall -g -O3 -fassociative-math".split() + [path.join(CPP_PATH, "main.cpp"), "-o", path.join(CPP_PATH, "dyncurve.exe")], shell=True)

    args.num_behaviors = 4
    with open(args.behavior_file, "r") as f:
        behaviors = [list(map(float, line.split())) for line in f.readlines()]
    args.num_behaviors = len(behaviors)
    if not args.no_boids:
        print("Generating boids...")

        for i, parameters in enumerate(behaviors):
            if len(parameters) == 3:
                parameters.extend([50, 100, 150])
            sep, ali, coh, sep_rad, ali_rad, coh_rad = parameters

            folder = path.join(OUTPUT_PATH, f"behavior{i}")
            if not path.exists(folder):
                makedirs(folder)

            for j in range(args.num_flocks):
                flock = Flock(args.num_boids, sep, ali, coh, sep_rad, ali_rad, coh_rad, seed=args.rand_seed)

                full_flock_filename = path.join(folder, f"flock{j}.txt")
                if path.exists(full_flock_filename):
                    remove(full_flock_filename)

                flock.simulate(args.time_steps,
                               num_equilib_steps=args.equilib_time_steps,
                               filename=full_flock_filename,
                               scale=args.scale,
                               write_every_n=args.write_nth)

        print("Boids generated!")
    

    cpp_output_file = path.join(OUTPUT_PATH, "dist_mat.dat")
    if not args.no_dist_mat:
        print("Generating distance matrix...")

        if path.exists(cpp_output_file):
            remove(cpp_output_file)

        flock_paths = []
        for folder in scandir(OUTPUT_PATH):
            if folder.is_dir() and "behavior" in folder.name:
                for file in scandir(folder):
                    if file.is_file() and "flock" in file.name:
                        flock_paths.append(file.path)
        flock_paths.sort()

        dyncurv_exe = "dyncurv"
        if sys.platform.startswith('win'):
            dyncurv_exe = "dyncurv.exe"
        
        subprocess.run([
            path.join(CPP_PATH, dyncurv_exe), 
            str(args.k), str(args.num_target_samples), str(args.num_max_samples), cpp_output_file
        ] + flock_paths)
        
        print("Distance matrix generated!")
    

    if not args.no_analysis:
        import matplotlib.pyplot as plt
        from sklearn.manifold import MDS
        from scipy.cluster.hierarchy import dendrogram, linkage

        behaviors = args.num_behaviors
        COLORS = ["red", "green", "blue", "purple", "orange", "black"][:behaviors]

        print("Analyzing results...")
        with open(cpp_output_file, "r") as f:
            dist_mat = [list(map(float, line.split())) for line in f.readlines()]
        flocks = len(dist_mat) // behaviors

        cmds = MDS(n_components=2, dissimilarity="precomputed") # Change n_components=3 for 2d
        X_cmds = cmds.fit_transform(dist_mat)
        # fig = plt.figure()
        # ax = fig.add_subplot(projection="3d")
        # ax.scatter(X_cmds[:, 0], X_cmds[:, 1], X_cmds[:, 2], c=sum([[col]*flocks for col in COLORS], start=[]))
        offset = 0
        for behavior, col in enumerate(COLORS):
            pts = X_cmds[offset:offset+flocks]
            plt.scatter(pts[:,0], pts[:,1], c=col, label=f"Behavior {behavior+1}")
            offset += flocks
        plt.legend()
        plt.show()

        Z = linkage(squareform(dist_mat), 'single')
        dn = dendrogram(Z, leaf_label_func = lambda i : 1+i//flocks)
        
        plt.show()
