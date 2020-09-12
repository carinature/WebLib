# engine = create_engine(SQLALCHEMY_DATABASE_URI, echo=False)
# # engine: Engine  # fixme - remove! only for autocomplete
# connection = engine.connect()

# # todo DO NOT REMOVE
# # DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
# # """:type: sqlalchemy.orm.Session"""
#

# for the type_dict

from utilities.models import *
from properties import SQLALCHEMY_DATABASE_URI
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

# Create engine
engine = create_engine(SQLALCHEMY_DATABASE_URI, echo=False)

# Create All Tables
Base.metadata.create_all(engine)

# Create the session
Session = sessionmaker(bind=engine)
session = Session()
# session = scoped_session(Session())

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


# records = session.query(Entry).all()
# # create your own object instead to receive only the columns you want/need:
# for record in records:
#     recordObject = {'id': record.int_value_col, 'text': record.text_value_col}
#     # , 'team_name': record.team.name, 'team_city': record.team.city}
#     print(recordObject)
#
# records = session.query(Entry).filter(Entry.int_value_col == 3).all()
# print(records)
#
# records = session.query(Entry).filter_by(int_value_col=3).all()
# print(records)
#
# records = session.query(Entry).filter(Entry.int_value_col.like('1%')).all()
# print(records)

# todo
#   In addition to filter(), there are a few basic methods we should absolutely be familiar with.
#   Each of these corresponds to SQL keywords you're probably familiar with:
#   limit([INTEGER]): Limits the number of rows to a maximum of the number provided.
#   order_by([COLUMN]): Sorts results by the provided column.
#   offset([INTEGER]): Begins the query at row n.
#   "Group by" aggregation
#   records = session.query(func.count(Customer.first_name)).group_by(Customer.first_name).all()

