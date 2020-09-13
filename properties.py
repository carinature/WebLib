import os

# global ROOT_DIR
# global RAW_DATA_DIR
ROOT_DIR = os.path.dirname(os.path.realpath(__file__))  # todo - find absolute path
RAW_DATA_DIR = os.path.join(ROOT_DIR, 'raw_data')
TEMPLATES_DIR = os.path.join(ROOT_DIR, 'templates')
STATIC_DIR = os.path.join(ROOT_DIR, 'templates')
UTILS_DIR = os.path.join(ROOT_DIR, 'utilities')

CHUNK_SIZE_DB = 1000  # used in DB migration for chunking huge amounts of data

# SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://{username}:{password}@{hostname}/{db_name}".format(
#     username="karinature",
#     password="dsmiUw2sn",
#     hostname="karinature.mysql.pythonanywhere-services.com",
#     db_name="karinature$tryout",
# )
SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://{username}:{password}@{hostname}/{db_name}".format(
    username="root",
    password="123",
    hostname="localhost",
    db_name="tryout",
)
