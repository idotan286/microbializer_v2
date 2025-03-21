import os
import shutil
import uuid
import json
import pandas as pd
from InputValidator import InputValidator
from Job_Manager_Thread_Safe_Microbializer import Job_Manager_Thread_Safe_Microbializer
from utils import send_email, logger, LOGGER_LEVEL_JOB_MANAGE_API
import consts

from flask_interface_consts import IDENTITY_CUTOFF, \
    CORE_MINIMAL_PERCENTAGE, BOOTSTRAP, OUTGROUP, FILTER_OUT_PLASMIDS, \
    DATA_2_VIEW_IN_HISTOGRAM, OG_TABLE, SPECIES_TREE_NEWICK, PATHS_TO_DOWNLOAD, JOB_PARAMETERS_FILE_NAME, \
    COVERAGE_CUTOFF, ADD_ORPHAN_GENES_TO_OGS, INPUT_FASTA_TYPE, ALL_OUTPUTS_ZIPPED, ERROR_FILE_PATH, PROGRESSBAR_FILE_NAME, \
    ADDITIONAL_OWNER_EMAILS, SEND_EMAIL_WHEN_JOB_FINISHED_FROM_PIPELINE, WEBSERVER_PROJECT_ROOT_DIR
from SharedConsts import EMAIL_CONSTS, State, OWNER_EMAIL
logger.setLevel(LOGGER_LEVEL_JOB_MANAGE_API)


class Job_Manager_API:
    """
    A class used to connect the __init__ to the backend.

    ...

    Attributes
    ----------
    

    Methods
    -------
    implemented below
    """
    def __init__(self, max_number_of_process: int, upload_root_path: str, input_file_names: list, func2update_html):
        """Creates the Job_Manager_API instances

        Parameters
        ----------
        max_number_of_process : int
            Max number of process that can run simultaneously
        upload_root_path: str
            A path to the saved files. Each process in there creates it's own folder
        input_file_names: lst
            The names of the input files (the file which the user uploaded). This is a list as 1 or 2 files might be uploaded
        func2update_html: function
            What function should be called once the state is updated

        Returns
        -------
        manager: Job_Manager_API
            instance of Job_Manager_API
        """
        self.__input_file_name = input_file_names[0]
        self.__input_file_name2 = input_file_names[1]
        self.__upload_root_path = upload_root_path
        self.__j_manager = Job_Manager_Thread_Safe_Microbializer(max_number_of_process, upload_root_path, input_file_names, self.__process_state_changed)
        self.input_validator = InputValidator() # creates the input_validator
        self.__func2update_html = func2update_html
        if consts.LOCAL:
            self.gallery_path = consts.MICROBIALIZER_LOCAL_GALLERY_PATH
        else:
            self.gallery_path = os.path.join(WEBSERVER_PROJECT_ROOT_DIR, 'gallery')

        self.__relative_files2download_and_paths = {}
        for title, paths in PATHS_TO_DOWNLOAD.items():
            for file_name, (path, description) in paths.items():
                self.__relative_files2download_and_paths[file_name] = path

    def __build_and_send_mail(self, process_id, subject, content, email_addresses):
        """Sends mail to user

        Parameters
        ----------
        process_id : str
            The ID of the process
        subject: str
            email subject
        content: str
            email content
        email_address: str
            where to send the email

        Returns
        -------
        """
        if not email_addresses:
            logger.info('mail is empty, not sending')
            return
        
        if type(email_addresses) == str:
            email_addresses = [email_addresses]
        
        for email_address in email_addresses:
            try:
                # the emails are sent from 'TAU BioSequence <bioSequence@tauex.tau.ac.il>'
                send_email('mxout.tau.ac.il', 'TAU BioSequence <bioSequence@tauex.tau.ac.il>',
                        email_address, subject=subject,
                        content= content)
                logger.info(f'sent email to {email_address} with subject {subject}')
            except:
                logger.exception(f'failed to send email to {email_address}')
            
    def __process_state_changed(self, process_id, state, email_address, job_name, job_prefix):
        """When the process state is changed, this function is called (this funciton is called for the Kraken and post process types).

        Parameters
        ----------
        process_id : str
            The ID of the process
        state: State (Enum)
            the new state of the process
        email_address: str
            where to send the email
        job_name: str
            The job name (optional) inserted by the user
        job_prefix: str
            To distinguish between processes types

        Returns
        -------
        """
        if not SEND_EMAIL_WHEN_JOB_FINISHED_FROM_PIPELINE:
            email_addresses = [OWNER_EMAIL]
            email_addresses.extend(ADDITIONAL_OWNER_EMAILS)
            if email_address is not None:
                email_addresses.append(email_address)
            else:
                logger.warning(f'process_id = {process_id} email_address is None, state = {state}, job_name = {job_name}')          
            
            # sends mail once the job finished or crashes
            if state == State.Finished:
                self.__build_and_send_mail(process_id, EMAIL_CONSTS.create_title(state, job_name), EMAIL_CONSTS.CONTENT_PROCESS_FINISHED.format(process_id=process_id), email_addresses)
            elif state == State.Crashed:
                self.__build_and_send_mail(process_id, EMAIL_CONSTS.create_title(state, job_name), EMAIL_CONSTS.CONTENT_PROCESS_CRASHED.format(process_id=process_id), email_addresses)

        self.__func2update_html(process_id, state)

    def __delete_folder(self, process_id):
        """Deletes folder.
        Used when the file isn't valid

        Parameters
        ----------
        process_id : str
            The ID of the process

        Returns
        -------
        """
        logger.info(f'process_id = {process_id}')
        folder2remove = os.path.join(self.__upload_root_path, process_id)
        shutil.rmtree(folder2remove)

    def __find_file_path(self, file2check):
        """finds if the file exists (zip or unzipped)

        Parameters
        ----------
        file2check : str
            The path of the file to check

        Returns
        -------
        path_of_file: str
           Returns the path of the file if exists, else False
        """
        if os.path.isfile(file2check):
            return file2check
        file2check += '.gz' #maybe it is zipped
        if os.path.isfile(file2check):
            return file2check
        return False
        
    def __validate_input_file(self, process_id):
        """validate input file by testing the file itself.
        Will ungzip file if needed

        Parameters
        ----------
        process_id : str
            The ID of the process

        Returns
        -------
        is_valid: bool
            True if the file is valid, else False.
        """
        parent_folder = os.path.join(self.__upload_root_path, process_id)
        if not os.path.isdir(parent_folder):
            logger.warning(f'process_id = {process_id} doen\'t have a dir')
            return False
        file2check = os.path.join(parent_folder, self.__input_file_name)
        file2check = self.__find_file_path(file2check)
        file2check2 = os.path.join(parent_folder, self.__input_file_name2) # for paired reads
        file2check2 = self.__find_file_path(file2check2)
        # test file in the input_validator
        if not file2check2: # not paired reads
            if file2check and self.input_validator.validate_input_file(file2check):
                return True
        else:
            if file2check and self.input_validator.validate_input_file(file2check) and self.input_validator.validate_input_file(file2check2):
                return True
        self.__delete_folder(process_id)
        if not file2check2:
            logger.warning(f'validation failed {file2check}, deleting folder')
        else:
            logger.warning(f'validation failed file1: {file2check} file2: {file2check2}, deleting folder')
        return False
        
    def __validate_email_address(self, email_address):
        """validate email address.

        Parameters
        ----------
        email_address : str
            email address

        Returns
        -------
        is_valid: bool
            True if the email_address is valid, else False.
        """
        #TOOD this is a simple validation, might be better to change it
        if len(email_address) > 100:
            return False
        if '@' in email_address and '.' in email_address:
            return True
        if '' == email_address:
            return True
        return False

    def get_new_process_id(self):
        """generates a new process id

        Parameters
        ----------

        Returns
        -------
        process_id: str
            a random process_id
        """
        return str(uuid.uuid4())

    def add_process(self, process_id: str, email_address: str, job_name: str, job_arguemnts: dict):
        """Creates a new kraken process based on the user parameters

        Parameters
        ----------
        process_id: str
            The ID of the process
        email_address: str
            email adress
        job_name: str
            The job name (optional) inserted by the user
        job_arguemnts: dict
            Job arguemnts to run with
            
        Returns
        -------
        is_process_added: bool
            True if the process has been added, else False
        """
        logger.info(f'process_id = {process_id} email_address = {email_address} job_name = {job_name}')
        is_valid_email = self.__validate_email_address(email_address)
        # validating file and email
        if is_valid_email:
            # adding the process
            self.__j_manager.add_process(process_id, email_address, job_name, job_arguemnts)
            
            email_addresses = [OWNER_EMAIL]
            email_addresses.extend(ADDITIONAL_OWNER_EMAILS)
            if email_address != None:
                email_addresses.append(email_address)

            self.__build_and_send_mail(process_id, EMAIL_CONSTS.SUBMITTED_TITLE.format(job_name=job_name), EMAIL_CONSTS.SUBMITTED_CONTENT.format(process_id=process_id), email_addresses)
            return True
        logger.warning(f'process_id = {process_id}, can\'t add process: is_valid_email = {is_valid_email}')
        return False
        
    def get_files_dict(self, process_id: str):
        """After the post process has finished (and the user already filtred his reads), this will return the path to the result file

        Parameters
        ----------
        process_id: str
            The ID of the process
        
        Returns
        -------
        dict_of_files_to_export: dict
            Dict of (title, path) for files to download
        """
        parent_folder = self.get_process_folder(process_id)
        if os.path.exists(parent_folder):
            return PATHS_TO_DOWNLOAD

        return None
    
    def get_file(self, process_id: str, file_name: str):
        """Find specific result file and download

        Parameters
        ----------
        process_id: str
            The ID of the process
        file_name: str
            The name of the file
        Returns
        -------
        path2file: str
            path to required file, else None
        """
        if not file_name in self.__relative_files2download_and_paths:
            return None
        parent_folder = self.get_process_folder(process_id)
            
        path2file = os.path.join(parent_folder, self.__relative_files2download_and_paths[file_name])
        if not os.path.exists(path2file):
            return None
        return path2file

    def get_process_state(self, process_id):
        """Given process_id returns the kraken process state

        Parameters
        ----------
        process_id: str
            The ID of the process
        
        Returns
        -------
        """
        return self.__j_manager.get_process_state(process_id)

    def get_process_error(self, process_id):
        """Given process_id returns the error txt
        
        Parameters
        ----------
        process_id: str
            The ID of the process
        
        Returns
        -------
        error text
        """
        parent_folder = os.path.join(self.__upload_root_path, process_id)
        if os.path.isdir(parent_folder):
            error_file = os.path.join(parent_folder, ERROR_FILE_PATH)
            if os.path.isfile(error_file):
                return open(error_file, 'r').read()
            else:
                return "error file does not exists"
        logger.warning(f'process_id = {process_id} don\'t have a folder')
        return "no process ID folder"
        
    def parse_form_inputs(self, form_dict: dict):
        """Parse the form of the user.

        Parameters
        ----------
        form_dict: dict
            The from from the request of the user
        
        Returns
        -------
        email_address: str
            user email adress
        job_name: str
            the name of the job, inserted by user (optional), if None is inserted then a empty string will be returned
        """
        email_address = form_dict.get('email', None)
        job_name = form_dict.get('job_name', "")
        logger.info(f"email_address = {email_address}, job_name = {job_name}, form_dict = {form_dict}")
        job_arguemnts = {
            IDENTITY_CUTOFF: form_dict.get('minIdentity', ""),
            CORE_MINIMAL_PERCENTAGE: form_dict.get('orthologsPercent', ""),
            OUTGROUP: form_dict.get('outgroup', ""),
            BOOTSTRAP: form_dict.get('isBootstrap', ""),
            COVERAGE_CUTOFF: form_dict.get('coverageCutoff', ""),
            FILTER_OUT_PLASMIDS: form_dict.get('isFilter', ""),
            ADD_ORPHAN_GENES_TO_OGS: form_dict.get('isAddOrphanGenes', ""),
            INPUT_FASTA_TYPE: form_dict.get('inputFastaType', ""),
        }
        logger.info(f"job_arguemnts = {job_arguemnts}")
        return email_address, job_name, job_arguemnts

    def get_summary_stats(self, process_id: str):
        """Return the input paramaters for the run
        
        Parameters
        ----------
        process_id: str
            The ID of the process
        
        Returns
        -------
        data: dict
            dict of dict were key is the tilte of the data and the data is a dict:
                    were the key is the genomes and the value are scalars
        """
        parent_folder = self.get_process_folder(process_id)
        
        if not os.path.isdir(parent_folder):
            return {}
        input_file = os.path.join(parent_folder, JOB_PARAMETERS_FILE_NAME)
        
        if os.path.exists(input_file):
            with open(input_file) as json_file:
                dict2return = json.load(json_file)
                dict2return.pop('run_dir', None)
                dict2return = {consts.ARG_NAME_IN_PIPELINE_TO_DISPLAY[key]: value for key, value in dict2return.items()}
                return dict2return
        return {}
    
    def get_historgram_data(self, process_id: str):
        """Return the data to display histogram

        Parameters
        ----------
        process_id: str
            The ID of the process
        
        Returns
        -------
        data: dict
            dict of dict were key is the tilte of the data and the data is a dict:
                    were the key is the genomes and the value are scalars
        """
        parent_folder = self.get_process_folder(process_id)
        if not os.path.isdir(parent_folder):
            return None
        
        data = {}
        for key, value in DATA_2_VIEW_IN_HISTOGRAM.items():
            data_path = os.path.join(parent_folder, value)
            if os.path.isfile(data_path):
                with open(data_path, 'r') as f:
                    data[key] = json.load(f)
        
        if len(data.items()):
            return data
        return None
    
    def get_orthologous_data(self, process_id: str, offset: int, limit: int):
        """Return the data to display histogram

        Parameters
        ----------
        process_id: str
            The ID of the process
        offset: int
            To read chunks of the OG table
        limit: int
            To read chunks of the OG table
        
        Returns
        -------
        data: dict
            dict of dict were key is the tilte of the data and the data is a dict:
                    were the key is the genomes and the value are scalars
        """
        parent_folder = self.get_process_folder(process_id)
        if not os.path.isdir(parent_folder):
            return None
        
        data = {}
        data_path = os.path.join(parent_folder, OG_TABLE)
        if os.path.isfile(data_path):
            df = pd.read_csv(data_path, index_col=0, skiprows=offset, nrows=limit)
            # convert not nan values to 1 and nan values to 0
            df = df.notnull().astype("int")
            data = df.to_dict('split')
        
        if len(data.items()):
            return data
        return None

    def get_max_rows_orthologous(self, process_id: str):
        """Return the data to display histogram

        Parameters
        ----------
        process_id: str
            The ID of the process

        Returns
        -------
        max_rows: ind
            max_number of rows for offset
        """
        parent_folder = self.get_process_folder(process_id)
        if not os.path.isdir(parent_folder):
            return None

        data_path = os.path.join(parent_folder, OG_TABLE)
        if os.path.isfile(data_path):
            df = pd.read_csv(data_path)
            return len(df.index)

        return None

    def get_newick_tree(self, process_id: str):
        """Return the newick tree

        Parameters
        ----------
        process_id: str
            The ID of the process
        
        Returns
        -------
        tree: str
            the phylogenetic tree
        """
        parent_folder = self.get_process_folder(process_id)
        if not os.path.isdir(parent_folder):
            return None
        
        data = {}
        data_path = os.path.join(parent_folder, SPECIES_TREE_NEWICK)
        if os.path.isfile(data_path):
            with open(data_path, 'r') as f:
                return f.read().replace('\n', '')
        
        return None

    def get_progress_bar(self, process_id: str):
        """Return progress bar list

        Parameters
        ----------
        process_id: str
            The ID of the process
        
        Returns
        -------
        progress_status: str
            which stages and done
        """
        parent_folder = os.path.join(self.__upload_root_path, process_id)
        if not os.path.isdir(parent_folder):
            return None
        
        data_path = os.path.join(parent_folder, PROGRESSBAR_FILE_NAME)
        if os.path.isfile(data_path):
            import csv
            progressbar = []
            with open(data_path, newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    progressbar.append(row)
            return progressbar
        
        return []
        
    def get_all_outputs_path(self, process_id: str):
        """get path to all outputs

        Parameters
        ----------
        process_id: str
            The ID of the process
        
        Returns
        -------
        tree: path
            path to zip file
        """
        parent_folder = os.path.join(self.__upload_root_path, process_id)
        if not os.path.isdir(parent_folder):
            return None
        
        data_path = os.path.join(parent_folder, ALL_OUTPUTS_ZIPPED)
        if os.path.isfile(data_path):
            return data_path
        
        return None
    
    def clean_internal_state(self):
        """clean job state dictionary

        Parameters
        ----------

        Returns
        -------
        """
        self.__j_manager.clean_internal_state()

    def get_websites(self):
        """return list of other websites

        Parameters
        ----------

        Returns
        -------
        """
        logger.info(f'in get_websites')
        try:
            with open("/lsweb/pupko/websites.json") as f:
                data = json.load(f)
            logger.info(data)
            return data
        except Exception as e:
            logger.warning(e)
        return []

    def get_process_folder(self, process_id: str):
        if process_id in ['chlamydia_run_a', 'chlamydia_run_b']:
            process_folder = os.path.join(self.gallery_path, process_id)
        else:
            process_folder = os.path.join(self.__upload_root_path, process_id)
        
        return process_folder
