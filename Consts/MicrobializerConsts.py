from pathlib import Path

# Microbializer processor Job variables
MICROBIALIZER_PROCESSOR_JOB_QUEUE_NAME = 'lifesciweb'
NUBMER_OF_CPUS_MICROBIALIZER_PROCESSOR_JOB = '1'
MICROBIALIZER_PROCESSOR_JOB_PREFIX = 'MC'
MICROBIALIZER_PROCESSOR_RESULTS_FILE_NAME = 'results.txt'


MICROBIALIZER_JOB_TEMPLATE = '''
#!/bin/bash

#PBS -S /bin/bash
#PBS -r y
#PBS -q {queue_name}
#PBS -l ncpus={cpu_number}
#PBS -l mem={mem_req}gb
#PBS -v PBS_O_SHELL=bash,PBS_ENVIRONMENT=PBS_BATCH
#PBS -N {job_name}
#PBS -e {error_files_path}
#PBS -o {output_files_path}

source /powerapps/share/miniconda3-4.7.12/etc/profile.d/conda.sh
conda activate NGScleaner
PYTHONPATH=$(pwd)
pwd
sleep {sleep_interval}

#python {path_to_input_validator_script} --folder2verify {path_to_folder} --file_name1_to_check {file_name_1} --file_name2_to_check {file_name_2}

cat "OKAY" > {results_file_path}

'''

