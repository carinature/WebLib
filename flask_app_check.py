

# engine = create_engine(SQLALCHEMY_DATABASE_URI, echo=False)
# # engine: Engine  # fixme - remove! only for autocomplete
# connection = engine.connect()

# # todo DO NOT REMOVE
# # DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
# # """:type: sqlalchemy.orm.Session"""
#
from datetime import datetime

from models import *
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from os import environ

# Create engine
# db_uri = environ.get('SQLALCHEMY_DATABASE_URI')
engine = create_engine(SQLALCHEMY_DATABASE_URI, echo=False)

Session = sessionmaker(bind=engine)
session = Session()

# Create All Tables
# Base.metadata.create_all(engine)

user = UserModel(name='todd', description='im testing this', vip=True, id=datetime.now().microsecond,
                 join_date=datetime.now())
session.add(user)
session.commit()
print("user")
print(user)

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