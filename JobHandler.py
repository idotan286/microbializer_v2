import pathlib
import os
from utils import logger
import json
import sys

import consts
if consts.LOCAL:
    sys.path.append(consts.MICROBIALIZER_PIPELINE_LOCAL_FLASK_PATH)
else:
    sys.path.append(consts.MICROBIALIZER_PIPELINE_MGMT_FLASK_PATH)

from flask_interface_consts import MICROBIALIZER_PROCESSOR_JOB_PREFIX, MICROBIALIZER_JOB_TEMPLATE, \
    JOB_PARAMETERS_FILE_NAME, RUN_DIR
from slurm_example import submit_job



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
            if len(input_path) == 0:
                raise ValueError('Input file path parameter was an empty list')
            input_path_parent = pathlib.Path(input_path[0]).parent
        else:
            raise ValueError('Input file path parameter was not a list of a string')
        job_unique_id = str(input_path_parent.stem)
        job_name = f'{MICROBIALIZER_PROCESSOR_JOB_PREFIX}_{job_unique_id}'
        job_arguemnts[RUN_DIR] = str(input_path_parent)
        json_parameters_file_path = os.path.join(input_path_parent, JOB_PARAMETERS_FILE_NAME)
        with open(json_parameters_file_path, 'w') as fp:
            json.dump(job_arguemnts, fp)
        command_to_run = MICROBIALIZER_JOB_TEMPLATE.format(
            args_json_path=json_parameters_file_path,
        )

        # run the job
        run_parameters = {
            "job_name": job_name,
            "logs_path": input_path_parent,
            "script_commands": command_to_run
        }
        run_parameters['logger'] = logger
        logger.debug(f'{run_parameters}')
        return submit_job(**run_parameters)
