import re
import subprocess
import os
import pandas as pd
from get_jobs import get_jobs, ACCOUNT_NAME

from SharedConsts import QstatDataColumns, SRVER_USERNAME, JOB_CHANGE_COLS, JOB_ELAPSED_TIME, \
    JOB_RUNNING_TIME_LIMIT_IN_HOURS, JOB_NUMBER_COL, LONG_RUNNING_JOBS_NAME, QUEUE_JOBS_NAME, NEW_RUNNING_JOBS_NAME, \
    FINISHED_JOBS_NAME, JOB_STATUS_COL, WEIRD_BEHAVIOR_JOB_TO_CHECK, ERROR_JOBS_NAME, PATH2SAVE_PREVIOUS_DF, \
    JOB_NAME_COL
from utils import logger


class PbsListener:

    def __init__(self, job_prefix_to_function_mapping):
        """
        :param job_prefix_to_function_mapping: MUST be a dictionary of this structure:
        keys are Job prefixes (that must appear in the PBS_JOB_PREFIXES Const) and the values are dictionaries.
        the inner dictionaries MUST be of this structure:
        keys are Job States (From the Consts) and the values are functions to call for the appropriate state and job
        type.
        Example (not with all job states and kinds):
        {'KR': {'NewRunning': some_function}, 'PP':{'NewRunning': some_other_function}}
        """
        self.job_prefix_to_function_mapping = job_prefix_to_function_mapping
        if os.path.isfile(PATH2SAVE_PREVIOUS_DF):
            self.previous_state = pd.read_csv(PATH2SAVE_PREVIOUS_DF)
        else:
            self.previous_state = None
        self.job_prefixes = tuple(job_prefix_to_function_mapping.keys())

    def run(self):
        """
        main running loop for the listener
        :return: None
        """
        #get running jobs data
        logger.info(f'in run')
        current_job_state = self.get_server_job_stats()
        logger.info(f'current_job_state = {current_job_state}')
        # check state diff, act accordingly
        try:
            self.handle_job_state(current_job_state)
        except Exception as e:
            logger.exception(f'Error with handle_job_state, with error {e}')
        # update job status
        self.previous_state = current_job_state[JOB_CHANGE_COLS]
        self.previous_state.to_csv(PATH2SAVE_PREVIOUS_DF, index=False)

    def handle_job_state(self, new_job_state):
        """
        this function gets the newly sampled PBS job status and alerts the job manager accordingly through the
        "functions_to_call" dictionary that is provided by the job manager upon creation.
        :param new_job_state: newly sampled job state
        """
        # todo: talk with everyone of the case of jobs stuck in Q
        # todo: talk with Edo about jobs that run/error in a time between intervals (I think we have to do a wrapper
        #  layer that "knows" which jobs it runs.
        # make sure we have running jobs
        # EDO - remarked as comment, causing problems
        # if len(new_job_state.index) == 0:
        #    return
        # check for long running jobs:
        # self.handle_long_running_jobs(new_job_state)

        # find jobs who have changed status and act accordingly
        changed_jobs = self.get_changed_job_state(new_job_state)
        logger.info(f'changed_jobs = {changed_jobs}')
        # make sure there is something to report
        if len(changed_jobs.index) == 0:
            return
        for job_prefix in self.job_prefixes:
            relevant_df = changed_jobs[changed_jobs[JOB_NAME_COL].str.startswith(job_prefix)]
            logger.info(f'relevant_df = {relevant_df}')
            for index, job_row in relevant_df.iterrows():
                job_number = job_row[JOB_NUMBER_COL]
                job_status = job_row[JOB_STATUS_COL]
                try:
                    if job_status == 'RUNNING':
                        logger.debug(f'job_row = {job_row} running')
                        self.job_prefix_to_function_mapping[job_prefix][NEW_RUNNING_JOBS_NAME](job_number)
                    elif job_status == 'COMPLETED':
                        logger.debug(f'job_row = {job_row} finished')
                        self.job_prefix_to_function_mapping[job_prefix][FINISHED_JOBS_NAME](job_number)
                    elif job_status == 'FAILED':
                        logger.warning(f'job_row = {job_row} error')
                        self.job_prefix_to_function_mapping[job_prefix][ERROR_JOBS_NAME](job_number)
                    else:
                        logger.warning(f'job_row = {job_row} weird behavior')
                        logger.warning(f'job_status = {job_status}')
                        self.job_prefix_to_function_mapping[job_prefix][WEIRD_BEHAVIOR_JOB_TO_CHECK](job_number)
                except Exception as e:
                    logger.exception(f'There was an error with job {job_number}, with error {e}')

    def get_server_job_stats(self):
        """
        gets the users current job statistics (running and queued) and parses them
        :return: a data frame of all current jobs
        """
        logger.info(f'ACCOUNT_NAME = {ACCOUNT_NAME}')
        results_df = pd.DataFrame(get_jobs(account=ACCOUNT_NAME, logger=logger))
        logger.info(f'1 results_df = {results_df}')
        logger.info(f'1 results_df = {results_df.columns}')
        results_df = results_df[[JOB_NUMBER_COL, JOB_NAME_COL, 'state']]
        logger.info(f'2 results_df = {results_df}')
        results_df = results_df[results_df[JOB_NAME_COL].str.startswith(self.job_prefixes)]
        logger.info(f'3 results_df = {results_df}')
        results_df[['state', 'reason']] = results_df['state'].apply(pd.Series)
        logger.info(f'4 results_df = {results_df}')
        results_df['current_state'] = results_df['state'].apply(lambda x: ','.join(map(str, x)))
        logger.info(f'5 results_df = {results_df}')
        return results_df

    def get_changed_job_state(self, current_job_state):
        """
        takes the new job state and returns a pandas DF with only the relevant job data,
        it does so by removing all jobs that appear with the same status in both of the states (previous, current)
        it does NOT handle long running jobs.
        :param current_job_state: the newly sampled job state
        :return: a pandas df with jobs that have a different status in new sampled data than the previous
        (including new jobs)
        """
        if self.previous_state is None:
            temp_df = current_job_state[JOB_CHANGE_COLS]
            temp_df['origin'] = 'N'
            return temp_df
        temp_df = self.previous_state
        temp_df['origin'] = 'P'
        current_job_state = current_job_state[JOB_CHANGE_COLS]
        current_job_state['origin'] = 'N'
        temp_df = temp_df.append(current_job_state)
        after_drop_duplicates = temp_df.drop_duplicates(JOB_CHANGE_COLS, keep=False)
        return after_drop_duplicates

    def handle_long_running_jobs(self, current_job_state):
        """
        handles jobs that have exceeded the timeout
        :param current_job_state: newly sampled job state
        """
        # todo: discuss if we want to kill these jobs from here or not.
        temp_new_job_state = current_job_state
        temp_new_job_state[JOB_ELAPSED_TIME] = temp_new_job_state[JOB_ELAPSED_TIME].astype(str).replace('--', '')
        temp_new_job_state[JOB_ELAPSED_TIME] = temp_new_job_state[JOB_ELAPSED_TIME].str.replace('', '0').str.split(
            ':')  # just care about the hours
        temp_new_job_state[JOB_ELAPSED_TIME] = temp_new_job_state[JOB_ELAPSED_TIME].apply(lambda x: int(x[0]))
        long_running_jobs = temp_new_job_state[temp_new_job_state[JOB_ELAPSED_TIME] >= JOB_RUNNING_TIME_LIMIT_IN_HOURS][
            JOB_NUMBER_COL].values
        for job_prefix in self.job_prefixes:
            for long_running_job in long_running_jobs:
                self.job_prefix_to_function_mapping[job_prefix][LONG_RUNNING_JOBS_NAME](long_running_job)
