import os
project_home = os.path.dirname(os.path.abspath(__file__))

# add your project directory to the sys.path
import sys
if project_home not in sys.path:
    sys.path = [project_home] + sys.path

from dotenv import load_dotenv
load_dotenv(os.path.join(project_home, '.env'))

from app import create_app
app = create_app()

import logging, logging.config
from time import time, localtime

tt = '-'.join([str(i) for i in localtime()])
logging.config.fileConfig('logging.conf',
                          defaults={
                              'logfilename'     : f'logs/db_migration_{tt}_empty.log',
                              'fulllogfilename' : f'logs/db_migration_full_{tt}_empty.log',
                              'querylogfilename': f"logs/q_{tt}.log",
                              }
                          )
query_logger: logging.Logger = logging.getLogger('queryLogger')
query_logger.info('~' * 80)


# if __name__ == "__main__":
#     app.run(host='0.0.0.0')
