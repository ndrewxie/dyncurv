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
cd python_impl
(cd python_impl && python3 experiment.py --no_analysis --no_dist_mat --num_flocks=10 --num_boids=50 --time_steps 600 --equilib_time_steps 600 --scale 2.5 --write_nth 10)
(cd data && python3 run_betti.py)