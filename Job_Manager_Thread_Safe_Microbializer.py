import os
import SharedConsts as sc
import MicrobializerConsts as mc
from Handlers.JobHandler import Handler
from Job_Manager_Thread_Safe import Job_Manager_Thread_Safe
from utils import logger


class Job_Manager_Thread_Safe_Microbializer:
    """
    A specific implementation of Job_Manager_Thread_Safe.py for the NGS Read Cleaning webserver.
    Where all logic pertaining to a specific webservers backend comes to play.
    Job_Manager_Thread_Safe.py does not know what it runs, so what runs is defined here.
    ...

    Attributes
    ----------
    

    Methods
    -------
    implemented below
    """
    
    def __init__(self, max_number_of_process: int, upload_root_path: str, input_file_names: list, func2update):
        """
        Creates the Job_Manager_Thread_Safe_GenomeFltr instances.
        Here we create the backend and we insert the content of our webserver. 
        This is done by creating dictionaries where different pbs job prefixes are the keys.
        Three different dictionaries are needed for the backend:
            1. function2call_processes_changes_state:
                What function to call when the job state is changed
            2. function2append_process:
                What function to call when a new job is added (this functions have to return the PBS id - the job id as runs on the queue)
            3. paths2verify_process_ends:
                A functions to build the path of the results for verifications that the processes have finished (and not crashed).

        Here the actual lifecycle stages of a process are defined.
        Each lifecycle stage (pbs job) need to have:
            1. a unique pbs job prefix - this is used to identify the job in the PBS pool once running so it needs
            to be long enough to avoid random noise but not too long as to exceed PBS limitations
            2. a function running the process - actually submits the job to pbs
            3. an add function - calls the base add function from Job_Manager_Thread_Safe.py with the relevant params

        In this example there are 3 lifecycle stages, and hence 3 different jobs:
        1. download - which downloads genomic data from NCBI data base (in the case of a custom database creating)
        2. kraken - which runs the actual kraken algorithm, processes the results and creates the required UI files
        3. postprocess - which receives the users input from the UI and prepares the requested result files.
        
        Parameters
        ----------
        max_number_of_process : int
            Max number of process that can run simultaneously
        upload_root_path: str
            A path to the saved files. Each process in there creates it's own folder
        input_file_names: lst
            The names of the input files (the file which the user uploaded). This is a list as 1 or 2 files might be uploaded
        func2update: function
            What function should be called once the state is changed in the process

        Returns
        -------
        manager: Job_Manager_Thread_Safe_Microbializer
            instance of Job_Manager_Thread_Safe_GenomeFltr
        """
        self.__handler = Handler()
        self.__input_file_names = input_file_names
        self.__func2update = func2update

        function2call_processes_changes_state = {
            mc.MICROBIALIZER_PROCESSOR_JOB_PREFIX: self.__func2update
        }
        function2append_process = {
            mc.MICROBIALIZER_PROCESSOR_JOB_PREFIX: self.__add_process
        }
        paths2verify_process_ends = {
            #when the job crashes/ finished this list of file paths will be checked to set the change to finished if one of the files exists of crashed if file doesn't.
            #for a string of: '' it won't set the state
            mc.MICROBIALIZER_PROCESSOR_JOB_PREFIX: [lambda process_id: os.path.join(os.path.join(upload_root_path, process_id), mc.MICROBIALIZER_PROCESSOR_RESULTS_FILE_NAME)]
        }
        self.__job_manager = Job_Manager_Thread_Safe(max_number_of_process, upload_root_path, function2call_processes_changes_state, function2append_process, paths2verify_process_ends)
    
    def __get_files_in_folder(self, process_folder_path):
        """
        Returns a list with files from the user
        ** Specific to this webserver
        Parameters
        ----------
        process_folder_path : str
            A path to save the donwloaded genomes
        
        Returns
        -------
        files_list: str
            A list with files from the user based on the self.__input_file_names
        """
        files_list = [] #list of files to fltr
        for file_name in self.__input_file_names:
            file2fltr = os.path.join(process_folder_path, file_name)
            # check if file exists, if so adds to list
            if os.path.isfile(file2fltr) or os.path.isfile(str(file2fltr) + '.gz'):
                files_list.append(file2fltr)
        return files_list
    
    def __add_process(self, process_folder_path: str, email_address, job_name):
        """
        Creates a kraken process
        ** Specific to this webserver

        Parameters
        ----------
        process_folder_path : str
            A path to save the donwloaded genomes
        email_address: str
            email address
        job_name: str
            The job name (optional) inserted by the user. If none is inserted then job_name = ""

        Returns
        -------
        pbs_id: str
            The number of the job as it runs in the queue
        """
        logger.info(f'process_folder_path = {process_folder_path}')
        files2fltr = self.__get_files_in_folder(process_folder_path)
        pbs_id, _ = self.__handler.submit_micro_job(files2fltr)
        return pbs_id
        
    def __get_state(self, process_id, job_prefix):
        """
        Gets the job state from the job_manager
        
        Parameters
        ----------
        process_id : str
            The ID of the process
        job_prefix: str
            the job prefix (this is the job type)

        Returns
        -------
        state: State (Enum)
            The state of the process
        """
        state = self.__job_manager.get_job_state(process_id, job_prefix)
        if state:
            return state
        logger.warning(f'process_id = {process_id}, job_prefix = {job_prefix} not in __job_manager')
        return None
        
    def get_process_state(self, process_id):
        """
        Get kraken job state
        ** Specific to this webserver

        Parameters
        ----------
        process_id : str
            The ID of the process

        Returns
        -------
        state: State (Enum)
            The state of the process
        """
        return self.__get_state(process_id, mc.MICROBIALIZER_PROCESSOR_JOB_PREFIX)
    
    def get_job_name(self, process_id):
        """
        Get job name

        Parameters
        ----------
        process_id : str
            The ID of the process

        Returns
        -------
        job_name: str 
            The job name (optional) inserted by the user. If none is inserted then job_name = "". 
            Returns None if process_id does not exists.
        """
        return self.__job_manager.get_job_name(process_id)
    
    def add_process(self, process_id: str, email_address, job_name: str):
        """
        adds a kraken process
        ** Specific to this webserver

        Parameters
        ----------
        process_id : str
            The ID of the process
        email_address: str
            email address
        job_name: str
            The job name (optional) inserted by the user. If none is inserted then job_name = ""

        Returns
        -------
        """
        logger.info(f'process_id = {process_id}, email_address = {email_address}, job_name = {job_name}')
        self.__job_manager.add_process(process_id, mc.MICROBIALIZER_PROCESSOR_JOB_PREFIX, email_address, job_name)
    
    
    def add_example_postprocess(self, email_address: str, job_name:str, process_id: str, k_threshold, species_list):
        """
        adds a post process
        ** Specific to this webserver

        Parameters
        ----------
        process_id : str
            The ID of the process
        k_threshold: str
            a threshold to filter from
        species_list: list
            list of species to filter

        Returns
        -------
        """
        #logger.info(f'process_id = {process_id}')
        #self.__job_manager.add_process(process_id, sc.POSTPROCESS_JOB_PREFIX, email_address, job_name, k_threshold, species_list)
    
    def get_job_state(self, process_id: str, job_prefix: str):
        #TODO might be a duplication
        logger.info(f'process_id = {process_id} job_prefix = {job_prefix}')
        return self.__job_manager.get_job_state(process_id, job_prefix)

    def clean_internal_state(self):
        """
        this function clean the internal job dictionary (inside the backend)
        
        Parameters
        ----------
        
        Returns
        -------
        """
        self.__job_manager.clean_internal_state()