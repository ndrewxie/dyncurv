#!/bin/bash
#SBATCH --partition=main
#SBATCH --requeue
#SBATCH --job-name=dyncurv
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=32
#SBATCH --mem=32000
#SBATCH --time=12:00:00
#SBATCH --output=slurm.%N.%j.out
#SBATCH --error=slurm.%N.%j.err
#SBATCH --exclude=halk[0001-0106]
#SBATCH --mail-type=ALL
#SBATCH --mail-user=andrew.x@rutgers.edu

cd /scratch/$USER
module purge

export MODULEPATH=$MODULEPATH:/projects/community/modulefiles
module load gcc/10.2.0-bz186

cd dyncurv
(cd cpp_impl && make clean && make release)

module load anaconda/2020.07-gc563
eval "$(conda shell.bash hook)"
conda env update -f environment.yml
conda activate dyncurv_venv

export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK
export SCALE_DELTA=5

echo "Running $OMP_NUM_THREADS threads"
(cd python_impl && python3 experiment.py --no_analysis --no_dist_mat --num_flocks=10 --num_boids=50 --time_steps 600 --equilib_time_steps 600 --scale $SCALE_DELTA --write_nth 10)
(cd python_impl && python3 experiment.py --no_analysis --no_boids --num_flocks=10 --k 1 --num_target_samples 15000 --num_max_samples 2000)
(cd data && mv dist_mat.dat dist_mat_1.dat)
(cd python_impl && python3 experiment.py --no_analysis --no_boids --num_flocks=10 --k 0 --num_target_samples 7000 --num_max_samples 1000)
(cd data && mv dist_mat.dat dist_mat_0.dat)
#(cd python_impl && python3 experiment.py --no_analysis --no_boids --num_flocks=10 --k 2 --num_target_samples $N_SAMPLES_T --num_max_samples $N_SAMPLES_M)
#(cd data && mv dist_mat.dat dist_mat_2.dat)
