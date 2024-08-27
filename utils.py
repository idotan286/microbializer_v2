from enum import Enum
from datetime import datetime
import logging
import os

import consts

if consts.LOCAL:
    LOGS_BASE_PATH = os.path.join(consts.LOCAL_BASE_PATH, 'logs')
    os.makedirs(LOGS_BASE_PATH, exist_ok=True)
else:
    LOGS_BASE_PATH = '/var/www/vhosts/dev.microbializer.tau.ac.il/logs/'


LOGGER_LEVEL_JOB_MANAGE_THREAD_SAFE = logging.DEBUG
LOGGER_LEVEL_JOB_MANAGE_API = logging.DEBUG
logger = logging.getLogger('main')
formatter = logging.Formatter('%(asctime)s[%(levelname)s][%(filename)s][%(funcName)s]: %(message)s')

handler = logging.FileHandler(os.path.join(LOGS_BASE_PATH, 'flask-error.log'))  # Adjust the path
handler.setFormatter(formatter)
handler.setLevel(logging.ERROR)
logger.addHandler(handler)

handler_debug = logging.FileHandler(os.path.join(LOGS_BASE_PATH, 'flask-debug.log'))  # Adjust the path
handler_debug.setFormatter(formatter)
handler_debug.setLevel(logging.DEBUG)
logger.addHandler(handler_debug)

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
