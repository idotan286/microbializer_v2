import os
import warnings
import sys
from random import choice

from flask import Flask, request, redirect, url_for, render_template, send_file, json, send_from_directory
from werkzeug.utils import secure_filename

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import consts
if consts.LOCAL:
    sys.path.append(consts.MICROBIALIZER_PIPELINE_LOCAL_FLASK_PATH)

from utils import logger
from Job_Manager_API import Job_Manager_API
from SharedConsts import UI_CONSTS, State, USER_FILE_NAME_TAR, USER_FILE_NAME_ZIP, WEBSERVER_ADDRESS, ALLOWED_EXTENSIONS
from flask_interface_consts import WEBSERVER_PROJECT_ROOT_DIR

if consts.LOCAL:
    UPLOAD_FOLDERS_ROOT_PATH = consts.MICROBIALIZER_LOCAL_USER_RESULTS
else:
    UPLOAD_FOLDERS_ROOT_PATH = f'{WEBSERVER_PROJECT_ROOT_DIR}/user_results/'  # path to folder to save results


def render_template_wrapper(*args, **kwargs):
    names = os.listdir(os.path.join(app.static_folder, 'images/background/webp'))
    img_url = url_for('static', filename=f'images/background/webp/{choice(names)}')
    return render_template(*args, **kwargs, file_name=img_url)


#TODO think about it
warnings.filterwarnings("ignore")


# force use of HTTPS protocol, should be removed once the server is developed
class ReverseProxied(object):
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        if consts.LOCAL:
            environ['wsgi.url_scheme'] = 'http'
        else:
            environ['wsgi.url_scheme'] = 'https'
        return self.app(environ, start_response)


app = Flask(__name__)
app.wsgi_app = ReverseProxied(app.wsgi_app)

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')  # security key
app.config['PASSPHRASE_KILL'] = os.environ.get('PASSPHRASE_KILL')  # password to kill server
app.config['PASSPHRASE_CLEAN'] = os.environ.get('PASSPHRASE_CLEAN')  # password to clean job dictionary

app.config['UPLOAD_FOLDERS_ROOT_PATH'] = UPLOAD_FOLDERS_ROOT_PATH  # path to folder to save results
app.config['MAX_CONTENT_LENGTH'] = 16 * 1000 * 1000 * 1000  # MAX file size to upload


manager = Job_Manager_API(UPLOAD_FOLDERS_ROOT_PATH, [USER_FILE_NAME_ZIP, USER_FILE_NAME_TAR])


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
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


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
    if job_state is None:
        return redirect(url_for('error', error_type=UI_CONSTS.UI_Errors.UNKNOWN_PROCESS_ID.name))
    
    if job_state == State.Crashed:
        return redirect(url_for('error_from_job', process_id=process_id))
    if job_state == State.Finished:
        return redirect(url_for('results', process_id=process_id))
    else:
        # here we decide what GIF will be displayed to the user
        progressbar = manager.get_progress_bar(process_id)                                                  
        kwargs = {
            "process_id": process_id,
            "text": UI_CONSTS.states_text_dict[job_state],
            "gif": UI_CONSTS.states_gifs_dict[job_state],
            "message_to_user": UI_CONSTS.PROCESS_INFO_KR,
            "update_text": UI_CONSTS.TEXT_TO_RELOAD_HTML,
            "update_interval_sec": UI_CONSTS.FETCH_UPDATE_INTERVAL_HTML_SEC,
            "progressbar": progressbar                         
        }
        return render_template_wrapper('process_running.html', **kwargs)


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
    job_state = manager.get_process_state(process_id)
    if job_state is None:
        return redirect(url_for('error', error_type=UI_CONSTS.UI_Errors.UNKNOWN_PROCESS_ID.name))

    if job_state == State.Crashed:
        return redirect(url_for('error_from_job', process_id=process_id))

    dict_of_files_to_export = manager.get_files_dict(process_id)
    if dict_of_files_to_export is None:
        return redirect(url_for('error', error_type=UI_CONSTS.UI_Errors.UNKNOWN_PROCESS_ID.name))
    summary_stats = manager.get_summary_stats(process_id)
    job_description = '' 
    if consts.ARG_DISPLAY_JOB_NAME in summary_stats and summary_stats[consts.ARG_DISPLAY_JOB_NAME]:
        job_description = f'(Job name: {summary_stats[consts.ARG_DISPLAY_JOB_NAME]})'
    return render_template_wrapper('download_page.html', paths2download=dict_of_files_to_export, process_id=process_id,
                                   job_description=job_description)


@app.route('/download/<process_id>/<file_name>', methods=['GET'])
def download(process_id, file_name):
    logger.info(f'process_id, file_name = {process_id}, {file_name}')
    file_path = manager.get_file(process_id, file_name)
    logger.info(f'file_path = {file_path}')
    if file_path is None:
        return redirect(url_for('error', error_type=UI_CONSTS.UI_Errors.FILE_NOT_FOUND.name))
        
    return send_file(file_path, as_attachment=True, mimetype='application/octet-stream')


@app.route('/get_table/<process_id>', methods=['GET'])
def get_table(process_id):
    offset_og = int(request.args.get('offset'))
    limit_og = int(request.args.get('limit'))
    logger.info(f'limit_og = {limit_og}, offset_og = {offset_og}')
    orthologous_data = manager.get_orthologous_data(process_id, offset_og, limit_og)
    if orthologous_data is None:
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
    job_state = manager.get_process_state(process_id)
    if job_state is None:
        return redirect(url_for('error', error_type=UI_CONSTS.UI_Errors.UNKNOWN_PROCESS_ID.name))

    if job_state == State.Crashed:
        return redirect(url_for('error_from_job', process_id=process_id))

    histogram_data = manager.get_historgram_data(process_id)
    if histogram_data is None:
        return redirect(url_for('error', error_type=UI_CONSTS.UI_Errors.HISTOGRAM_DATA_IS_NULL.name))

    max_num_of_rows = manager.get_max_rows_orthologous(process_id)

    if max_num_of_rows is None:
        return redirect(url_for('error', error_type=UI_CONSTS.UI_Errors.ORTHOLOGOUS_DATA_IS_NULL.name))

    newick_tree_str = manager.get_newick_tree(process_id)
    if newick_tree_str is None:
        return redirect(url_for('error', error_type=UI_CONSTS.UI_Errors.NEWICK_DATA_IS_NULL.name))

    # If the newick_file contains an error message, it will not start with a '(', and in that case we don't want to
    # display it.
    if newick_tree_str[0] != '(':
        newick_tree_str = ''

    summary_stats = manager.get_summary_stats(process_id)
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
        return render_template_wrapper('error_page.html', error_text=UI_CONSTS.UI_Errors[error_type].value,
                                       contact_info=contact_info)
    except:
        return render_template_wrapper('error_page.html',
                                       error_text=f'Unknown error, \"{error_type}\" is not a valid error code',
                                       contact_info=contact_info)


@app.route('/error_from_job/<process_id>')
def error_from_job(process_id):
    """Endpoint to display errors.
    Parameters
    ----------
    process_id : str
        The ID of the process
    Returns
    -------
    error_page.html: HTML page
        displays the error nicely
    """
    job_state = manager.get_process_state(process_id)
    if job_state is None:
        return redirect(url_for('error', error_type=UI_CONSTS.UI_Errors.UNKNOWN_PROCESS_ID.name))

    if job_state == State.Finished:
        return redirect(url_for('results', process_id=process_id))

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
        if files[-1].filename == '':  # if nothing was inserted to second input then remove it from the files list
            files = files[:-1]
        logger.info(f'files = {files}')
        for file in files:
            if file.filename == '' or not file or not allowed_file(file.filename):
                return redirect(url_for('error', error_type=UI_CONSTS.UI_Errors.INVALID_FILE_EXTENTION.name))
        email_address, job_name, job_arguemnts = manager.parse_form_inputs(request.form)
        is_valid_email = manager.validate_email_address(email_address)
        if not is_valid_email:
            logger.warning(f'email_address is invalid')
            return redirect(url_for('error', error_type=UI_CONSTS.UI_Errors.INVALID_MAIL.name))
        new_process_id = manager.get_new_process_id()
        folder2save_file = os.path.join(app.config['UPLOAD_FOLDERS_ROOT_PATH'], new_process_id)
        os.mkdir(folder2save_file)
        for file_idx, file in enumerate(files):
            logger.info(f'file number = {file_idx} uploaded = {file}, email_address = {email_address}')
            filename = secure_filename(file.filename)
            if filename.endswith('zip'):  # zipped file
                file.save(os.path.join(folder2save_file, USER_FILE_NAME_ZIP))
            elif filename.endswith('tar.gz'):
                file.save(os.path.join(folder2save_file, USER_FILE_NAME_TAR))
            logger.info(f'file number = {file_idx} saved = {file}')
        add_process_succeeded = manager.add_process(new_process_id, email_address, job_name, job_arguemnts)
        if not add_process_succeeded:
            return redirect(url_for('error', error_type=UI_CONSTS.UI_Errors.CORRUPTED_FILE.name))
        logger.info(f'process added add_process_succeeded = {add_process_succeeded}, redirecting url')
        return redirect(url_for('process_state', process_id=new_process_id))
    extensions=",".join(ALLOWED_EXTENSIONS)
    return render_template_wrapper('home.html', 
            extensions=extensions,
            args_display_job_name=consts.ARG_DISPLAY_JOB_NAME,
            args_display_email=consts.ARG_DISPLAY_EMAIL,
            args_display_inputs_fasta_type=consts.ARG_DISPLAY_INPUTS_FASTA_TYPE,
            args_display_filter_out_plasmids=consts.ARG_DISPLAY_FILTER_OUT_PLASMIDS,
            args_display_identity_cutoff=consts.ARG_DISPLAY_IDENTITY_CUTOFF,
            args_display_coverage_cutoff=consts.ARG_DISPLAY_COVERAGE_CUTOFF,
            args_display_core_minimal_percentage=consts.ARG_DISPLAY_CORE_MINIMAL_PERCENTAGE,
            args_display_outgroup=consts.ARG_DISPLAY_OUTGROUP,
            args_display_bootstrap=consts.ARG_DISPLAY_BOOTSTRAP,
            args_display_add_orphan_genes_to_ogs=consts.ARG_DISPLAY_ADD_ORPHAN_GENES_TO_OGS)


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
    return render_template_wrapper('about.html', contact_info=UI_CONSTS.ERROR_CONTACT_INFO)


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


@app.route("/gallery")
def gallery():
    """Endpoint to about page.
    Parameters
    ----------
    Returns
    -------
    about.html: HTML page
        about page
    """
    return render_template_wrapper('gallery.html')


@app.route("/tools")
def tools():
    """Endpoint to tools page.
    Parameters
    ----------
    Returns
    -------
    tools.html: HTML page
        tools page
    """
    websites = manager.get_websites()
    return render_template_wrapper('tools.html', websites=websites)


@app.route('/uploads/<path:filename>')
def download_image(filename):
    return send_from_directory("/lsweb/pupko/websites_figures/", filename, as_attachment=True)


@app.route("/faq")
def faq():
    """Endpoint to about page.
    Parameters
    ----------
    Returns
    -------
    about.html: HTML page
        about page
    """
    return render_template_wrapper('faq.html')


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
    return render_template_wrapper('debug.html')
