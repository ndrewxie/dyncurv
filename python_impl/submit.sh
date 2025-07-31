#!/bin/bash
#SBATCH --partition=main
#SBATCH --requeue
#SBATCH --job-name=dyncurv
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=32
#SBATCH --mem=6500
#SBATCH --time=03:00:00
#SBATCH --output=slurm.%N.%j.out
#SBATCH --error=slurm.%N.%j.err
#SBATCH --mail-type=ALL
#SBATCH --mail-user=andrew.x@rutgers.edu

cd /scratch/$USER
module purge

export MODULEPATH=$MODULEPATH:/projects/community/modulefiles
module load gcc/10.2.0-bz186
module load python/3.8.2

cd dyncurv
(cd cpp_impl && make clean && make release)

module load anaconda/2020.07-gc563
eval "$(conda shell.bash hook)"
conda env update -f -y environment.yml
conda activate dyncurv_venv

export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK
echo "Running $OMP_NUM_THREADS threads"
(cd python_impl && python3 experiment.py --no-analysis --num-flocks 5 --num-samples 1500 --num-boids 50 --time-steps 750 --k 1 --scale 0.1)