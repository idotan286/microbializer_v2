from enum import Enum
from datetime import datetime
import logging
import os


LOGGER_LEVEL_JOB_MANAGE_THREAD_SAFE = logging.DEBUG
LOGGER_LEVEL_JOB_MANAGE_API = logging.DEBUG
DEV_SERVER_DIR = r'/data/www/flask/microbializer_v2/'
SERVER_DIR = r'/data/www/flask/microbializer_v2/'

def init_dir_path():
    current_directory = os.getcwd()
    if 'dev' in os.path.basename(current_directory):
        path2change = DEV_SERVER_DIR
    else:
        path2change = SERVER_DIR
    if os.path.isdir(path2change):
        os.chdir(path2change)

init_dir_path()
logging_file_name = os.path.join('logs/', datetime.now().strftime('%Y_%m_%d_%H_%M.log'))
logging.basicConfig(filename = logging_file_name, level=logging.WARNING, format='%(asctime)s[%(levelname)s][%(filename)s][%(funcName)s]: %(message)s')
logger = logging.getLogger('main')


def send_email(smtp_server, sender, receiver, subject='', content=''):
    from email.mime.text import MIMEText
    from smtplib import SMTP
    msg = MIMEText(content)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = receiver
    s = SMTP(smtp_server)
    s.send_message(msg)
    s.quit()
