import os
import warnings
import time
import sys
from random import choice

from flask import Flask, flash, request, redirect, url_for, render_template, Response, jsonify, send_file, json
from werkzeug.utils import secure_filename

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import consts
if consts.LOCAL:
    sys.path.append(consts.MICROBIALIZER_PIPELINE_LOCAL_FLASK_PATH)

from utils import logger
from Job_Manager_API import Job_Manager_API
from SharedConsts import UI_CONSTS, CUSTOM_DB_NAME, State, USER_FILE_NAME_TAR, USER_FILE_NAME_ZIP, MAX_NUMBER_PROCESS


def render_template_wrapper(*args, **kwargs):
    names = os.listdir(os.path.join(app.static_folder, 'images/background'))
    img_url = url_for('static', filename=f'images/background/{choice(names)}')
    return render_template(*args, **kwargs, file_name=img_url)


#TODO think about it
warnings.filterwarnings("ignore")

if consts.LOCAL:
    UPLOAD_FOLDERS_ROOT_PATH = os.path.join(consts.WEBSERVER_LOCAL_OUTPUTS, 'user_results')
    os.makedirs(UPLOAD_FOLDERS_ROOT_PATH, exist_ok=True)
else:
    UPLOAD_FOLDERS_ROOT_PATH = '/lsweb/pupko/microbializer/user_results/' # path to folder to save results

# force use of HTTPS protocol, should be removed once the server is developed
class ReverseProxied(object):
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        environ['wsgi.url_scheme'] = 'https'
        # todo remove when server is ready
        environ['wsgi.url_scheme'] = 'http'
        return self.app(environ, start_response)

app = Flask(__name__)
app.wsgi_app = ReverseProxied(app.wsgi_app)

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') # security key
app.config['PASSPHRASE_KILL'] = os.environ.get('PASSPHRASE_KILL') # password to kill server
app.config['PASSPHRASE_CLEAN'] = os.environ.get('PASSPHRASE_CLEAN') # password to clean job dictionary

app.config['UPLOAD_FOLDERS_ROOT_PATH'] = UPLOAD_FOLDERS_ROOT_PATH # path to folder to save results
app.config['MAX_CONTENT_LENGTH'] = 16 * 1000 * 1000 * 1000 # MAX file size to upload
process_id2update = []

def update_html(process_id, state):
    """Gets the process_ids that will need to be updated
    Parameters
    ----------
    process_id : str
        The ID of the process to update
    state : State (Enum from SharedConst)
        The new state of the process to be updated
    Returns
    -------
    None
    """
    #logger.info(f'process_id = {process_id} state = {state}')
    if process_id:
        process_id2update.append(process_id)


@app.route("/process_page_update/<process_id>")
def update_process_page(process_id):
    """The endpoint where the clients can find if need to be reloaded
    Parameters
    ----------
    process_id : str
        The ID of the process to update
    Returns
    -------
    is_reload: str
        A string that will indicate if reload is needed. "" indicates no reload is needed
    """
    if process_id in process_id2update:
        process_id2update.remove(process_id)
        return UI_CONSTS.TEXT_TO_RELOAD_HTML
    return ""


manager = Job_Manager_API(MAX_NUMBER_PROCESS, UPLOAD_FOLDERS_ROOT_PATH, [USER_FILE_NAME_ZIP, USER_FILE_NAME_TAR], update_html)


def allowed_file(filename):
    """Verify if the extenstion of the file name is valid (it doesn't check if the file itself is valid)
    Parameters
    ----------
    filename : str
        The file name
    Returns
    -------
    is_valid: bool
        True if the filename is valid, else False
    """
    logger.debug(f'filename = {filename}')
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in UI_CONSTS.ALLOWED_EXTENSIONS

@app.route('/process_state/<process_id>')
def process_state(process_id):
    """End point to track process state.
    Given a process_id, the function extracts the states of the process and redirect the user.
    Each process might have 2 states as some processes download genomes too (which is done in a different process).
    If the process is still running (or init / queue state) than a GIF is displayed to the user.
    If the process is finished, the function redirects the process to results page.
    Parameters
    ----------
    process_id : str
        The ID of the process
    Returns
    -------
    process_running.html: HTML page
        if the process is still running
    redirection to results:
        if the process is finished
    """
    job_state = manager.get_process_state(process_id)
    if job_state == None:
        return redirect(url_for('error', error_type=UI_CONSTS.UI_Errors.UNKNOWN_PROCESS_ID.name))
    
    if job_state == State.Crashed:
        return redirect(url_for('error_from_job', process_id=process_id))
    if job_state != State.Finished:
        # here we decide what GIF will be displayed to the user
        kwargs = {
            "process_id": process_id,
            "text": UI_CONSTS.states_text_dict[job_state],
            "gif": UI_CONSTS.states_gifs_dict[job_state],
            "message_to_user": UI_CONSTS.PROCESS_INFO_KR,
            "update_text": UI_CONSTS.TEXT_TO_RELOAD_HTML,
            "update_interval_sec": UI_CONSTS.FETCH_UPDATE_INTERVAL_HTML_SEC
        }
        return render_template_wrapper('process_running.html', **kwargs)
    else:
        return redirect(url_for('results', process_id=process_id))

@app.route('/download_page/<process_id>', methods=['GET', 'POST'])
def download_page(process_id):
    """Endpoint to download the results file
    Parameters
    ----------
    process_id : str
        The ID of the process
    Returns
    -------
    export_file.html: HTML page
        When using the GET request type
    results: file
        When using the POST request type
    """
    dict_of_files_to_export = manager.get_files_dict(process_id)
    if dict_of_files_to_export == None:
        return redirect(url_for('error', error_type=UI_CONSTS.UI_Errors.UNKNOWN_PROCESS_ID.name))
    return render_template_wrapper('download_page.html', paths2download=dict_of_files_to_export, process_id=process_id)

@app.route('/download/<process_id>/<file_name>', methods=['GET'])
def download(process_id, file_name):
    logger.info(f'process_id, file_name = {process_id}, {file_name}')
    file_path = manager.get_file(process_id, file_name)
    logger.info(f'file_path = {file_path}')
    if file_path == None:
        return redirect(url_for('error', error_type=UI_CONSTS.UI_Errors.FILE_NOT_FOUND.name))
        
    return send_file(file_path, as_attachment=True, mimetype='application/octet-stream')



@app.route('/get_table/<process_id>', methods=['GET'])
def get_table(process_id):
    offset_og = int(request.args.get('offset'))
    limit_og = int(request.args.get('limit'))
    logger.info(f'limit_og = {limit_og}, offset_og = {offset_og}')
    orthologous_data = manager.get_orthologous_data(process_id, offset_og, limit_og)
    if orthologous_data == None:
        return redirect(url_for('error', error_type=UI_CONSTS.UI_Errors.ORTHOLOGOUS_DATA_IS_NULL.name))
        
    return json.dumps(orthologous_data)

@app.route('/results/<process_id>', methods=['GET', 'POST'])
def results(process_id):
    """Endpoint to analysis the Kraken results. 
    The GET request will return the matrix to display the data to the user.
    Parameters
    ----------
    process_id : str
        The ID of the process
    Returns
    -------
    results.html: HTML page
        the page contains the reads matrix to display to the user
    """
    histogram_data = manager.get_historgram_data(process_id)
    if histogram_data == None:
        return redirect(url_for('error', error_type=UI_CONSTS.UI_Errors.HISTOGRAM_DATA_IS_NULL.name))

    max_num_of_rows = manager.get_max_rows_orthologous(process_id)

    if max_num_of_rows == None:
        return redirect(url_for('error', error_type=UI_CONSTS.UI_Errors.ORTHOLOGOUS_DATA_IS_NULL.name))

    newick_tree_str = manager.get_newick_tree(process_id)
    if newick_tree_str == None:
        return redirect(url_for('error', error_type=UI_CONSTS.UI_Errors.NEWICK_DATA_IS_NULL.name))

    summary_stats = manager.get_summary_stats(process_id)
    summary_stats.pop('run_dir', None)
    return render_template_wrapper('results.html', 
        histogram_data=json.dumps(histogram_data), 
        tree_str=json.dumps(newick_tree_str),
        max_num_of_rows=max_num_of_rows,
        summary_stats=summary_stats, 
        process_id=process_id
    )

@app.route('/error/<error_type>')
def error(error_type):
    """Endpoint to display errors.
    Parameters
    ----------
    error_type : UI_CONSTS.UI_Errors (this is Enum)
        the error to display
    Returns
    -------
    error_page.html': HTML page
        displays the error nicely
    """
    # checking if error_type exists in error enum
    contact_info = UI_CONSTS.ERROR_CONTACT_INFO
    try:
        return render_template_wrapper('error_page.html', error_text=UI_CONSTS.UI_Errors[error_type].value, contact_info=contact_info)
    except:
        return render_template_wrapper('error_page.html', error_text=f'Unknown error, \"{error_type}\" is not a valid error code', contact_info=contact_info)

@app.route('/error_from_job/<process_id>')
def error_from_job(process_id):
    """Endpoint to display errors.
    Parameters
    ----------
    process_id : str
        The ID of the process
    Returns
    -------
    error_page.html': HTML page
        displays the error nicely
    """
    # checking if error_type exists in error enum
    contact_info = UI_CONSTS.ERROR_CONTACT_INFO
    error_text = manager.get_process_error(process_id)
    return render_template_wrapper('error_page.html', error_text=error_text, contact_info=contact_info)

@app.route('/', methods=['GET', 'POST'])
def home():
    """Endpoint to the home page.
    The GET request will return the home.html.
    The POST request will start a kraken process. This will require a file and a few parameters.
    Parameters
    ----------
    Returns
    -------
    home.html: HTML page
        the page contains the submition of a process
    redirection to process_state:
        if the process has been started
    """
    if request.method == 'POST':
        logger.info(f'request.files = {request.files}')
        if 'file' not in request.files:
            return redirect(url_for('error', error_type=UI_CONSTS.UI_Errors.INVALID_FILE_EXTENTION.name))
        files = request.files.getlist("file")
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        logger.info(f'request.form = {request.form}')
        if 2 < len(files):
            return redirect(url_for('error', error_type=UI_CONSTS.UI_Errors.INVALID_FILES_NUMBER.name))
        if files[-1].filename == '': #if nothing was insereted to second input then remove it from the files list
            files = files[:-1]
        logger.info(f'files = {files}')
        for file in files:
            if file.filename == '' or not file or not allowed_file(file.filename):
                return redirect(url_for('error', error_type=UI_CONSTS.UI_Errors.INVALID_FILE_EXTENTION.name))
        email_address, job_name, job_arguemnts = manager.parse_form_inputs(request.form)
        if email_address == None:
            logger.warning(f'email_address not available')
            return redirect(url_for('error', error_type=UI_CONSTS.UI_Errors.INVALID_MAIL.name))
        new_process_id = manager.get_new_process_id()
        folder2save_file = os.path.join(app.config['UPLOAD_FOLDERS_ROOT_PATH'], new_process_id)
        os.mkdir(folder2save_file)
        for file_idx, file in enumerate(files):
            logger.info(f'file number = {file_idx} uploaded = {file}, email_address = {email_address}')
            filename = secure_filename(file.filename)
            if filename.endswith('zip'): #zipped file
                file.save(os.path.join(folder2save_file, USER_FILE_NAME_ZIP))
            elif filename.endswith('tar.gz'):
                file.save(os.path.join(folder2save_file, USER_FILE_NAME_TAR))
            logger.info(f'file number = {file_idx} saved = {file}')
        man_results = manager.add_process(new_process_id, email_address, job_name, job_arguemnts)
        if not man_results:
            logger.warning(f'job_manager_api can\'t add process')
            return redirect(url_for('error', error_type=UI_CONSTS.UI_Errors.CORRUPTED_FILE.name))
        logger.info(f'process added man_results = {man_results}, redirecting url')
        return redirect(url_for('process_state', process_id=new_process_id))
    extensions=",".join(UI_CONSTS.ALLOWED_EXTENSIONS)
    return render_template_wrapper('home.html', 
            extensions=extensions
    )

@app.errorhandler(404)
def page_not_found(e):
    """Endpoint 404 error (page not found).
    If a client request a page that doesn't exists, this endpoint will catch the request
    Parameters
    ----------
    Returns
    -------
    error_page.html': HTML page
        page not found error
    """
    return redirect(url_for('error', error_type=UI_CONSTS.UI_Errors.PAGE_NOT_FOUND.name))


@app.route("/about")
def about():
    """Endpoint to about page.
    Parameters
    ----------
    Returns
    -------
    about.html: HTML page
        about page
    """
    return render_template_wrapper('about.html', help_text_about_list=UI_CONSTS.HELP_TEXT_ABOUT_LIST, contact_info=UI_CONSTS.ERROR_CONTACT_INFO)

@app.route("/overview")
def overview():
    """Endpoint to about page.
    Parameters
    ----------
    Returns
    -------
    about.html: HTML page
        about page
    """
    return render_template_wrapper('overview.html')

@app.route("/example", methods=['GET', 'POST'])
def example():
    """Endpoint to example page.
    Parameters
    ----------
    Returns
    -------
    example.html: HTML page
        example page
    """
    histogram_data, max_num_of_rows, newick_tree_str = manager.get_example_data()
    
    summary_stats = {
        'job_name': 'example'
    }
    
    return render_template_wrapper('results.html', 
        histogram_data=json.dumps(histogram_data), 
        tree_str=json.dumps(newick_tree_str),
        max_num_of_rows=max_num_of_rows,
        summary_stats=summary_stats,
        process_id='example'
    )

@app.route("/debug/killswitch", methods=['GET', 'POST'])
def killswitch():
    """Endpoint to kill switch. 
    Users with passwords can kill (and thus restart the server) or clean the job dictionary.
    GET request returns the debug.html
    POST request with the right passwords can kill / clean the server (passwords are at the start of this page).
    Parameters
    ----------
    Returns
    -------
    debug.html: HTML page
        debug page
    """
    if request.method == 'POST':
        passphrase = request.form.get("passphrase")
        if passphrase == None:
            return
        if passphrase == app.config['PASSPHRASE_KILL']:
            # should check which process group we are in.
            import signal, os
            os.kill(os.getpid(), signal.SIGINT)
        if passphrase == app.config['PASSPHRASE_CLEAN']:
            manager.clean_internal_state()
    return render_template_wrapper('debug.html')
