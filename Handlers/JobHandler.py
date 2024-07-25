import pathlib
import subprocess
from subprocess import PIPE
import os
from utils import logger
from SharedConsts import PATH_TO_OUTPUT_PROCESSOR_SCRIPT, RESULTS_SUMMARY_FILE_NAME, INPUT_CLASSIFIED_FILE_NAME, \
    INPUT_UNCLASSIFIED_FILE_NAME, TEMP_CLASSIFIED_IDS, TEMP_UNCLASSIFIED_IDS, INTERVAL_BETWEEN_LISTENER_SAMPLES, \
    INPUT_CLASSIFIED_FILE_NAME_PAIRED, INPUT_UNCLASSIFIED_FILE_NAME_PAIRED, USER_FILE_NAME_ZIP, USER_FILE_NAME_TAR
from flask_interface_consts import MICROBIALIZER_PROCESSOR_JOB_QUEUE_NAME, NUBMER_OF_CPUS_MICROBIALIZER_PROCESSOR_JOB, \
    MICROBIALIZER_PROCESSOR_JOB_PREFIX, MICROBIALIZER_PROCESSOR_RESULTS_FILE_NAME, MICROBIALIZER_JOB_TEMPLATE, \
    ARGS_JSON_PATH_KEY, JOB_PARAMETERS_FILE_NAME, CONTIGS_DIR
import glob
from slurm_example import submit_job
import datetime
import json


class Handler:
    """
    a class holding all code related to running the job itself
    """

    @staticmethod
    def submit_micro_job(input_path, job_arguemnts):
        """
        this function actually preforms the kraken2 search
        :param input_path: path to input query file
        :param run_parameters: a dictionary with the kraken run parameters
        :return: created job id, path to results
        """
        # create the job
        if isinstance(input_path, str):
            input_path_parent = pathlib.Path(input_path).parent
        elif isinstance(input_path, list):
            input_path_parent = pathlib.Path(input_path[0]).parent
        else:
            raise ValueError('Input file path parameter was not a list of a string')
        job_unique_id = str(input_path_parent.stem)
        temp_script_path = input_path_parent / f'temp_micro_search_running_file_{job_unique_id}.sh'
        results_file_path = input_path_parent / MICROBIALIZER_PROCESSOR_RESULTS_FILE_NAME
        job_name = f'{MICROBIALIZER_PROCESSOR_JOB_PREFIX}_{job_unique_id}'
        job_arguemnts[CONTIGS_DIR] = str(input_path_parent)
        json_parameters_file_path = os.path.join(input_path_parent, JOB_PARAMETERS_FILE_NAME)
        with open(json_parameters_file_path, 'w') as fp:
            json.dump(job_arguemnts, fp)
        command_to_run = MICROBIALIZER_JOB_TEMPLATE.format(
            sleep_interval=INTERVAL_BETWEEN_LISTENER_SAMPLES,
            args_json_path_key=ARGS_JSON_PATH_KEY,
            args_json_path=json_parameters_file_path,
            results_file_path=results_file_path
        )

        # run the job
        run_parameters = {
            "queue": MICROBIALIZER_PROCESSOR_JOB_QUEUE_NAME, 
            "num_cpus": NUBMER_OF_CPUS_MICROBIALIZER_PROCESSOR_JOB, 
            "job_name": job_name,
            "logs_path": input_path_parent,
            "script_commands": command_to_run,
            "memory": "10"
        }
        run_parameters['logger'] = logger
        logger.debug(f'{run_parameters}')
        return submit_job(**run_parameters)

