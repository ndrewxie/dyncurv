#!/bin/bash
#SBATCH --partition=main
#SBATCH --requeue
#SBATCH --job-name=dyncurv_betti
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=32
#SBATCH --mem=96000
#SBATCH --time=38:00:00
#SBATCH --output=slurm.%N.%j.out
#SBATCH --error=slurm.%N.%j.err
#SBATCH --exclude=halk[0001-0106]
#SBATCH --mail-type=ALL
#SBATCH --mail-user=andrew.x@rutgers.edu

cd /scratch/$USER
module purge

export MODULEPATH=$MODULEPATH:/projects/community/modulefiles

cd dyncurv

module load anaconda/2020.07-gc563
eval "$(conda shell.bash hook)"
#conda env update -f environment.yml
conda activate dyncurv_venv

export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK
export SCALE_DELTA=5

echo "Running $OMP_NUM_THREADS threads"
(cd python_impl && python3 experiment.py --no_analysis --no_dist_mat --num_flocks=10 --num_boids=50 --time_steps 600 --equilib_time_steps 600 --scale $SCALE_DELTA --write_nth 10)
echo "Done writing boids"
(cd data && PYTHONUNBUFFERED=1 python3 run_betti.py)
