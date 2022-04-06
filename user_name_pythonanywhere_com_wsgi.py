# This file contains the WSGI configuration required to serve up your
# web application at http://<your-username>.pythonanywhere.com/
# It works by setting the variable 'application' to a WSGI handler of some
# description.
#
# The below has been auto-generated for your Flask project

import sys

# add your project directory to the sys.path
# project_home = '/home/wildhrushka/mysite'
# if project_home not in sys.path:
#     sys.path = [project_home] + sys.path

# import flask app but need to call it "application" for WSGI to work
# ~~~~~~~~  You should put this part in   ~~~~~~~~~
# from flask_app import app as application  # noqa


# ~~~~~~~~  You should add this part  ~~~~~~~~~
# Has to be here and not config.py
import os

project_home =  os.getcwd()+'/mysite'
if project_home not in sys.path:
    sys.path = [project_home] + sys.path


from dotenv import load_dotenv
load_dotenv(os.path.join(project_home, '.env'))

from app import create_app

application = create_app()
# import app as application  # noqa


logs_dir = 'logs'
os.mkdir(os.path.join(project_home, logs_dir))

import logging, logging.config
from time import time, localtime

print('*' * 80)
tt = '-'.join([str(i) for i in localtime()])
logging.config.fileConfig(os.path.join(project_home,'./logging.conf'),
                          defaults={
                              'logfilename'     : f'{project_home}/{logs_dir}/db_migration_empty.log',
                              'fulllogfilename' : f'{project_home}/{logs_dir}/db_migration_full_empty.log',
                              'querylogfilename': f'{project_home}/{logs_dir}/q_tt.log',
                              }
                          )
query_logger: logging.Logger = logging.getLogger('queryLogger')
query_logger.info('~' * 80)

