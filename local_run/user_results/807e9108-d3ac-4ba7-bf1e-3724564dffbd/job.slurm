#!/bin/bash

#SBATCH --job-name=microbializer
#SBATCH --account=pupkoweb-users
#SBATCH --partition=pupkoweb
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=8192
#SBATCH --output=C:\repos\microbializer_v2\local_run\user_results\807e9108-d3ac-4ba7-bf1e-3724564dffbd\main_%j.out
#SBATCH --error=C:\repos\microbializer_v2\local_run\user_results\807e9108-d3ac-4ba7-bf1e-3724564dffbd\main_%j.err


sleep 10

echo "Job ID: $SLURM_JOB_ID"
echo "Running on nodes: $SLURM_JOB_NODELIST"
echo "Allocated CPUs: $SLURM_JOB_CPUS_PER_NODE"

export HOME=/lsweb/pupko/microbializer
source /lsweb/pupko/microbializer/miniconda3/etc/profile.d/conda.sh
conda activate /lsweb/pupko/microbializer/miniconda3/envs/microbializer
export PATH=$CONDA_PREFIX/bin:$PATH

echo "PATH: $PATH"

python "/lsweb/pupko/microbializer/pipeline/main.py" --args_json_path C:\repos\microbializer_v2\local_run\user_results\807e9108-d3ac-4ba7-bf1e-3724564dffbd\input_parameters.json --account_name pupkoweb-users --queue_name pupkoweb
