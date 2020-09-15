import os

# global ROOT_DIR
# global RAW_DATA_DIR
import sqlalchemy
from flask_sqlalchemy import Model, SQLAlchemy

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

from flask import Flask
from flask_sqlalchemy import SQLAlchemy


class Config(object):
    SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI
    SQLALCHEMY_POOL_RECYCLE = 299
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_POOL_RECYCLE = 280

    DEBUG = True  # todo fixme remove this in production!!!
    # ...
    POSTS_PER_PAGE = 10


app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)  # the type is SQLAlchemy.orm ?
# db:SQLAlchemy = SQLAlchemy(app)  # the type is SQLAlchemy.orm ?


def _include_sqlalchemy(obj):
    for module in sqlalchemy, sqlalchemy.orm:
        for key in module.__all__:
            if not hasattr(obj, key):
                setattr(obj, key, getattr(module, key))

# class Test(object):
#     def __init__(self):
#         _include_sqlalchemy(self, self.__class__)


# db:SQLAlchemy = Test() # <-- add a type hint to let pycharm know what db is.
