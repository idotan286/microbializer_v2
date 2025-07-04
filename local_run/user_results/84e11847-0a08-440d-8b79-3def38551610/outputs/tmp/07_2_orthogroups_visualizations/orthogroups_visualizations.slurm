#!/bin/bash 
#SBATCH --job-name=orthogroups_visualizations
#SBATCH --account=pupkoweb-users
#SBATCH --partition=pupkoweb
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=32G
#SBATCH --output=/lsweb/pupko/microbializer/user_results/1e1bec97-f954-428c-881c-5e92edfa6421/outputs/tmp/07_2_orthogroups_visualizations/orthogroups_visualizations_%j.out
#SBATCH --error=/lsweb/pupko/microbializer/user_results/1e1bec97-f954-428c-881c-5e92edfa6421/outputs/tmp/07_2_orthogroups_visualizations/orthogroups_visualizations_%j.err
echo Job ID: $SLURM_JOB_ID
echo Running on nodes: $SLURM_JOB_NODELIST
echo Allocated CPUs: $SLURM_JOB_CPUS_PER_NODE
echo Memory per node: $SLURM_MEM_PER_NODE MB
echo Job name: $SLURM_JOB_NAME
/lsweb/pupko/microbializer/user_results/1e1bec97-f954-428c-881c-5e92edfa6421/outputs/tmp/07_2_orthogroups_visualizations/orthogroups_visualizations.sh
scontrol show job $SLURM_JOB_ID | grep -m 1 "RunTime=" >> /lsweb/pupko/microbializer/user_results/1e1bec97-f954-428c-881c-5e92edfa6421/outputs/tmp/07_2_orthogroups_visualizations/$(echo $SLURM_JOB_NAME)_$(echo $SLURM_JOB_ID)_log.txt
scontrol show job $SLURM_JOB_ID | grep -m 1 "NumCPUs=" >> /lsweb/pupko/microbializer/user_results/1e1bec97-f954-428c-881c-5e92edfa6421/outputs/tmp/07_2_orthogroups_visualizations/$(echo $SLURM_JOB_NAME)_$(echo $SLURM_JOB_ID)_log.txt
