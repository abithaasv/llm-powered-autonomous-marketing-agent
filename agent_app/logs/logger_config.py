import logging
import os

def setup_logging():

    log_directory = os.path.dirname(os.path.abspath(__file__))
    log_file_path = os.path.join(log_directory, 'app.log')

    logging.basicConfig(filename=log_file_path, filemode='a', format='[%(asctime)s] %(levelname)s in %(module)s: %(message)s', level=logging.INFO)
