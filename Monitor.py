from SharedConsts import State, PATH2SAVE_MONITOR_DATA, SEPERATOR_FOR_MONITOR_DF, KRAKEN_SUMMARY_RESULTS_FOR_UI_FILE_NAME
import os
from utils import logger, send_email
from datetime import datetime
import glob
import json
import time
from pathlib import Path
import pandas as pd
import ast
import json

class Monitor_Jobs:
    """
    This class manages and orchestrates all parts of monitoring the usage of the webserver.
    Job_Manager_Thread_Safe.py calls this class when the states of the processes changes, and this class saves the process new state into files.
    ...

    Attributes
    ----------


    Methods
    -------
    implemented below
    """

    def __init__(self, upload_root_path):
        """
        The function makes sure the folder to save object exists.
        This although creates the __customs_functions which will generate the data per process per state (only customs). If no need for custom data, leave it empty.
        Before you start changing the custom function! look at the data saved every state update (the general data).
        The way to add functinos is very important: the name of the function should be: {job_prefix}_{state}. For example, if you want to add sepcific data for the State.Finished for the KR process, the name of the function (the key of the dict) will be: KR_Finished. The value of this will be the functions that returns the dict with specific data.
        
        
        **Usually developers should change only the self.__customs_fucntions.
        Parameters
        ----------
        upload_root_path: str
            A path to where the folder of the process are.
            
        Returns
        -------
        Monitor_Jobs: Monitor_Jobs
            instance of Monitor_Jobs
        """
        # titles as will be saved to the file, will be used later to analysis df
        self.STATE_COLUMN_TITLE = 'state'
        self.TIME_COLUMN_TITLE = 'time'
        self.PREFIX_COLUMN_TITLE = 'job_prefix'
        self.PATH_COLUMN_TITLE = 'path_to_folder'
        self.PARAMETERS_COLUMN_TITLE = 'parameters'
        self.COLUMNS_TITLES = [self.STATE_COLUMN_TITLE, self.TIME_COLUMN_TITLE, self.PREFIX_COLUMN_TITLE, self.PATH_COLUMN_TITLE, self.PARAMETERS_COLUMN_TITLE]
        self.__upload_root_path = upload_root_path
        
        if not os.path.exists(PATH2SAVE_MONITOR_DATA):
            os.makedirs(PATH2SAVE_MONITOR_DATA)
            
        try:
            """
            functions declared shoule have the following:
                1. key of the function: {job_prefix}_{state} # check example above
                2. process_id is the only parameter of these functions (you can calc the folder of the process via os.path.join(self.__upload_root_path, process_id))
                3. returns a dictionary with the results for further analysis
            """
            def KR_Init(process_id):
                paraemeters = {}
                parent_folder = os.path.join(self.__upload_root_path, process_id)
                for file in glob.glob(parent_folder + "/*"):
                    file_name = os.path.basename(file)
                    paraemeters[f'{file_name}_size'] = os.stat(file).st_size
                return paraemeters
                
            def KR_Finished(process_id):
                paraemeters = {}
                parent_folder = os.path.join(self.__upload_root_path, process_id)
                summary_path = os.path.join(parent_folder, KRAKEN_SUMMARY_RESULTS_FOR_UI_FILE_NAME)
                if os.path.isfile(summary_path):
                    with open(summary_path) as summary_file:
                        paraemeters = json.load(summary_file)
                return paraemeters
                
            self.__customs_fucntions = {
                'KR_Init': KR_Init,
                'KR_Finished': KR_Finished
            }
        except Exception as e:
            logger.error(e)
            self.__customs_fucntions = {}
        
    def calc_general_data(self, process_id, state, job_prefix):
        """
        This function is for every change of process state.
        This calculates the general stuff important for all of the different states and jobs types.
        If a data is required for only a specific state, please use the self.__customs_fucntions (see above).
        
        **The data retured should be in the same order as the self.COLUMNS_TITLES!!
        
        Parameters
        ----------
        state: State (Enum)
            the new state of the job
        job_prefix: str
            to which of the jobs the state should change
        process_id: str
            the ID of the process
        
        Returns
        -------
        general_data: list
            a list with the general data
        """
        now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        path2process_folder = os.path.join(self.__upload_root_path, process_id)
        return [state.name, now_str, job_prefix, path2process_folder]
        
    def update_monitor_data(self, process_id, state, job_prefix, parameters):
        """
        This function is called when the state of the jobs updates.
        This function writes the data into the correct file at: PATH2SAVE_MONITOR_DATA/{process_id}.csv
        The data written to those files contains two parts:
            1. General - this include: time of update, the new state, job_prefix, path_to_folder
            2. Custom per state - for example, in this webserver we are intreseted in the summary text when the job is finished. Thus this data will be added only when the KR process is finished.
        
        Parameters
        ----------
        state: State (Enum)
            the new state of the job
        job_prefix: str
            to which of the jobs the state should change
        process_id: str
            the ID of the process
        parameters: dict
            parameters to add to custom_data
        
        Returns
        -------
        """
        
        path2monitor_data = f'{os.path.join(PATH2SAVE_MONITOR_DATA, process_id)}.csv'
        #creates the file if not exists and add the tiltes columns
        if not os.path.isfile(path2monitor_data):
            with open(path2monitor_data, 'w') as monitor_file:
                monitor_file.write(SEPERATOR_FOR_MONITOR_DF.join(self.COLUMNS_TITLES) + '\n')
                
        # calculate the general data
        data = self.calc_general_data(process_id, state, job_prefix)
        custom_func_key = f'{job_prefix}_{state.name}'
        
        # adds the custom data
        if self.__customs_fucntions.get(custom_func_key) != None:
            try:
                custom_dict = self.__customs_fucntions.get(custom_func_key)(process_id)
                custom_dict.update(parameters)
                data.append(str(custom_dict))
            except Exception as e:
                logger.error(e)
        else:
            # no custom data is needed
            data.append(str(parameters))
            
        with open(path2monitor_data, 'a') as monitor_file:
            monitor_file.write(SEPERATOR_FOR_MONITOR_DF.join(data) + '\n')
            
    def create_and_send_weekly_summary(self):
        """
        This function is called weekly and send by mail summary to describe the web server usage
        
        Parameters
        ----------
        
        Returns
        -------
        """
        
        # check latest usage of 7 days
        # how many days to check since last modified (should be same as the running time of this job)
        AMOUNT_OF_DAYS_2_CHECK = 7
        EMAIL_TITLE = "GenomeFLTR: Weekly Summary"
        EMAIL_LIST_OF_RECIVERS = ['edodotan@mail.tau.ac.il', 'elya.wygoda@gmail.com']
        now = time.time()
        
        def test_modified(filepath):
            delta = now - os.path.getmtime(filepath)
            delta = delta / (60*60*24) # time in days
            if delta < AMOUNT_OF_DAYS_2_CHECK: 
                return True
            return False
        
        logger.info(f"{PATH2SAVE_MONITOR_DATA}/*.csv")
        weekly_usage_files = [f for f in glob.glob(f"{PATH2SAVE_MONITOR_DATA}/*.csv") if test_modified(f)]
        # no usage -> return - no need to send email
        if len(weekly_usage_files) == 0:
            logger.info(f'weekly usage is 0 - not sending mails')
            return
        
        # will contain the emails list of the users
        # IMPORTANT the '' (no email inserted) will also be included in this email and will get a spefic SHA
        # the emails are encoded by a sha-256
        emails_list = [] 
        # will contian the pairs of process_prefix: list_of_process_ids_that_finished
        # for example: {KR: [process_id1, process_id2], PP: [process_id2, process_id3]}
        finished_process = {} 
        # crashed processes - similar to the finished_process
        crashed_process = {} 
        # init processes - similar to the finished_process
        init_process = {} 
        # init processes without finished state - similar to the finished_process
        init_but_not_finished_process = {}
        
        # paths to crashed processes folders
        crashed_processes_paths = []
        
        # open each csv file and aggregate into a the above structures
        for f in weekly_usage_files:
            process_df = pd.read_csv(f, delimiter=SEPERATOR_FOR_MONITOR_DF)
            process_id = Path(f).stem # file name is process_id
            # extracting only rows with init
            init_rows = process_df[process_df[self.STATE_COLUMN_TITLE] == 'Init']
            # extracting the parameters field of the first Init row
            # process_df.iloc[0][self.COLUMNS_TITLES[-1]] should be a dict
            if len(init_rows.index):
                parameters_dict_str = process_df.iloc[0][self.PARAMETERS_COLUMN_TITLE]
                prameters_list = ast.literal_eval(parameters_dict_str).get('input_parameters')
                if len(prameters_list):
                    # first parameters should be the email (it will be encoded with a sha-256)
                    emails_list.append(prameters_list[0])
            
            processes_prefix = list(process_df[self.PREFIX_COLUMN_TITLE].unique())
            # seperate processes by prefix, will be easier to summarizes and monitor
            for prefix in processes_prefix:
                # df of init per process
                init_rows = process_df[(process_df[self.STATE_COLUMN_TITLE] == 'Init') & (process_df[self.PREFIX_COLUMN_TITLE] == prefix)]
                # df of finished per process
                finished_rows = process_df[(process_df[self.STATE_COLUMN_TITLE] == 'Finished') & (process_df[self.PREFIX_COLUMN_TITLE] == prefix)]
                # df of crashed per process
                crashed_rows = process_df[(process_df[self.STATE_COLUMN_TITLE] == 'Crashed') & (process_df[self.PREFIX_COLUMN_TITLE] == prefix)]
                
                # append to dicts
                for _ in range(len(init_rows.index)):
                    list_of_processes = init_process.get(prefix, [])
                    list_of_processes.append(process_id)
                    init_process[prefix] = list_of_processes
                    
                for _ in range(len(finished_rows.index)):
                    list_of_processes = finished_process.get(prefix, [])
                    list_of_processes.append(process_id)
                    finished_process[prefix] = list_of_processes
                
                for index, row in crashed_rows.iterrows():
                    list_of_processes = crashed_process.get(prefix, [])
                    list_of_processes.append(process_id)
                    crashed_process[prefix] = list_of_processes
                    crashed_processes_paths.append(row[self.PATH_COLUMN_TITLE])
                    
                for _ in range(len(init_rows.index) - len(finished_rows.index)):
                    list_of_processes = init_but_not_finished_process.get(prefix, [])
                    list_of_processes.append(process_id)
                    init_but_not_finished_process[prefix] = list_of_processes
        
        # create email text
        email_body_text = f'Over the past week we had approximately {len(set(emails_list))} unique users. \n\n'
        email_body_text += f'Below are some metrics for the GenomeFLTR webserver. \n'
        email_body_text += f'\t KR prefix -> stand for Kraken Search Job (searching each read against a target database). \n'
        email_body_text += f'\t PP prefix -> stand for Post Process Job (creating the after the user analysis). \n'
        email_body_text += f'\t CDB prefix -> stand for Custom Database (downloading and creating a unique dataset for the user). \n'
        
        email_body_text += f'The following table show the number of processes that initalized: \n'
        for key, value in init_process.items():
            email_body_text += f'\t\t{key}:\t\t{len(value)}\n'
        
        email_body_text += f'\nThe following table show the number of processes that finished: \n'
        for key, value in finished_process.items():
            email_body_text += f'\t\t{key}:\t\t{len(value)}\n'
        
        email_body_text += f'\nThe following table show the number of processes that crashed: \n'
        for key, value in crashed_process.items():
            email_body_text += f'\t\t{key}:\t\t{len(value)}\n'
            
        email_body_text += f'\nThe following table show the number of processes that initalized but without finished state: \n'
        for key, value in init_but_not_finished_process.items():
            email_body_text += f'\t\t{key}:\t\t{len(value)}\n'
        
        email_body_text += f'\nPaths to folders with crashed state: \n'
        for p in crashed_processes_paths:
            email_body_text += f'\t\t{p}\n'
        
        for email_address in EMAIL_LIST_OF_RECIVERS:
            try:
                # the emails are sent from 'TAU BioSequence <bioSequence@tauex.tau.ac.il>'
                send_email('mxout.tau.ac.il', 'TAU BioSequence <bioSequence@tauex.tau.ac.il>',
                           email_address, subject=EMAIL_TITLE,
                           content=email_body_text)
                logger.info(f'sent weekly summary to {email_address}')
            except:
                logger.exception(f'failed to sent email to {email_address}')