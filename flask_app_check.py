# engine = create_engine(SQLALCHEMY_DATABASE_URI, echo=False)
# # engine: Engine  # fixme - remove! only for autocomplete
# connection = engine.connect()

# # todo DO NOT REMOVE
# # DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
# # """:type: sqlalchemy.orm.Session"""
#
from datetime import datetime

# for the type_dict
import sqlalchemy
import decimal

from models import *
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from os import environ

# Create engine
# db_uri = environ.get('SQLALCHEMY_DATABASE_URI')
engine = create_engine(SQLALCHEMY_DATABASE_URI, echo=False)

# Create All Tables
Base.metadata.create_all(engine)

# Create the session
Session = sessionmaker(bind=engine)
session = Session()

# user = UserModel(name='todd', description='im testing this', vip=True, id=datetime.now().microsecond,
#                  join_date=datetime.now())
# session.add(user)
# session.commit()
# print("user")
# print(user)

# for i in range(13):
#     entry = Entry(text_value_col=f'{i}'+f'{i}'+f'{i}'+f'{i}')
#     session.add(entry)
#     print("entry")
#     print(entry)
#     session.commit()


records = session.query(Entry).all()
# create your own object instead to receive only the columns you want/need:
for record in records:
    recordObject = {'id': record.int_value_col, 'text': record.text_value_col}
    # , 'team_name': record.team.name, 'team_city': record.team.city}
    print(recordObject)

records = session.query(Entry).filter(Entry.int_value_col == 3).all()
print(records)

records = session.query(Entry).filter_by(int_value_col=3).all()
print(records)

records = session.query(Entry).filter(Entry.int_value_col.like('1%')).all()
print(records)

# todo
#   In addition to filter(), there are a few basic methods we should absolutely be familiar with.
#   Each of these corresponds to SQL keywords you're probably familiar with:
#   limit([INTEGER]): Limits the number of rows to a maximum of the number provided.
#   order_by([COLUMN]): Sorts results by the provided column.
#   offset([INTEGER]): Begins the query at row n.
#   "Group by" aggregation
#   records = session.query(func.count(Customer.first_name)).group_by(Customer.first_name).all()


#  ~~~~~~~~~~~~ READ THIS!!!
# The engine is what allows you to use connection pooling. By default, it will persist connections across requests. The basic usage (without fancy things like scoped_session or sessionmaker) is like this:
# engine = create_engine(...)
#
# @app.route(...)
# def foo():
#     session = Session(bind=engine)
#     try:
#         session.query(...)
#         session.commit()
#     finally:
#         session.close()
#     return ""
# On top of this, you can add scoped_session and sessionmaker:
# engine = create_engine(...)
# Session = sessionmaker(bind=engine)
# session = scoped_session(Session, scopefunc=...)
#
# @app.route(...)
# def foo():
#     try:
#         session.query(...)
#         session.commit()
#     finally:
#         session.close()
#     return ""
# flask-sqlalchemy makes your life easier by providing all of this:
# db = SQLAlchemy(app)
#
# @app.route(...)
# def foo():
#     db.session.query(...)
#     db.session.commit()
#     return ""

from sqlalchemy.types import Integer, String, Text, DateTime, Float, Boolean, PickleType

import pandas as pd
from flask_app import db
from flask_sqlalchemy import SQLAlchemy

dtype_dic_csv2py = {'book_bibliographic_info': int, 'file': str, 'titleref': str, 'gcode': str}
dtype_dic_py2sql = {int: Integer, str: Text}

csv_file_path = 'raw_data/bookreferences2.csv'
print('-----------------')
with open(csv_file_path, 'r') as csv_file:
    # dataframe = pd.read_csv(file, usecols=['file', 'titleref'])[['titleref', 'file']]  # , 'gcode'])
    # dataframe = pd.read_csv(csv_file, header=0, names=['kaka', 'pipi'])[['pipi', 'kaka']]
    # dataframe = pd.read_csv(csv_file, header=0, dtype=dtype_dic_csv2py) #dtype=BookRef)
    dataframe = pd.read_csv(csv_file, header=0)
    print(dataframe)
# DO NOT DELETE THE NEXT 2 (3) LINES
db.engine.execute(BookRef.__table__.insert(), dataframe.to_dict('records'))
# todo the next one is anpther good WORKING option - find out which of the 2 (or 3) is faster
# dataframe.to_sql(name=BookRef.__tablename__, con=engine, if_exists='replace', index=False,
#                  index_label='book_bibliographic_info', dtype=dtype_dic_py2sql) #this one workd! dont delte
# fixme the next one should be the best option but it doesn't work. WHY??
# session.bulk_insert_mappings(BookRef, dataframe.to_dict(orient='records'))  # should work but doesnt. why?! dont delete
# new_mapper = sqlalchemy.orm.mapper(BookRef, local_table=BookRef.__table__, non_primary=True)  # should work but doesnt
# session.bulk_insert_mappings(new_mapper, dataframe.to_dict('records'))  # should work but doesnt. why?! dont delete

print('~~~~~~~~~~~~')
print(dataframe.to_dict('records'))
print('===============')
print(dataframe.to_dict('index'))
print('******************')
print(dataframe.to_dict())


session.close()