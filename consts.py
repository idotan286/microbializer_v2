import os

LOCAL = True

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WEBSERVER_LOCAL_OUTPUTS = os.path.join(BASE_DIR, 'local_run')

MICROBIALIZER_PIPELINE_LOCAL_PATH = r'C:\repos\microbializer'
MICROBIALIZER_PIPELINE_LOCAL_FLASK_PATH = os.path.join(MICROBIALIZER_PIPELINE_LOCAL_PATH, 'pipeline', 'flask')

LOCAL_INTERVAL_BETWEEN_LISTENER_SAMPLES = 60
