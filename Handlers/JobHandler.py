import pathlib
import subprocess
from subprocess import PIPE
import os
from utils import logger
from SharedConsts import PATH_TO_OUTPUT_PROCESSOR_SCRIPT, RESULTS_SUMMARY_FILE_NAME, INPUT_CLASSIFIED_FILE_NAME, \
    INPUT_UNCLASSIFIED_FILE_NAME, TEMP_CLASSIFIED_IDS, TEMP_UNCLASSIFIED_IDS, INTERVAL_BETWEEN_LISTENER_SAMPLES, \
    INPUT_CLASSIFIED_FILE_NAME_PAIRED, INPUT_UNCLASSIFIED_FILE_NAME_PAIRED, USER_FILE_NAME
from flask_interface_consts import MICROBIALIZER_PROCESSOR_JOB_QUEUE_NAME, NUBMER_OF_CPUS_MICROBIALIZER_PROCESSOR_JOB, MICROBIALIZER_PROCESSOR_JOB_PREFIX, MICROBIALIZER_PROCESSOR_RESULTS_FILE_NAME, MICROBIALIZER_JOB_TEMPLATE
import glob
import datetime


class Handler:
    """
    a class holding all code related to running the job itself
    """

    @staticmethod
    def submit_micro_job(input_path):
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
        temp_script_text = MICROBIALIZER_JOB_TEMPLATE.format(queue_name=MICROBIALIZER_PROCESSOR_JOB_QUEUE_NAME,
                                          cpu_number=NUBMER_OF_CPUS_MICROBIALIZER_PROCESSOR_JOB, job_name=job_name,
                                          error_files_path=input_path_parent,
                                          output_files_path=input_path_parent,
                                          path_to_folder=input_path_parent,
                                          path_to_input_validator_script="",
                                          file_name_1=USER_FILE_NAME[0],
                                          file_name_2=USER_FILE_NAME[1],
                                          results_file_path=results_file_path,
                                          sleep_interval=INTERVAL_BETWEEN_LISTENER_SAMPLES,
                                          mem_req=10)

        # run the job
        with open(temp_script_path, 'w+') as fp:
            fp.write(temp_script_text)
        logger.info(f'submitting job, temp_script_path = {temp_script_path}:')
        logger.debug(f'{temp_script_text}')
        terminal_cmd = f'/opt/pbs/bin/qsub {str(temp_script_path)}'
        job_run_output = subprocess.run(terminal_cmd, stdout=PIPE, stderr=PIPE, shell=True)
        # os.remove(temp_script_path)
        
        return job_run_output.stdout.decode('utf-8').split('.')[0], results_file_path

