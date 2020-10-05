import os

# ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
# ROOT_DIR = os.path.dirname(os.path.realpath(__file__))  # todo - find absolute path?
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))  # todo - find absolute path?
RAW_DATA_DIR = os.path.join(ROOT_DIR, 'app/raw_data')
# UTILS_DIR = os.path.join(ROOT_DIR, 'utilities')


class Config(object):
    EXPLAIN_TEMPLATE_LOADING = True
    # General Flask config variables
    SECRET_KEY = os.environ.get('SECRET_KEY')
    static_folder = 'dlf/static'
    # STATIC_FOLDER = 'static'
    TEMPLATES_FOLDER = 'templates'
    # SESSION_COOKIE_NAME = os.environ.get('SESSION_COOKIE_NAME')

    # Database
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_POOL_RECYCLE = 299
    SQLALCHEMY_ECHO = False  # if True log all database activity to Python's stderr
    CHUNK_SIZE_DB = 1000  # used in DB migration for chunking huge amounts of data

    # # AWS Secrets
    # AWS_SECRET_KEY = os.environ.get('AWS_SECRET_KEY')
    # AWS_KEY_ID = os.environ.get('AWS_KEY_ID')


class DevConfig(Config):
    FLASK_ENV = 'development' #fixme should work with the config.py instead
    DEBUG = True #fixme should work with the config.py instead
    # TESTING = True #fixme should work with the config.py instead

    # Database
    SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://{username}:{password}@{hostname}/{db_name}".format(
        username="root",
        password="123",
        hostname="localhost",
        db_name="tryout",
    )
    # SQLALCHEMY_ECHO = True
    # SQLALCHEMY_ENGINE_OPTIONS =  # options to pass to SQLAlchemy-engine which holds your app's DB connection.

    # MISC
    POSTS_PER_PAGE = 3  # used for pagination of the DB-query results
    SUBJECTS_POSTS_PER_PAGE = 10
    CHUNK_SIZE_DB = 10000  # used in DB migration for chunking huge amounts of data


class ProdConfig(Config):
    FLASK_ENV = 'production'
    DEBUG = False
    TESTING = False

    # Database
    SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://{username}:{password}@{hostname}/{db_name}".format(
        username="karinature",
        password="dsmiUw2sn",
        hostname="karinature.mysql.pythonanywhere-services.com",
        db_name="karinature$tryout",
    )
    SQLALCHEMY_ECHO = False

    # MISC
    POSTS_PER_PAGE = 10
    SUBJECTS_POSTS_PER_PAGE = 100



# def _include_sqlalchemy(obj):
#     for module in sqlalchemy, sqlalchemy.orm:
#         for key in module.__all__:
#             if not hasattr(obj, key):
#                 setattr(obj, key, getattr(module, key))

# class Test(object):
#     def __init__(self):
#         _include_sqlalchemy(self, self.__class__)


# db:SQLAlchemy = Test() # <-- add a type hint to let pycharm know what db is.
