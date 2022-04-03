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

print('*' * 80)
tt = '-'.join([str(i) for i in localtime()])
# print(os.path.join(project_home, 'logging.conf'))
logging.config.fileConfig(
        os.path.join(project_home, 'logging.conf'),
        defaults={
            'logfilename'     : f'{project_home}/logs/db_migration_empty.log',
            'fulllogfilename' : f'{project_home}/logs/db_migration_full_empty.log',
            'querylogfilename': f'{project_home}/logs/q_empty.log',
            }
        )
query_logger: logging.Logger = logging.getLogger('queryLogger')
query_logger.info('~' * 80)


# if __name__ == "__main__":
#     app.run(host='0.0.0.0')
