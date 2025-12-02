# Dyncurv
An implementation of curvature sets over dynamic metric spaces

# Usage
First, build dyncurv executable (which supports computation of supports and various distances):
```bash
cd cpp_impl && make -j8
```

Then load the required dependencies (optional if installed):
```bash
conda env update -f environment.yml
conda activate dyncurv_venv
``` 

Then cd into working directory:
```bash
cd python_impl
```
and generate the boids:
```bash
python3 experiment.py --no-analysis --no_dist_mat --num_flocks=10 --num_boids=50 --time_steps 600 --scale 2.5 --write_nth 5)
```
and then run the `k=0` and `k=1` stages:
```bash
python3 experiment.py --no_analysis --no_boids --num_flocks=10 --k 1 --num_target_samples 15000 --num_max_samples 2000
mv ../data/dist_mat.dat ../data/dist_mat_1.dat
python3 experiment.py --no_analysis --no_boids --num_flocks=10 --k 0 --num_target_samples 7000 --num_max_samples 1000
mv ../data/dist_mat.dat ../data/dist_mat_0.dat
```
Then leave working directory:
```bash
cd ..
```

Finally, visualize the output:
```bash
cd data
python3 build_mats.py # Type dE when prompted: d2 is for testing purposes. Type yes for rescaling when prompted
cd ..
cd python_impl 
python3 experiment.py --no_boids --no_dist_mat
```
